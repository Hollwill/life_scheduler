import datetime
import uuid

import pytest

from application.task_instance.schemas import TaskInstanceResponse
from application.task_template.schemas import (
    DailyTriggerPayload,
    MonthlyTriggerPayload,
    OneTimeTriggerPayload,
    TaskTemplateResponse,
    TriggerPayload,
    WeeklyTriggerPayload,
    YearlyTriggerPayload,
)
from presentation.telegram.renderers import render_task_instances, render_task_templates


def test_render_task_templates_empty() -> None:
    assert render_task_templates([]) == "📋 Task templates\n\nNo templates found."


@pytest.mark.parametrize(
    ("task_template_id", "task_template_title"),
    ((uuid.UUID("00000000-0000-0000-0000-000000000001"), "Drink water"),),
)
@pytest.mark.parametrize(
    "expected_task_template_parts",
    (("📋 Task templates", "#00000000", "Drink water"),),
)
@pytest.mark.parametrize(
    ("trigger", "expected_trigger_parts"),
    (
        (
            DailyTriggerPayload(
                type="DAILY",
                reminder_time=datetime.time.fromisoformat("09:00"),
            ),
            (
                "🔁 Daily",
                "⏰ 09:00:00",
            ),
        ),
        (
            OneTimeTriggerPayload(
                type="ONE_TIME",
                occurrence_date=datetime.date.fromisoformat("2026-06-10"),
                reminder_time=datetime.time.fromisoformat("18:30"),
            ),
            (
                "🔁 One Time (2026-06-10)",
                "⏰ 18:30:00",
            ),
        ),
        (
            WeeklyTriggerPayload(
                type="WEEKLY",
                weekdays=[1, 3, 5],
                reminder_time=None,
            ),
            ("🔁 Weekly (Mon,Wed,Fri)",),
        ),
        (
            MonthlyTriggerPayload(
                type="MONTHLY",
                day_of_month=15,
                reminder_time=None,
            ),
            ("🔁 Monthly (15)",),
        ),
        (
            YearlyTriggerPayload(
                type="YEARLY",
                month=5,
                day=10,
                reminder_time=None,
            ),
            ("🔁 Yearly (May, 10)",),
        ),
    ),
)
def test_render_task_templates_trigger_types(
    task_template_id: uuid.UUID,
    task_template_title: str,
    trigger: TriggerPayload,
    expected_task_template_parts: tuple[str, ...],
    expected_trigger_parts: tuple[str, ...],
) -> None:
    template = TaskTemplateResponse(
        id=task_template_id,
        title=task_template_title,
        description=None,
        trigger=trigger,
    )

    result = render_task_templates([template])

    for expected_part in (*expected_task_template_parts, *expected_trigger_parts):
        assert expected_part in result


@pytest.mark.parametrize(
    "expected_task_template_parts",
    (("Drink water", "📝 2 liters per day"),),
)
@pytest.mark.parametrize(
    "task_template_response",
    (
        TaskTemplateResponse(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            title="Drink water",
            description="2 liters per day",
            trigger=DailyTriggerPayload(
                type="DAILY",
                reminder_time=None,
            ),
        ),
    ),
)
def test_render_task_templates_with_description(
    task_template_response: TaskTemplateResponse,
    expected_task_template_parts: tuple[str, ...],
) -> None:

    result = render_task_templates([task_template_response])

    for expected_part in expected_task_template_parts:
        assert expected_part in result


@pytest.mark.parametrize(
    "expected_task_template_parts",
    (("Drink water", "Workout", "#00000001", "#00000002"),),
)
@pytest.mark.parametrize(
    "task_template_responses",
    (
        (
            TaskTemplateResponse(
                id=uuid.UUID("00000001-0000-0000-0000-000000000001"),
                title="Drink water",
                description=None,
                trigger=DailyTriggerPayload(
                    type="DAILY",
                    reminder_time=None,
                ),
            ),
            TaskTemplateResponse(
                id=uuid.UUID("00000002-0000-0000-0000-000000000002"),
                title="Workout",
                description=None,
                trigger=MonthlyTriggerPayload(
                    type="MONTHLY",
                    day_of_month=15,
                    reminder_time=None,
                ),
            ),
        ),
    ),
)
def test_render_task_templates_multiple_templates(
    expected_task_template_parts: tuple[str, ...],
    task_template_responses: tuple[TaskTemplateResponse, ...],
) -> None:

    result = render_task_templates(task_template_responses)

    for expected_part in expected_task_template_parts:
        assert expected_part in result


