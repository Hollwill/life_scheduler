import datetime
import uuid

import pytest

from application.task_template.commands import (
    GenerateTasksForDayCommand,
    GenerateTasksForDayHandler,
)
from domain.task_instance.aggregate import TaskInstance
from domain.task_template.aggregate import TaskTemplate
from domain.user.aggregate import User
from domain.user.value_objects import TimeZone
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.task_instance import TaskInstanceFactory
from tests.factories.task_template import TaskTemplateFactory
from tests.factories.trigger import OneTimeTriggerFactory
from tests.factories.user import UserFactory


@pytest.mark.parametrize(
    "now", (datetime.datetime.fromisoformat("2021-01-10T08:00:00"),)
)
@pytest.mark.parametrize(
    "task_templates",
    (
        (
            TaskTemplateFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                trigger=OneTimeTriggerFactory.build(
                    occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                ),
            ),
            TaskTemplateFactory.build(
                is_active=False,
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                trigger=OneTimeTriggerFactory.build(
                    occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                ),
            ),
            TaskTemplateFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                trigger=OneTimeTriggerFactory.build(
                    occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                ),
            ),
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                trigger=OneTimeTriggerFactory.build(
                    occurrence_date=datetime.date.fromisoformat("2021-01-11"),
                ),
            ),
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
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
    "user", (UserFactory.build(id=uuid.UUID("00000000-0000-0000-0000-000000000000")),)
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
    task_templates: tuple[TaskTemplate, ...],
    task_instances: tuple[TaskInstance, ...],
    expected_task_instance_count: int,
    expected_task_template_ids: tuple[uuid.UUID, ...],
    user: User,
    now: datetime.datetime,
):
    async with memory_uow:
        await memory_uow.users.save(user)

        for task_template in task_templates:
            await memory_uow.task_templates.save(task_template)

        for task_instance in task_instances:
            await memory_uow.task_instances.save(task_instance)

    command = GenerateTasksForDayCommand(
        day=datetime.date.fromisoformat("2021-01-10"),
        now=now,
    )

    await GenerateTasksForDayHandler(
        uow=memory_uow,
    ).handle(command)

    task_instances = await memory_uow.task_instances.get_all_by_day(command.day)

    assert len(task_instances) == expected_task_instance_count

    assert {task_instance.task_template_id for task_instance in task_instances} == set(
        expected_task_template_ids
    )


@pytest.mark.parametrize(
    ("timezone", "reminder_time", "expected_scheduled_at"),
    (
        (
            TimeZone("Europe/Berlin"),
            datetime.time.fromisoformat("08:00:00"),
            datetime.datetime.fromisoformat("2021-01-10T07:00:00+00:00"),
        ),
        (
            TimeZone("Europe/Moscow"),
            datetime.time.fromisoformat("08:00:00"),
            datetime.datetime.fromisoformat("2021-01-10T05:00:00+00:00"),
        ),
        (
            TimeZone("Asia/Tokyo"),
            datetime.time.fromisoformat("08:00:00"),
            datetime.datetime.fromisoformat("2021-01-09T23:00:00+00:00"),
        ),
    ),
)
@pytest.mark.parametrize(
    "user",
    (
        UserFactory.build(
            id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        ),
    ),
)
@pytest.mark.parametrize(
    "task_template",
    (
        TaskTemplateFactory.build(
            id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            trigger=OneTimeTriggerFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    ("command_day", "now"),
    (
        (
            datetime.date.fromisoformat("2021-01-10"),
            datetime.datetime.fromisoformat("2021-01-01T00:00:00"),
        ),
    ),
)
async def test_generate_tasks_for_day_respects_user_timezone(
    memory_uow: MemoryUnitOfWork,
    user: User,
    task_template: TaskTemplate,
    timezone: TimeZone,
    reminder_time: datetime.time,
    expected_scheduled_at: datetime.datetime,
    command_day: datetime.date,
    now: datetime.datetime,
):
    user.timezone = timezone

    task_template.trigger.reminder_time = reminder_time

    async with memory_uow:
        await memory_uow.users.save(user)
        await memory_uow.task_templates.save(task_template)

    await GenerateTasksForDayHandler(
        uow=memory_uow,
    ).handle(
        GenerateTasksForDayCommand(
            day=command_day,
            now=now,
        )
    )

    task_instances = await memory_uow.task_instances.get_all_by_day(command_day)

    assert len(task_instances) == 1

    task_instance = next(iter(task_instances))

    assert task_instance.scheduled_at == expected_scheduled_at
