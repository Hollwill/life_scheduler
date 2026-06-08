import datetime

import pytest

from application.task_template.commands import (
    DeactivateTaskTemplateCommand,
    DeactivateTaskTemplateHandler,
)
from application.task_template.exceptions import TaskTemplateNotFoundException
from domain.task_template.aggregate import TaskTemplate
from infrastructure.memory.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.task_template import TaskTemplateFactory


@pytest.mark.parametrize(
    "task_template",
    (TaskTemplateFactory.build(),),
)
async def test_deactivate_task_template_handler(
    task_template: TaskTemplate,
    memory_uow: MemoryUnitOfWork,
    memory_task_template_repository: MemoryTaskTemplateRepository,
    now: datetime.datetime,
):

    await memory_task_template_repository.save(task_template)

    handler = DeactivateTaskTemplateHandler(uow=memory_uow)

    command = DeactivateTaskTemplateCommand(
        task_template_public_id=task_template.public_id,
        now=now,
    )

    await handler.handle(command)

    updated_template = await memory_task_template_repository.get_by_id(task_template.id)

    assert updated_template
    assert updated_template.is_active is False


async def test_deactivate_task_template_not_found(
    memory_uow: MemoryUnitOfWork,
    now: datetime.datetime,
):

    handler = DeactivateTaskTemplateHandler(uow=memory_uow)

    command = DeactivateTaskTemplateCommand(task_template_public_id="00000000", now=now)

    with pytest.raises(TaskTemplateNotFoundException):
        await handler.handle(command)
