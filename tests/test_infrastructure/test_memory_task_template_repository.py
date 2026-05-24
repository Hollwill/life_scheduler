import datetime
import typing
import uuid

import pytest

from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import DailyTrigger
from infrastructure.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)


class TaskTemplateRepoTestCase(typing.NamedTuple):
    title: str
    description: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


@pytest.mark.parametrize(
    TaskTemplateRepoTestCase._fields,
    [
        TaskTemplateRepoTestCase(
            title="Test Template",
            description="Description",
            is_active=True,
            created_at=datetime.datetime.fromisoformat("2026-05-24T09:00:00"),
            updated_at=datetime.datetime.fromisoformat("2026-05-24T09:00:00"),
        )
    ],
)
async def test_memory_task_template_repository_save_and_get(
    title: str,
    description: str,
    is_active: bool,
    created_at: datetime.datetime,
    updated_at: datetime.datetime,
):
    repo = MemoryTaskTemplateRepository()
    template_id = uuid.uuid4()
    template = TaskTemplate(
        id=template_id,
        user_id=uuid.uuid4(),
        title=title,
        description=description,
        trigger=DailyTrigger(id=uuid.uuid4()),
        is_active=is_active,
        created_at=created_at,
        updated_at=updated_at,
    )

    await repo.save(template)
    retrieved = await repo.get_by_id(template_id)

    assert retrieved is not None
    assert retrieved.id == template.id
    assert retrieved.title == template.title
    assert retrieved is not template  # Deepcopy check


async def test_memory_task_template_repository_get_none():
    repo = MemoryTaskTemplateRepository()
    retrieved = await repo.get_by_id(uuid.uuid4())
    assert retrieved is None


@pytest.mark.parametrize(
    ("title", "created_at"),
    [
        (
            "Original Title",
            datetime.datetime.fromisoformat("2026-05-24T09:00:00"),
        )
    ],
)
async def test_memory_task_template_repository_deepcopy_isolation(
    title: str,
    created_at: datetime.datetime,
):
    repo = MemoryTaskTemplateRepository()
    template = TaskTemplate(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title=title,
        description="Description",
        trigger=DailyTrigger(id=uuid.uuid4()),
        is_active=True,
        created_at=created_at,
        updated_at=created_at,
    )

    await repo.save(template)

    # Change original object
    template.title = "Changed Title"

    # Check that repo still has the original data
    retrieved = await repo.get_by_id(template.id)
    assert retrieved.title == title

    # Change retrieved object
    retrieved.title = "Changed Again"

    # Check that repo still has the original data
    retrieved_again = await repo.get_by_id(template.id)
    assert retrieved_again.title == title
