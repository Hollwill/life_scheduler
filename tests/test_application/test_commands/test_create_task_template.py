import datetime

import pytest

from application.task_template.commands import (
    CreateTaskTemplateCommand,
    CreateTaskTemplateHandler,
)
from application.task_template.schemas import (
    TriggerPayload,
    WeeklyTriggerPayload,
    trigger_payload_adapter,
)
from application.user.exceptions import UserNotFoundException
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import WeeklyTrigger
from domain.task_template.value_objects import TriggerType
from domain.user.aggregate import User
from infrastructure.memory.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)
from infrastructure.memory.repositories.memory_user_repository import (
    MemoryUserRepository,
)
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.user import UserFactory


@pytest.mark.parametrize("user", (UserFactory.build(),))
@pytest.mark.parametrize(
    "trigger_payload",
    (
        trigger_payload_adapter.validate_python(
            {"type": TriggerType.WEEKLY.value, "weekdays": [1], "reminder_time": None}
        ),
    ),
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
    memory_uow: MemoryUnitOfWork,
    memory_user_repository: MemoryUserRepository,
    memory_task_template_repository: MemoryTaskTemplateRepository,
    trigger_payload: WeeklyTriggerPayload,
    task_template_title: str,
    task_template_description: str | None,
):

    await memory_user_repository.save(user)

    handler = CreateTaskTemplateHandler(
        uow=memory_uow,
    )

    command = CreateTaskTemplateCommand(
        user_id=user.id,
        title=task_template_title,
        description=task_template_description,
        trigger_payload=trigger_payload,
        now=datetime.datetime.now(),
    )

    result = await handler.handle(command)
    task_template_public_id = result["task_template_public_id"]

    saved_template = await memory_task_template_repository.get_by_public_id(
        task_template_public_id
    )

    assert isinstance(saved_template, TaskTemplate)

    assert saved_template.user_id == command.user_id
    assert saved_template.title == task_template_title
    assert saved_template.description == task_template_description

    assert isinstance(saved_template.trigger, WeeklyTrigger)
    assert (
        list(map(lambda x: int(x), saved_template.trigger.weekdays))
        == trigger_payload.weekdays
    )
    assert saved_template.trigger.reminder_time == trigger_payload.reminder_time

    assert saved_template.is_active is True

    assert result == {
        "status": "success",
        "task_template_public_id": saved_template.public_id,
    }


@pytest.mark.parametrize("user", (UserFactory.build(),))
@pytest.mark.parametrize(
    "trigger_payload",
    (trigger_payload_adapter.dump_python({"type": "WEEKLY", "weekdays": [1]}),),
)
@pytest.mark.parametrize(
    ("task_template_title", "task_template_description"),
    (("Wash floor", "Kitchen and bathroom"),),
)
async def test_create_task_template_user_not_found(
    user: User,
    memory_uow: MemoryUnitOfWork,
    trigger_payload: TriggerPayload,
    task_template_title: str,
    task_template_description: str | None,
):

    handler = CreateTaskTemplateHandler(
        uow=memory_uow,
    )

    command = CreateTaskTemplateCommand(
        user_id=user.id,
        title=task_template_title,
        description=task_template_description,
        trigger_payload=trigger_payload,
        now=datetime.datetime.now(),
    )

    with pytest.raises(UserNotFoundException):
        await handler.handle(command)
