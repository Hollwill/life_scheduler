import datetime

import pytest

from application.task_instance.commands import (
    GenerateTaskRemindersCommand,
    GenerateTaskRemindersHandler,
)
from domain.task_instance.aggregate import TaskInstance, TaskStatus
from domain.task_instance.events import TaskReminderRequested
from infrastructure.memory.repositories import MemoryTaskInstanceRepository
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.task_instance import TaskInstanceFactory


@pytest.mark.parametrize(
    "now", (datetime.datetime.fromisoformat("2021-01-10T08:00:00"),)
)
@pytest.mark.parametrize(
    (
        "task_instance",
        "should_remind",
    ),
    (
        # 1. happy path → reminder created
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
                status=TaskStatus.PENDING,
                reminded_at=None,
            ),
            True,
        ),
        # 2. wrong status → no reminder
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
                status=TaskStatus.COMPLETED,
                reminded_at=None,
            ),
            False,
        ),
        # 3. already reminded → idempotent skip
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
                status=TaskStatus.PENDING,
                reminded_at=datetime.datetime.fromisoformat("2021-01-10T07:50:00"),
            ),
            False,
        ),
        # 4. wrong date → skip
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-09"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
                status=TaskStatus.PENDING,
                reminded_at=None,
            ),
            False,
        ),
        # 5. no scheduled_at → skip
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=None,
                status=TaskStatus.PENDING,
                reminded_at=None,
            ),
            False,
        ),
    ),
)
async def test_generate_task_reminders_handler_cases(
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    memory_uow: MemoryUnitOfWork,
    now: datetime.datetime,
    task_instance: TaskInstance,
    should_remind: bool,
):
    reminded_at_before = task_instance.reminded_at
    await memory_task_instance_repository.save(task_instance)

    handler = GenerateTaskRemindersHandler(uow=memory_uow, now=now)

    await handler.handle(GenerateTaskRemindersCommand())

    updated = await memory_task_instance_repository.get_by_id(task_instance.id)

    assert updated

    if should_remind:
        assert updated.reminded_at == now
        assert any(isinstance(e, TaskReminderRequested) for e in updated.flush_events())
    else:
        assert updated.reminded_at == reminded_at_before
        assert updated.flush_events() == []
