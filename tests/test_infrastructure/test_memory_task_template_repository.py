import datetime
import typing
import uuid

import pytest

from domain.task_template.aggregate import TaskTemplate
from infrastructure.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)
from tests.factories.task_template import TaskTemplateFactory


class TaskTemplateRepoTestCase(typing.NamedTuple):
    title: str
    description: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


@pytest.mark.parametrize("task_template", (TaskTemplateFactory.build(),))
async def test_memory_task_template_repository_save_and_get(
    task_template: TaskTemplate,
):
    repo = MemoryTaskTemplateRepository()

    await repo.save(task_template)
    retrieved = await repo.get_by_id(task_template.id)

    assert retrieved is not None
    assert retrieved.id == task_template.id
    assert retrieved.title == task_template.title
    assert retrieved is not task_template  # Deepcopy check


async def test_memory_task_template_repository_get_none():
    repo = MemoryTaskTemplateRepository()
    retrieved = await repo.get_by_id(uuid.uuid4())
    assert retrieved is None


@pytest.mark.parametrize("task_template", (TaskTemplateFactory.build(),))
@pytest.mark.parametrize("title_to_change", ("Changed Title",))
async def test_memory_task_template_repository_deepcopy_isolation(
    task_template: TaskTemplate,
    title_to_change: str,
):
    task_template_title = task_template.title

    repo = MemoryTaskTemplateRepository()

    await repo.save(task_template)

    # Change original object
    task_template.title = title_to_change

    # Check that repo still has the original data
    retrieved = await repo.get_by_id(task_template.id)
    assert retrieved
    assert retrieved.title == task_template_title

    # Change retrieved object
    retrieved.title = title_to_change

    # Check that repo still has the original data
    retrieved_again = await repo.get_by_id(task_template.id)

    assert retrieved_again
    assert retrieved_again.title == task_template_title


@pytest.mark.parametrize(
    "task_templates",
    (
        (
            TaskTemplateFactory.build(),
            TaskTemplateFactory.build(),
        )
    ),
)
async def test_memory_task_template_repository_get_all_active(
    task_templates: typing.List[TaskTemplate],
):
    repo = MemoryTaskTemplateRepository()

    task_template1 = TaskTemplateFactory.build()
    task_template2 = TaskTemplateFactory.build()
    task_template_inactive = TaskTemplateFactory.build(is_active=False)

    await repo.save(task_template1)
    await repo.save(task_template2)
    await repo.save(task_template_inactive)

    task_templates = await repo.get_all_active()

    assert len(task_templates) == 2

    assert {task_template1.id, task_template2.id} == set(
        task_template.id for task_template in task_templates
    )
