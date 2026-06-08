import datetime

import pytest

from application.task_instance.commands import (
    CompleteTaskInstanceCommand,
    CompleteTaskInstanceHandler,
)
from application.task_instance.exceptions import TaskInstanceNotFoundException
from domain.task_instance.aggregate import TaskInstance, TaskStatus
from infrastructure.memory.repositories import MemoryTaskInstanceRepository
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.task_instance import TaskInstanceFactory


@pytest.mark.parametrize(
    "task_instance",
    (TaskInstanceFactory.build(),),
)
async def test_complete_task_instance_handler(
    task_instance: TaskInstance,
    memory_uow: MemoryUnitOfWork,
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    now: datetime.datetime,
):

    await memory_task_instance_repository.save(task_instance)

    handler = CompleteTaskInstanceHandler(
        uow=memory_uow,
    )

    command = CompleteTaskInstanceCommand(
        task_instance_public_id=task_instance.public_id,
    )

    await handler.handle(command)

    updated_template = await memory_task_instance_repository.get_by_id(task_instance.id)

    assert updated_template
    assert updated_template.status is TaskStatus.COMPLETED


async def test_complete_task_instance_not_found(
    memory_uow: MemoryUnitOfWork,
    now: datetime.datetime,
):

    handler = CompleteTaskInstanceHandler(
        uow=memory_uow,
    )

    command = CompleteTaskInstanceCommand(task_instance_public_id="00000000")

    with pytest.raises(TaskInstanceNotFoundException):
        await handler.handle(command)
