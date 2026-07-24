import datetime
import logging
import uuid

from application.common.events import EventHandler
from application.common.notifiers import TelegramNotifier
from application.common.unit_of_work import UnitOfWork
from application.task_instance.events import (
    DailyAgendaRequested,
    ReminderNotificationRequested,
)
from application.task_instance.formatters import TaskInstancesFormatter
from application.user.exceptions import UserNotFoundException

logger = logging.getLogger(__name__)


class SendTelegramReminderHandler(EventHandler[ReminderNotificationRequested]):
    def __init__(self, uow: UnitOfWork, telegram_notifier: TelegramNotifier):
        super().__init__(uow)
        self.telegram_notifier = telegram_notifier

    async def handle(
        self,
        event: ReminderNotificationRequested,
    ) -> None:

        task_instance = await self.uow.task_instances.get_by_id(
            uuid.UUID(event.task_instance_id)
        )
        if not task_instance:
            logger.error("Task instance %s not found", task_instance.id)
            return

        user = await self.uow.users.get_by_id(task_instance.user_id)

        if not user:
            logger.error("User %s not found", task_instance.user_id)
            return

        await self.telegram_notifier.send_message(
            user.telegram_user_id,
            f"Reminder '{task_instance.title}'\n{task_instance.description}",
        )
        logger.info("Reminder %s has been sent to %s", task_instance.id, user.id)


class SendTelegramDailyAgendaHandler(EventHandler[DailyAgendaRequested]):
    def __init__(self, uow: UnitOfWork, telegram_notifier: TelegramNotifier):
        super().__init__(uow)
        self.telegram_notifier = telegram_notifier

    async def handle(
        self,
        event: DailyAgendaRequested,
    ) -> None:

        user = await self.uow.users.get_by_id(uuid.UUID(event.user_id))
        if not user:
            raise UserNotFoundException({"user_id": event.user_id})

        day = datetime.date.fromisoformat(event.day)
        task_instances = await self.uow.task_instances.get_all_by_user(
            user_id=uuid.UUID(event.user_id),
            from_date=day,
            to_date=day,
        )

        result = TaskInstancesFormatter.format(task_instances)

        await self.telegram_notifier.send_message(
            telegram_id=user.telegram_user_id, text=result
        )