def test_render_task_instances_empty() -> None:
    assert render_task_instances([]) == "📋 Tasks\n\nNo tasks found."


@pytest.mark.parametrize(
    ("task_instance_id", "task_instance_title"),
    (
        (
            uuid.UUID("00000000-0000-0000-0000-000000000001"),
            "Drink water",
        ),
    ),
)
@pytest.mark.parametrize(
    "expected_task_instance_parts",
    (
        (
            "📋 Tasks",
            "#00000000",
            "Drink water",
        ),
    ),
)
@pytest.mark.parametrize(
    (
        "occurrence_date",
        "scheduled_at",
        "status",
        "expected_status_parts",
    ),
    (
        (
            datetime.date.fromisoformat("2026-06-10"),
            None,
            "CREATED",
            (
                "📅 2026-06-10",
                "✅ CREATED",
            ),
        ),
        (
            datetime.date.fromisoformat("2026-06-10"),
            datetime.datetime.fromisoformat("2026-06-10T09:00:00"),
            "COMPLETED",
            (
                "📅 2026-06-10",
                "⏰ 09:00",
                "✅ COMPLETED",
            ),
        ),
    ),
)
def test_render_task_instances_status_and_schedule(
    task_instance_id: uuid.UUID,
    task_instance_title: str,
    occurrence_date: datetime.date,
    scheduled_at: datetime.datetime | None,
    status: str,
    expected_task_instance_parts: tuple[str, ...],
    expected_status_parts: tuple[str, ...],
) -> None:
    task_instance = TaskInstanceResponse(
        id=task_instance_id,
        title=task_instance_title,
        description=None,
        occurrence_date=occurrence_date,
        scheduled_at=scheduled_at,
        status=status,
    )

    result = render_task_instances([task_instance])

    for expected_part in (
        *expected_task_instance_parts,
        *expected_status_parts,
    ):
        assert expected_part in result


@pytest.mark.parametrize(
    "expected_task_instance_parts",
    (
        (
            "Drink water",
            "📝 2 liters per day",
        ),
    ),
)
@pytest.mark.parametrize(
    "task_instance_response",
    (
        TaskInstanceResponse(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            title="Drink water",
            description="2 liters per day",
            occurrence_date=datetime.date.fromisoformat("2026-06-10"),
            scheduled_at=None,
            status="CREATED",
        ),
    ),
)
def test_render_task_instances_with_description(
    task_instance_response: TaskInstanceResponse,
    expected_task_instance_parts: tuple[str, ...],
) -> None:
    result = render_task_instances([task_instance_response])

    for expected_part in expected_task_instance_parts:
        assert expected_part in result


@pytest.mark.parametrize(
    "expected_task_instance_parts",
    (
        (
            "Drink water",
            "Workout",
            "#00000001",
            "#00000002",
        ),
    ),
)
@pytest.mark.parametrize(
    "task_instance_responses",
    (
        (
            TaskInstanceResponse(
                id=uuid.UUID("00000001-0000-0000-0000-000000000001"),
                title="Drink water",
                description=None,
                occurrence_date=datetime.date.fromisoformat("2026-06-10"),
                scheduled_at=None,
                status="CREATED",
            ),
            TaskInstanceResponse(
                id=uuid.UUID("00000002-0000-0000-0000-000000000002"),
                title="Workout",
                description=None,
                occurrence_date=datetime.date.fromisoformat("2026-06-10"),
                scheduled_at=None,
                status="COMPLETED",
            ),
        ),
    ),
)
def test_render_task_instances_multiple_instances(
    expected_task_instance_parts: tuple[str, ...],
    task_instance_responses: tuple[TaskInstanceResponse, ...],
) -> None:
    result = render_task_instances(task_instance_responses)

    for expected_part in expected_task_instance_parts:
        assert expected_part in result
