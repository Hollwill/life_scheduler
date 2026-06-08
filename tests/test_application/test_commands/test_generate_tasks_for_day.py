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
from infrastructure.memory.repositories import (
    MemoryTaskInstanceRepository,
)
from infrastructure.memory.repositories.memory_task_template_repository import (
    MemoryTaskTemplateRepository,
)
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
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
                is_active=False,
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
    memory_uow: MemoryUnitOfWork,
    memory_task_template_repository: MemoryTaskTemplateRepository,
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    task_templates: tuple[TaskTemplate, ...],
    task_instances: tuple[TaskInstance, ...],
    expected_task_instance_count: int,
    expected_task_template_ids: tuple[uuid.UUID, ...],
    now: datetime.datetime,
):
    task_generation_service = TaskGenerationService()

    for task_template in task_templates:
        await memory_task_template_repository.save(task_template)

    for task_instance in task_instances:
        await memory_task_instance_repository.save(task_instance)

    command = GenerateTasksForDayCommand(day=datetime.date.fromisoformat("2021-01-10"))

    await GenerateTasksForDayHandler(
        uow=memory_uow,
        task_generation_service=task_generation_service,
        now=now,
    ).handle(command)

    task_instances = await memory_task_instance_repository.get_all_by_day(command.day)

    assert len(task_instances) == expected_task_instance_count

    assert {task_instance.task_template_id for task_instance in task_instances} == set(
        expected_task_template_ids
    )
