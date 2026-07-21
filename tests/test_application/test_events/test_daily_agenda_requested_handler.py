import datetime
import typing
import uuid

import pytest

from application.task_instance.event_handlers import (
    SendTelegramDailyAgendaHandler,
)
from application.task_instance.events import (
    DailyAgendaRequested,
)
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
    "task_instances",
    (
        [
            TaskInstanceFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Task Instance #0",
                public_id="QW73IGDK",
                description="description 1",
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
            ),
            TaskInstanceFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Task Instance #1",
                public_id="LX2SGHCF",
                description="description 2",
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
            ),
        ],
    ),
)
@pytest.mark.parametrize(
    "user", (UserFactory.build(id=uuid.UUID("00000000-0000-0000-0000-000000000000")),)
)
@pytest.mark.parametrize(
    "expected_message",
    (
        """📋 Tasks

#QW73IGDK
Task Instance #0
📝 description 1
📅 2021-01-10
⏰ 08:00
✅ TaskStatus.PENDING

#LX2SGHCF
Task Instance #1
📝 description 2
📅 2021-01-10
⏰ 08:00
✅ TaskStatus.PENDING""",
    ),
)
async def test_agenda_requested_handler(
    memory_user_repository: MemoryUserRepository,
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    memory_uow: MemoryUnitOfWork,
    user: User,
    task_instances: typing.Iterable[TaskInstance],
    expected_message: str,
    now: datetime.datetime,
) -> None:

    await memory_user_repository.save(user)
    for task_instance in task_instances:
        await memory_task_instance_repository.save(task_instance)

    telegram_notifier = FakeTelegramNotifier()

    handler = SendTelegramDailyAgendaHandler(
        uow=memory_uow, telegram_notifier=telegram_notifier
    )

    event = DailyAgendaRequested(user_id=str(user.id), day="2021-01-10")

    async with memory_uow:
        await handler.handle(event)

    task_instance_sent_messages = telegram_notifier.sent_messages[user.telegram_user_id]

    assert len(task_instance_sent_messages) == 1

    assert task_instance_sent_messages[0] == expected_message


@pytest.mark.parametrize(
    "user", (UserFactory.build(id=uuid.UUID("00000000-0000-0000-0000-000000000000")),)
)
@pytest.mark.parametrize(
    "expected_message",
    ("📋 Tasks\n\nNo tasks today.",),
)
async def test_agenda_requested_handler_no_tasks(
    memory_user_repository: MemoryUserRepository,
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    memory_uow: MemoryUnitOfWork,
    user: User,
    expected_message: str,
    now: datetime.datetime,
) -> None:

    await memory_user_repository.save(user)

    telegram_notifier = FakeTelegramNotifier()

    handler = SendTelegramDailyAgendaHandler(
        uow=memory_uow, telegram_notifier=telegram_notifier
    )

    event = DailyAgendaRequested(user_id=str(user.id), day="2021-01-10")

    async with memory_uow:
        await handler.handle(event)

    task_instance_sent_messages = telegram_notifier.sent_messages[user.telegram_user_id]

    assert len(task_instance_sent_messages) == 1

    assert task_instance_sent_messages[0] == expected_message
