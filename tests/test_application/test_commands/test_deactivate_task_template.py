import datetime

import pytest

from application.task_template.commands import (
    DeactivateTaskTemplateCommand,
    DeactivateTaskTemplateHandler,
)
from application.task_template.exceptions import TaskTemplateNotFoundException
from application.task_template.schemas import (
    TriggerPayload,
)
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.value_objects import Weekday
from infrastructure.memory.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)
from tests.factories.task_template import TaskTemplateFactory
from tests.factories.trigger import WeeklyTriggerFactory


@pytest.mark.parametrize(
    "task_template",
    (TaskTemplateFactory.build(),),
)
async def test_deactivate_task_template_handler(
    task_template: TaskTemplate,
    now: datetime.datetime,
):
    task_template_repository = MemoryTaskTemplateRepository()

    await task_template_repository.save(task_template)

    handler = DeactivateTaskTemplateHandler(
        task_template_repository=task_template_repository,
    )

    command = DeactivateTaskTemplateCommand(
        task_template_public_id=task_template.public_id,
        now=now,
    )

    await handler.handle(command)

    updated_template = await task_template_repository.get_by_id(task_template.id)

    assert updated_template.is_active is False


@pytest.mark.parametrize(
    "trigger_payload",
    (WeeklyTriggerFactory.build(weekdays=frozenset([Weekday.MONDAY])),),
)
async def test_deactivate_task_template_not_found(
    trigger_payload: TriggerPayload,
    now: datetime.datetime,
):
    task_template_repository = MemoryTaskTemplateRepository()

    handler = DeactivateTaskTemplateHandler(
        task_template_repository=task_template_repository,
    )

    command = DeactivateTaskTemplateCommand(task_template_public_id="00000000", now=now)

    with pytest.raises(TaskTemplateNotFoundException):
        await handler.handle(command)
