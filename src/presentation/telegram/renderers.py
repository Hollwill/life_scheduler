import calendar
from typing import Iterable

from application.task_instance.schemas import TaskInstanceResponse
from application.task_template.schemas import (
    DailyTriggerPayload,
    MonthlyTriggerPayload,
    OneTimeTriggerPayload,
    ReminderTimeTriggerPayload,
    TaskTemplateResponse,
    TriggerPayload,
    WeeklyTriggerPayload,
    YearlyTriggerPayload,
)

WEEKDAY_NAMES = {
    0: "Mon",
    1: "Tue",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}


def _render_trigger(trigger: TriggerPayload) -> str:
    response = ""
    match trigger:
        case OneTimeTriggerPayload():
            response = f"🔁 One Time ({trigger.occurrence_date.isoformat()})"
        case DailyTriggerPayload():
            response = "🔁 Daily"
        case WeeklyTriggerPayload():
            weekdays_rendered = ",".join(
                [WEEKDAY_NAMES[weekday] for weekday in trigger.weekdays]
            )
            response = f"🔁 Weekly ({weekdays_rendered})"
        case MonthlyTriggerPayload():
            response = f"🔁 Monthly ({trigger.day_of_month})"
        case YearlyTriggerPayload():
            response = (
                f"🔁 Yearly ({calendar.month_name[trigger.month]}, {trigger.day})"
            )
    if isinstance(trigger, ReminderTimeTriggerPayload) and trigger.reminder_time:
        response = "".join((response, f"\n⏰ {trigger.reminder_time.isoformat()}"))

    return response


def _render_task_template(task_template: TaskTemplateResponse) -> str:
    parts = [f"#{str(task_template.public_id)}", f"{task_template.title}"]

    if task_template.description:
        parts.append(f"📝 {task_template.description}")

    parts.append(_render_trigger(task_template.trigger))
    return "\n".join(parts)


def render_task_templates(task_templates: Iterable[TaskTemplateResponse]) -> str:
    header = "📋 Task templates"
    if not task_templates:
        return f"{header}\n\nNo templates found."

    rendered_task_templates = [
        _render_task_template(task_template) for task_template in task_templates
    ]
    return "\n\n".join((header, *rendered_task_templates))


def _render_task_instance(task_instance: TaskInstanceResponse) -> str:
    parts = [
        f"#{str(task_instance.public_id)}",
        task_instance.title,
    ]

    if task_instance.description:
        parts.append(f"📝 {task_instance.description}")

    parts.append(f"📅 {task_instance.occurrence_date.isoformat()}")

    if task_instance.scheduled_at:
        parts.append(
            f"⏰ {task_instance.scheduled_at.time().isoformat(timespec='minutes')}"
        )

    parts.append(f"✅ {task_instance.status}")

    return "\n".join(parts)


def render_task_instances(
    task_instances: Iterable[TaskInstanceResponse],
) -> str:
    header = "📋 Tasks"

    task_instances = list(task_instances)

    if not task_instances:
        return f"{header}\n\nNo tasks found."

    rendered = [
        _render_task_instance(task_instance) for task_instance in task_instances
    ]

    return "\n\n".join((header, *rendered))
