import datetime
import typing
import uuid

import pytest

from domain.task_instance.aggregate import TaskInstance
from infrastructure.repositories.memory_task_instance_repository import (
    MemoryTaskInstanceRepository,
)


class TaskInstanceRepoTestCase(typing.NamedTuple):
    title: str
    description: str
    occurrence_date: datetime.date
    scheduled_at: datetime.datetime
    created_at: datetime.datetime


@pytest.mark.parametrize(
    TaskInstanceRepoTestCase._fields,
    [
        TaskInstanceRepoTestCase(
            title="Test Task",
            description="Description",
            occurrence_date=datetime.date.fromisoformat("2026-05-24"),
            scheduled_at=datetime.datetime.fromisoformat("2026-05-24T10:00:00"),
            created_at=datetime.datetime.fromisoformat("2026-05-24T09:00:00"),
        )
    ],
)
async def test_memory_task_instance_repository_save_and_get(
    title: str,
    description: str,
    occurrence_date: datetime.date,
    scheduled_at: datetime.datetime,
    created_at: datetime.datetime,
):
    repo = MemoryTaskInstanceRepository()
    task_instance_id = uuid.uuid4()
    instance = TaskInstance(
        id=task_instance_id,
        task_template_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title=title,
        description=description,
        occurrence_date=occurrence_date,
        scheduled_at=scheduled_at,
        created_at=created_at,
    )

    await repo.save(instance)
    retrieved = await repo.get_by_id(task_instance_id)

    assert retrieved is not None
    assert retrieved.id == instance.id
    assert retrieved.title == instance.title
    assert retrieved is not instance  # Deepcopy check


async def test_memory_task_instance_repository_get_none():
    repo = MemoryTaskInstanceRepository()
    retrieved = await repo.get_by_id(uuid.uuid4())
    assert retrieved is None


@pytest.mark.parametrize(
    ("title", "occurrence_date", "created_at"),
    [
        (
            "Original Title",
            datetime.date.fromisoformat("2026-05-24"),
            datetime.datetime.fromisoformat("2026-05-24T09:00:00"),
        )
    ],
)
async def test_memory_task_instance_repository_deepcopy_isolation(
    title: str,
    occurrence_date: datetime.date,
    created_at: datetime.datetime,
):
    repo = MemoryTaskInstanceRepository()
    instance = TaskInstance(
        id=uuid.uuid4(),
        task_template_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title=title,
        description="Description",
        occurrence_date=occurrence_date,
        scheduled_at=None,
        created_at=created_at,
    )

    await repo.save(instance)

    # Change original object
    instance.title = "Changed Title"

    # Check that repo still has the original data
    retrieved = await repo.get_by_id(instance.id)
    assert retrieved.title == title

    # Change retrieved object
    retrieved.title = "Changed Again"

    # Check that repo still has the original data
    retrieved_again = await repo.get_by_id(instance.id)
    assert retrieved_again.title == title
