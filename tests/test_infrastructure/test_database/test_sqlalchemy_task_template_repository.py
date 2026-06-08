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
    sqlalchemy_task_template_repository: SqlAlchemyTaskTemplateRepository,
    task_template: TaskTemplate,
):
    await sqlalchemy_task_template_repository.save(
        task_template,
    )

    loaded = await sqlalchemy_task_template_repository.get_by_id(
        task_template.id,
    )

    assert loaded is not None
    assert loaded.id == task_template.id
    assert loaded.title == task_template.title
    assert loaded.description == (task_template.description)


@pytest.mark.parametrize("public_id", ("12345678",))
@pytest.mark.parametrize(
    "task_template", (TaskTemplateFactory.build(public_id="12345678"),)
)
async def test_get_by_public_id_task_template(
    sqlalchemy_task_template_repository: SqlAlchemyTaskTemplateRepository,
    public_id: str,
    task_template: TaskTemplate,
):
    await sqlalchemy_task_template_repository.save(task_template)

    task_template = await sqlalchemy_task_template_repository.get_by_public_id(
        public_id
    )
    assert task_template is not None
    assert task_template.id == task_template.id
    assert task_template.title == task_template.title
    assert task_template.description == task_template.description


async def test_get_task_template_by_unknown_id_returns_none(
    sqlalchemy_task_template_repository: SqlAlchemyTaskTemplateRepository,
):
    loaded = await sqlalchemy_task_template_repository.get_by_id(
        uuid.uuid4(),
    )

    assert loaded is None


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
@pytest.mark.parametrize(
    (
        "task_template",
        "should_return",
    ),
    (
        (
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                is_active=True,
            ),
            True,
        ),
        (
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                is_active=False,
            ),
            False,
        ),
        (
            TaskTemplateFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                is_active=True,
            ),
            False,
        ),
    ),
)
async def test_get_all_active_by_user(
    sqlalchemy_task_template_repository: SqlAlchemyTaskTemplateRepository,
    user_id: uuid.UUID,
    task_template: TaskTemplate,
    should_return: bool,
):
    await sqlalchemy_task_template_repository.save(
        task_template,
    )
    templates = await sqlalchemy_task_template_repository.get_all_active_by_user(
        user_id=user_id
    )

    if should_return:
        assert len(templates) == 1
        assert next(iter(templates)).id == task_template.id
    else:
        assert len(templates) == 0


async def test_get_all_active_returns_only_active_templates(
    sqlalchemy_task_template_repository: SqlAlchemyTaskTemplateRepository,
):
    active = TaskTemplateFactory.build(
        is_active=True,
    )

    inactive = TaskTemplateFactory.build(
        is_active=False,
    )

    await sqlalchemy_task_template_repository.save(
        active,
    )
    await sqlalchemy_task_template_repository.save(
        inactive,
    )

    templates = await sqlalchemy_task_template_repository.get_all_active()

    assert len(templates) == 1
    assert next(iter(templates)).id == active.id


@pytest.mark.parametrize("task_template", (TaskTemplateFactory.build(),))
@pytest.mark.parametrize("new_title", ("Updated title",))
async def test_save_updates_existing_template(
    sqlalchemy_task_template_repository: SqlAlchemyTaskTemplateRepository,
    task_template: TaskTemplate,
    new_title: str,
    now,
):
    await sqlalchemy_task_template_repository.save(
        task_template,
    )

    task_template.change_title(
        new_title,
        now,
    )

    await sqlalchemy_task_template_repository.save(
        task_template,
    )

    loaded = await sqlalchemy_task_template_repository.get_by_id(
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
    sqlalchemy_task_template_repository: SqlAlchemyTaskTemplateRepository,
    trigger: Trigger,
    expected_trigger_type: type[Trigger],
):

    template = TaskTemplateFactory.build(trigger=trigger)

    await sqlalchemy_task_template_repository.save(template)

    loaded = await sqlalchemy_task_template_repository.get_by_id(
        template.id,
    )

    assert loaded is not None
    assert isinstance(loaded.trigger, expected_trigger_type)
    assert loaded.trigger == trigger
