import datetime

import pytest

from application.task_instance.commands import (
    UpdateTaskInstanceCommand,
    UpdateTaskInstanceHandler,
)
from application.task_instance.exceptions import TaskInstanceNotFoundException
from domain.task_instance.aggregate import TaskInstance
from infrastructure.memory.repositories.memory_task_instance_repository import (
    MemoryTaskInstanceRepository,
)
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.task_instance import TaskInstanceFactory


@pytest.mark.parametrize(
    "task_instance",
    (TaskInstanceFactory.build(),),
)
@pytest.mark.parametrize(
    (
        "new_title",
        "new_description",
        "new_occurrence_date",
        "new_scheduled_at",
    ),
    (
        (
            "New Title",
            "New Description",
            datetime.date(2026, 7, 25),
            datetime.datetime(2026, 7, 25, 19, 0),
        ),
        (
            "New Title",
            None,
            datetime.date(2026, 7, 25),
            None,
        ),
    ),
)
async def test_update_task_instance_handler_updates_and_saves_instance(
    memory_uow: MemoryUnitOfWork,
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    task_instance: TaskInstance,
    new_title: str,
    new_description: str | None,
    new_occurrence_date: datetime.date,
    new_scheduled_at: datetime.datetime | None,
):
    await memory_task_instance_repository.save(task_instance)

    handler = UpdateTaskInstanceHandler(
        uow=memory_uow,
    )

    command = UpdateTaskInstanceCommand(
        task_instance_public_id=task_instance.public_id,
        title=new_title,
        description=new_description,
        occurrence_date=new_occurrence_date,
        scheduled_at=new_scheduled_at,
        now=datetime.datetime.now(),
    )

    result = await handler.handle(command)

    updated_instance = await memory_task_instance_repository.get_by_id(
        task_instance.id,
    )

    assert updated_instance

    assert updated_instance.title == new_title
    assert updated_instance.description == new_description
    assert updated_instance.occurrence_date == new_occurrence_date
    assert updated_instance.scheduled_at == new_scheduled_at

    assert result == {
        "status": "success",
        "task_instance_public_id": task_instance.public_id,
    }


async def test_update_task_instance_not_found(
    memory_uow: MemoryUnitOfWork,
):
    handler = UpdateTaskInstanceHandler(
        uow=memory_uow,
    )

    command = UpdateTaskInstanceCommand(
        task_instance_public_id="12345678",
        title="Title",
        description="Description",
        occurrence_date=datetime.date(2026, 7, 25),
        scheduled_at=datetime.datetime(2026, 7, 25, 19, 0),
        now=datetime.datetime.now(),
    )

    with pytest.raises(TaskInstanceNotFoundException):
        await handler.handle(command)
