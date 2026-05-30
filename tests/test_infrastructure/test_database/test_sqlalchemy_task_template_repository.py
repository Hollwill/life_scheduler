import uuid

import pytest

from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import (
    DailyTrigger,
    MonthlyTrigger,
    OneTimeTrigger,
    Trigger,
    WeeklyTrigger,
    YearlyTrigger,
)
from infrastructure.database.repositories.task_template import (
    SqlAlchemyTaskTemplateRepository,
)
from tests.factories.task_template import TaskTemplateFactory
from tests.factories.trigger import (
    DailyTriggerFactory,
    MonthlyTriggerFactory,
    OneTimeTriggerFactory,
    WeeklyTriggerFactory,
    YearlyTriggerFactory,
)


@pytest.mark.parametrize("task_template", (TaskTemplateFactory.build(),))
async def test_save_task_template(
    task_template_database_repository: SqlAlchemyTaskTemplateRepository,
    task_template: TaskTemplate,
):
    await task_template_database_repository.save(
        task_template,
    )

    loaded = await task_template_database_repository.get_by_id(
        task_template.id,
    )

    assert loaded is not None
    assert loaded.id == task_template.id
    assert loaded.title == task_template.title
    assert loaded.description == (task_template.description)


async def test_get_task_template_by_unknown_id_returns_none(
    task_template_database_repository: SqlAlchemyTaskTemplateRepository,
):
    loaded = await task_template_database_repository.get_by_id(
        uuid.uuid4(),
    )

    assert loaded is None


async def test_get_all_active_returns_only_active_templates(
    task_template_database_repository: SqlAlchemyTaskTemplateRepository,
):
    active = TaskTemplateFactory.build(
        is_active=True,
    )

    inactive = TaskTemplateFactory.build(
        is_active=False,
    )

    await task_template_database_repository.save(
        active,
    )
    await task_template_database_repository.save(
        inactive,
    )

    templates = await task_template_database_repository.get_all_active()

    assert len(templates) == 1
    assert next(iter(templates)).id == active.id


@pytest.mark.parametrize("task_template", (TaskTemplateFactory.build(),))
@pytest.mark.parametrize("new_title", ("Updated title",))
async def test_save_updates_existing_template(
    task_template_database_repository: SqlAlchemyTaskTemplateRepository,
    task_template: TaskTemplate,
    new_title: str,
    now,
):
    await task_template_database_repository.save(
        task_template,
    )

    task_template.change_title(
        new_title,
        now,
    )

    await task_template_database_repository.save(
        task_template,
    )

    loaded = await task_template_database_repository.get_by_id(
        task_template.id,
    )

    assert loaded is not None
    assert loaded.title == new_title


@pytest.mark.parametrize(
    ("trigger", "expected_trigger_type"),
    (
        (
            DailyTriggerFactory.build(),
            DailyTrigger,
        ),
        (
            OneTimeTriggerFactory.build(),
            OneTimeTrigger,
        ),
        (
            WeeklyTriggerFactory.build(),
            WeeklyTrigger,
        ),
        (
            MonthlyTriggerFactory.build(),
            MonthlyTrigger,
        ),
        (
            YearlyTriggerFactory.build(),
            YearlyTrigger,
        ),
    ),
)
async def test_save_and_load_triggers(
    task_template_database_repository: SqlAlchemyTaskTemplateRepository,
    trigger: Trigger,
    expected_trigger_type: type[Trigger],
):

    template = TaskTemplateFactory.build(trigger=trigger)

    await task_template_database_repository.save(template)

    loaded = await task_template_database_repository.get_by_id(
        template.id,
    )

    assert loaded is not None
    assert isinstance(loaded.trigger, expected_trigger_type)
    assert loaded.trigger == trigger
