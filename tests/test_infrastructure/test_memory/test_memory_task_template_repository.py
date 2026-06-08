import typing
import uuid

import pytest

from domain.task_template.aggregate import TaskTemplate
from infrastructure.memory.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)
from tests.factories.task_template import TaskTemplateFactory


@pytest.mark.parametrize("task_template", (TaskTemplateFactory.build(),))
async def test_memory_task_template_repository_save_and_get(
    memory_task_template_repository: MemoryTaskTemplateRepository,
    task_template: TaskTemplate,
):

    await memory_task_template_repository.save(task_template)
    retrieved = await memory_task_template_repository.get_by_id(task_template.id)

    assert retrieved is not None
    assert retrieved.id == task_template.id
    assert retrieved.title == task_template.title
    assert retrieved is not task_template  # Deepcopy check


async def test_memory_task_template_repository_get_none(
    memory_task_template_repository: MemoryTaskTemplateRepository,
):
    retrieved = await memory_task_template_repository.get_by_id(uuid.uuid4())
    assert retrieved is None


@pytest.mark.parametrize("task_template", (TaskTemplateFactory.build(),))
@pytest.mark.parametrize("title_to_change", ("Changed Title",))
async def test_memory_task_template_repository_deepcopy_isolation(
    memory_task_template_repository: MemoryTaskTemplateRepository,
    task_template: TaskTemplate,
    title_to_change: str,
):
    task_template_title = task_template.title

    await memory_task_template_repository.save(task_template)

    # Change original object
    task_template.title = title_to_change

    # Check that repo still has the original data
    retrieved = await memory_task_template_repository.get_by_id(task_template.id)
    assert retrieved
    assert retrieved.title == task_template_title

    # Change retrieved object
    retrieved.title = title_to_change

    # Check that repo still has the original data
    retrieved_again = await memory_task_template_repository.get_by_id(task_template.id)

    assert retrieved_again
    assert retrieved_again.title == task_template_title


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
@pytest.mark.parametrize(
    (
        "task_template",
        "should_return",
    ),
    (
        (
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                is_active=True,
            ),
            True,
        ),
        (
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                is_active=False,
            ),
            False,
        ),
        (
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                is_active=True,
            ),
            False,
        ),
    ),
)
async def test_memory_task_template_repository_get_all_active_by_user(
    memory_task_template_repository: MemoryTaskTemplateRepository,
    user_id: uuid.UUID,
    task_template: TaskTemplate,
    should_return: bool,
):
    await memory_task_template_repository.save(
        task_template,
    )
    templates = await memory_task_template_repository.get_all_active_by_user(
        user_id=user_id
    )

    if should_return:
        assert len(templates) == 1
        assert next(iter(templates)).id == task_template.id
    else:
        assert len(templates) == 0


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
    memory_task_template_repository: MemoryTaskTemplateRepository,
    task_templates: typing.List[TaskTemplate],
):

    task_template1 = TaskTemplateFactory.build()
    task_template2 = TaskTemplateFactory.build()
    task_template_inactive = TaskTemplateFactory.build(is_active=False)

    await memory_task_template_repository.save(task_template1)
    await memory_task_template_repository.save(task_template2)
    await memory_task_template_repository.save(task_template_inactive)

    task_templates = await memory_task_template_repository.get_all_active()

    assert len(task_templates) == 2

    assert {task_template1.id, task_template2.id} == set(
        task_template.id for task_template in task_templates
    )
