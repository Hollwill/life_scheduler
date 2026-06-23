import datetime
import uuid

import pytest

from application.task_instance.commands import (
    MissOverdueTaskInstancesCommand,
    MissOverdueTaskInstancesHandler,
)
from domain.task_instance.aggregate import TaskInstance, TaskStatus
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.task_instance import TaskInstanceFactory


@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10T08:00:00"),),
)
@pytest.mark.parametrize(
    "task_instances",
    (
        (
            TaskInstanceFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                status=TaskStatus.PENDING,
                occurrence_date=datetime.date.fromisoformat("2021-01-09"),
            ),
            TaskInstanceFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                status=TaskStatus.PENDING,
                occurrence_date=datetime.date.fromisoformat("2021-01-08"),
            ),
        ),
    ),
)
async def test_miss_overdue_task_instances(
    memory_uow: MemoryUnitOfWork,
    task_instances: tuple[TaskInstance, ...],
    now: datetime.datetime,
):
    async with memory_uow:
        for task_instance in task_instances:
            await memory_uow.task_instances.save(task_instance)

    await MissOverdueTaskInstancesHandler(
        uow=memory_uow,
    ).handle(
        MissOverdueTaskInstancesCommand(
            now=now,
        ),
    )

    for original_task in task_instances:
        task = await memory_uow.task_instances.get_by_id(original_task.id)

        assert task is not None
        assert task.status is TaskStatus.MISSED


@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10T08:00:00"),),
)
@pytest.mark.parametrize(
    "task_instance",
    (
        TaskInstanceFactory.build(
            id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            status=TaskStatus.PENDING,
            occurrence_date=datetime.date.fromisoformat("2021-01-09"),
        ),
    ),
)
async def test_miss_overdue_task_instances_is_idempotent(
    memory_uow: MemoryUnitOfWork,
    task_instance: TaskInstance,
    now: datetime.datetime,
):
    async with memory_uow:
        await memory_uow.task_instances.save(task_instance)

    handler = MissOverdueTaskInstancesHandler(
        uow=memory_uow,
    )

    await handler.handle(MissOverdueTaskInstancesCommand(now=now))
    await handler.handle(MissOverdueTaskInstancesCommand(now=now))

    task = await memory_uow.task_instances.get_by_id(task_instance.id)

    assert task is not None
    assert task.status is TaskStatus.MISSED
