import datetime

import pytest

from application.task_instance.commands import (
    CompleteTaskInstanceCommand,
    CompleteTaskInstanceHandler,
)
from application.task_instance.exceptions import TaskInstanceNotFoundException
from domain.task_instance.aggregate import TaskInstance, TaskStatus
from infrastructure.memory.repositories import MemoryTaskInstanceRepository
from tests.factories.task_instance import TaskInstanceFactory


@pytest.mark.parametrize(
    "task_instance",
    (TaskInstanceFactory.build(),),
)
async def test_complete_task_instance_handler(
    task_instance: TaskInstance,
    now: datetime.datetime,
):
    task_instance_repository = MemoryTaskInstanceRepository()

    await task_instance_repository.save(task_instance)

    handler = CompleteTaskInstanceHandler(
        task_instance_repository=task_instance_repository,
    )

    command = CompleteTaskInstanceCommand(
        task_instance_public_id=task_instance.public_id,
    )

    await handler.handle(command)

    updated_template = await task_instance_repository.get_by_id(task_instance.id)

    assert updated_template
    assert updated_template.status is TaskStatus.COMPLETED


async def test_complete_task_instance_not_found(
    now: datetime.datetime,
):
    task_instance_repository = MemoryTaskInstanceRepository()

    handler = CompleteTaskInstanceHandler(
        task_instance_repository=task_instance_repository,
    )

    command = CompleteTaskInstanceCommand(task_instance_public_id="00000000")

    with pytest.raises(TaskInstanceNotFoundException):
        await handler.handle(command)
