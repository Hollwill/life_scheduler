import uuid

import pytest

from application.task_template.queries import (
    GetTaskTemplatesHandler,
    GetTaskTemplatesQuery,
)
from application.task_template.schemas import DailyTriggerPayload, TaskTemplateResponse
from domain.task_template.aggregate import TaskTemplate
from infrastructure.memory.repositories import MemoryTaskTemplateRepository
from tests.factories.task_template import TaskTemplateFactory
from tests.factories.trigger import DailyTriggerFactory


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
@pytest.mark.parametrize(
    (
        "task_template",
        "expected_response",
    ),
    (
        (
            TaskTemplateFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                public_id="00000000",
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                trigger=DailyTriggerFactory(reminder_time=None),
                description=None,
                is_active=True,
            ),
            [
                TaskTemplateResponse(
                    public_id="00000000",
                    title="Drink water",
                    description=None,
                    trigger=DailyTriggerPayload(type="DAILY", reminder_time=None),
                ),
            ],
        ),
        (
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                is_active=True,
            ),
            [],
        ),
        (
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                is_active=False,
            ),
            [],
        ),
    ),
)
async def test_get_task_templates(
    memory_task_template_repository: MemoryTaskTemplateRepository,
    user_id: uuid.UUID,
    task_template: TaskTemplate,
    expected_response: list[TaskTemplateResponse],
):

    await memory_task_template_repository.save(task_template)

    handler = GetTaskTemplatesHandler(
        task_template_repository=memory_task_template_repository
    )
    response = await handler.handle(GetTaskTemplatesQuery(user_id=user_id))
    assert response == expected_response
