import datetime
import uuid

import pytest

from application.task_template.commands import (
    UpdateTaskTemplateCommand,
    UpdateTaskTemplateHandler,
)
from application.task_template.exceptions import TaskTemplateNotFoundException
from application.task_template.schemas import (
    TriggerPayload,
    WeeklyTriggerPayload,
    trigger_payload_adapter,
)
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import WeeklyTrigger
from domain.task_template.value_objects import Weekday
from infrastructure.memory.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)
from tests.factories.task_template import TaskTemplateFactory
from tests.factories.trigger import WeeklyTriggerFactory


@pytest.mark.parametrize(
    "new_trigger_payload",
    (trigger_payload_adapter.validate_python({"type": "WEEKLY", "weekdays": [1]}),),
)
@pytest.mark.parametrize(
    "task_template",
    (TaskTemplateFactory.build(),),
)
@pytest.mark.parametrize(
    ("new_title", "new_description"), ((("New Title", "New Description"),))
)
async def test_update_task_template_handler_updates_and_saves_template(
    task_template: TaskTemplate,
    new_trigger_payload: WeeklyTriggerPayload,
    new_title: str,
    new_description: str,
):
    task_template_repository = MemoryTaskTemplateRepository()

    await task_template_repository.save(task_template)

    handler = UpdateTaskTemplateHandler(
        task_template_repository=task_template_repository,
    )

    command = UpdateTaskTemplateCommand(
        task_template_id=task_template.id,
        title=new_title,
        description=new_description,
        trigger_payload=new_trigger_payload,
        now=datetime.datetime.now(),
    )

    await handler.handle(command)

    updated_template = await task_template_repository.get_by_id(task_template.id)

    assert updated_template.title == new_title
    assert updated_template.description == new_description
    assert updated_template.updated_at > task_template.created_at

    assert isinstance(updated_template.trigger, WeeklyTrigger)
    assert (
        list(map(lambda x: int(x), updated_template.trigger.weekdays))
        == new_trigger_payload.weekdays
    )
    assert updated_template.trigger.reminder_time == new_trigger_payload.reminder_time

    # Test activation/deactivation
    updated_template.deactivate(datetime.datetime.now())
    assert updated_template.is_active is False

    updated_template.activate(datetime.datetime.now())
    assert updated_template.is_active is True


@pytest.mark.parametrize(
    "trigger_payload",
    (WeeklyTriggerFactory.build(weekdays=frozenset([Weekday.MONDAY])),),
)
async def test_update_task_template_not_found(
    trigger_payload: TriggerPayload,
):
    task_template_repository = MemoryTaskTemplateRepository()

    handler = UpdateTaskTemplateHandler(
        task_template_repository=task_template_repository,
    )

    command = UpdateTaskTemplateCommand(
        task_template_id=uuid.uuid4(),
        title="Title",
        description="Description",
        trigger_payload=trigger_payload,
        now=datetime.datetime.now(),
    )

    with pytest.raises(TaskTemplateNotFoundException):
        await handler.handle(command)
