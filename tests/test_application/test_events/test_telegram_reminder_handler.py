import uuid

import pytest

from application.task_instance.event_handlers import SendTelegramReminderHandler
from application.task_instance.events import ReminderNotificationRequested
from domain.task_instance.aggregate import TaskInstance
from domain.user.aggregate import User
from infrastructure.memory.repositories import (
    MemoryTaskInstanceRepository,
    MemoryUserRepository,
)
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from infrastructure.notifiers import FakeTelegramNotifier
from tests.factories.task_instance import TaskInstanceFactory
from tests.factories.user import UserFactory


@pytest.mark.parametrize(
    "task_instance",
    (
        TaskInstanceFactory.build(
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000000")
        ),
    ),
)
@pytest.mark.parametrize(
    "user", (UserFactory.build(id=uuid.UUID("00000000-0000-0000-0000-000000000000")),)
)
async def test_telegram_reminder_handler(
    memory_user_repository: MemoryUserRepository,
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    memory_uow: MemoryUnitOfWork,
    user: User,
    task_instance: TaskInstance,
) -> None:

    await memory_user_repository.save(user)
    await memory_task_instance_repository.save(task_instance)

    telegram_notifier = FakeTelegramNotifier()

    handler = SendTelegramReminderHandler(
        uow=memory_uow, telegram_notifier=telegram_notifier
    )

    event = ReminderNotificationRequested(task_instance_id=str(task_instance.id))

    async with memory_uow:
        await handler.handle(event)

    task_instance_sent_messages = telegram_notifier.sent_messages[user.telegram_user_id]

    assert len(task_instance_sent_messages) == 1

    assert (
        task_instance_sent_messages[0]
        == f"Reminder '{task_instance.title}'\n{task_instance.description}"
    )
