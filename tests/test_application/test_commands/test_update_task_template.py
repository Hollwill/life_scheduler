import datetime
import uuid

import pytest

from application.task_template.commands import (
    UpdateTaskTemplateCommand,
    UpdateTaskTemplateHandler,
)
from application.task_template.exceptions import TaskTemplateNotFoundException
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import DailyTrigger, Trigger
from domain.task_template.value_objects import TriggerType, Weekday
from infrastructure.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)


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
async def test_update_task_template_handler_updates_and_saves_template(
    trigger: Trigger,
):
    task_template_repository = MemoryTaskTemplateRepository()

    # Create and save initial template
    task_template = TaskTemplate.create(
        user_id=uuid.uuid4(),
        title="Old Title",
        description="Old Description",
        trigger=trigger,
        now=datetime.datetime.now() - datetime.timedelta(days=1),
    )
    await task_template_repository.save(task_template)

    handler = UpdateTaskTemplateHandler(
        task_template_repository=task_template_repository,
    )

    new_title = "New Title"
    new_description = "New Description"
    new_trigger = DailyTrigger(id=uuid.uuid4())

    command = UpdateTaskTemplateCommand(
        task_template_id=task_template.id,
        title=new_title,
        description=new_description,
        trigger=new_trigger,
        now=datetime.datetime.now(),
    )

    await handler.handle(command)

    updated_template = await task_template_repository.get_by_id(task_template.id)

    assert updated_template.title == new_title
    assert updated_template.description == new_description
    assert updated_template.trigger == new_trigger
    assert updated_template.updated_at > task_template.created_at

    # Test activation/deactivation
    updated_template.deactivate(datetime.datetime.now())
    assert updated_template.is_active is False

    updated_template.activate(datetime.datetime.now())
    assert updated_template.is_active is True


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
async def test_update_task_template_not_found(
    trigger: Trigger,
):
    task_template_repository = MemoryTaskTemplateRepository()

    handler = UpdateTaskTemplateHandler(
        task_template_repository=task_template_repository,
    )

    command = UpdateTaskTemplateCommand(
        task_template_id=uuid.uuid4(),
        title="Title",
        description="Description",
        trigger=trigger,
        now=datetime.datetime.now(),
    )

    with pytest.raises(TaskTemplateNotFoundException):
        await handler.handle(command)
