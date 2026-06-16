import logging

from application.common.events import EventHandler
from domain.task_instance.events import TaskReminderRequested

logger = logging.getLogger(__name__)


class SendTelegramReminderHandler(EventHandler[TaskReminderRequested]):
    async def handle(
        self,
        event: TaskReminderRequested,
    ) -> None:
        logger.info("Handler has called")
