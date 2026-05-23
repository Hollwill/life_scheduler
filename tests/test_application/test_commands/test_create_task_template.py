import pytest

from application.task_template.commands import (
    CreateTaskTemplateCommand,
    CreateTaskTemplateHandler,
)
from application.task_template.exceptions import UserNotFoundException
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import Trigger
from domain.task_template.value_objects import TriggerType, Weekday
from domain.user.aggregate import User
from infrastructure.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)
from infrastructure.repositories.memory_user_repository import MemoryUserRepository


@pytest.mark.parametrize(
    "trigger",
    (
        {
            "type": TriggerType.WEEKLY,
            "weekdays": {Weekday.MONDAY},
        },
    ),
    indirect=True,
)
@pytest.mark.parametrize(
    ("task_template_title", "task_template_description"),
    (
        ("Wash floor", "Kitchen and bathroom"),
        ("Wash floor", None),
    ),
)
async def test_create_task_template_handler_creates_and_saves_template(
    user: User,
    trigger: Trigger,
    task_template_title: str,
    task_template_description: str,
):
    task_template_repository = MemoryTaskTemplateRepository()
    user_repository = MemoryUserRepository()

    await user_repository.add(user)

    handler = CreateTaskTemplateHandler(
        task_template_repository=task_template_repository,
        user_repository=user_repository,
    )

    command = CreateTaskTemplateCommand(
        user_id=user.id,
        title=task_template_title,
        description=task_template_description,
        trigger=trigger,
    )

    task_template_id = await handler.handle(command)

    saved_template = await task_template_repository.get_by_id(task_template_id)

    assert isinstance(saved_template, TaskTemplate)

    assert saved_template.user_id == command.user_id
    assert saved_template.title == task_template_title
    assert saved_template.description == task_template_description

    assert saved_template.trigger == trigger

    assert saved_template.is_active is True

    assert task_template_id == saved_template.id


@pytest.mark.parametrize(
    "trigger",
    (
        {
            "type": TriggerType.WEEKLY,
            "weekdays": {Weekday.MONDAY},
        },
    ),
    indirect=True,
)
@pytest.mark.parametrize(
    ("task_template_title", "task_template_description"),
    (("Wash floor", "Kitchen and bathroom"),),
)
async def test_create_task_template_user_not_found(
    user: User,
    trigger: Trigger,
    task_template_title: str,
    task_template_description: str,
):
    task_template_repository = MemoryTaskTemplateRepository()
    user_repository = MemoryUserRepository()

    handler = CreateTaskTemplateHandler(
        task_template_repository=task_template_repository,
        user_repository=user_repository,
    )

    command = CreateTaskTemplateCommand(
        user_id=user.id,
        title=task_template_title,
        description=task_template_description,
        trigger=trigger,
    )

    with pytest.raises(UserNotFoundException):
        await handler.handle(command)
