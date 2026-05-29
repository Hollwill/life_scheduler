import datetime
import uuid

import pytest

from application.task_template.commands import (
    GenerateTasksForDayCommand,
    GenerateTasksForDayHandler,
)
from domain.task_instance.aggregate import TaskInstance
from domain.task_instance.service import TaskGenerationService
from domain.task_template.aggregate import TaskTemplate
from infrastructure.repositories.memory_task_instance_repository import (
    MemoryTaskInstanceRepository,
)
from infrastructure.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)
from tests.factories.task_instance import TaskInstanceFactory
from tests.factories.task_template import TaskTemplateFactory
from tests.factories.trigger import OneTimeTriggerFactory


@pytest.mark.parametrize(
    "now", (datetime.datetime.fromisoformat("2021-01-10T08:00:00"),)
)
@pytest.mark.parametrize(
    "task_templates",
    (
        (
            TaskTemplateFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                trigger=OneTimeTriggerFactory.build(
                    occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                ),
            ),
            TaskTemplateFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                trigger=OneTimeTriggerFactory.build(
                    occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                ),
            ),
            TaskTemplateFactory.build(
                trigger=OneTimeTriggerFactory.build(
                    occurrence_date=datetime.date.fromisoformat("2021-01-11"),
                ),
            ),
            TaskTemplateFactory.build(
                trigger=OneTimeTriggerFactory.build(
                    occurrence_date=datetime.date.fromisoformat("2021-01-09"),
                ),
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    "task_instances",
    (
        (
            TaskInstanceFactory.build(
                task_template_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    ("expected_task_instance_count", "expected_task_template_ids"),
    (
        (
            2,
            (
                uuid.UUID("00000000-0000-0000-0000-000000000000"),
                uuid.UUID("00000000-0000-0000-0000-000000000001"),
            ),
        ),
    ),
)
async def test_generate_tasks_for_day(
    task_templates: tuple[TaskTemplate, ...],
    task_instances: tuple[TaskInstance, ...],
    expected_task_instance_count: int,
    expected_task_template_ids: tuple[uuid.UUID, ...],
    now: datetime.datetime,
):
    task_instance_repo = MemoryTaskInstanceRepository()
    task_template_repo = MemoryTaskTemplateRepository()
    task_generation_service = TaskGenerationService()

    for task_template in task_templates:
        await task_template_repo.save(task_template)

    for task_instance in task_instances:
        await task_instance_repo.save(task_instance)

    command = GenerateTasksForDayCommand(day=datetime.date.fromisoformat("2021-01-10"))

    await GenerateTasksForDayHandler(
        task_template_repository=task_template_repo,
        task_instance_repository=task_instance_repo,
        task_generation_service=task_generation_service,
        now=now,
    ).handle(command)

    task_instances = await task_instance_repo.get_all_by_day(command.day)

    assert len(task_instances) == expected_task_instance_count

    assert {task_instance.task_template_id for task_instance in task_instances} == set(
        expected_task_template_ids
    )
