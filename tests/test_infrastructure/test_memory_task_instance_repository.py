import uuid

import pytest

from domain.task_instance.aggregate import TaskInstance
from infrastructure.repositories.memory_task_instance_repository import (
    MemoryTaskInstanceRepository,
)


async def test_memory_task_instance_repository_save_and_get(
    task_instance: TaskInstance,
):
    repo = MemoryTaskInstanceRepository()

    await repo.save(task_instance)
    retrieved = await repo.get_by_id(task_instance.id)

    assert retrieved is not None
    assert retrieved.id == task_instance.id
    assert retrieved.title == task_instance.title
    assert retrieved is not task_instance  # Deepcopy check


async def test_memory_task_instance_repository_get_none():
    repo = MemoryTaskInstanceRepository()
    retrieved = await repo.get_by_id(uuid.uuid4())
    assert retrieved is None


@pytest.mark.parametrize(
    "title_to_change",
    [
        "Changed Title",
    ],
)
async def test_memory_task_instance_repository_deepcopy_isolation(
    task_instance: TaskInstance,
    task_instance_title: str,
    title_to_change: str,
):
    repo = MemoryTaskInstanceRepository()

    await repo.save(task_instance)

    # Change original object
    task_instance.title = title_to_change

    # Check that repo still has the original data
    retrieved = await repo.get_by_id(task_instance.id)
    assert retrieved.title == task_instance_title

    # Change retrieved object
    retrieved.title = title_to_change

    # Check that repo still has the original data
    retrieved_again = await repo.get_by_id(task_instance.id)
    assert retrieved_again.title == task_instance_title
