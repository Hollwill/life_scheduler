import calendar
from typing import Iterable

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
    1: "Mon",
    2: "Tue",
    3: "Wed",
    4: "Thu",
    5: "Fri",
    6: "Sat",
    7: "Sun",
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
    parts = [f"#{str(task_template.id)[:8]}", f"{task_template.title}"]

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
