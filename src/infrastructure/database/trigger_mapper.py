import datetime
import uuid
from typing import Any

from domain.task_template.entities import (
    DailyTrigger,
    MonthlyTrigger,
    OneTimeTrigger,
    Trigger,
    WeeklyTrigger,
    YearlyTrigger,
)
from domain.task_template.value_objects import (
    DayOfMonth,
    Month,
    TriggerType,
    Weekday,
)


class TriggerMapper:
    @staticmethod
    def trigger_from_dict(data: dict[str, Any]) -> Trigger:
        trigger_type = TriggerType(data["type"])

        reminder_time_raw = data.get("reminder_time")
        reminder_time: datetime.time | None = None
        if reminder_time_raw:
            reminder_time = datetime.time.fromisoformat(reminder_time_raw)

        match trigger_type:
            case TriggerType.DAILY:
                return DailyTrigger(
                    id=uuid.UUID(data["id"]),
                    reminder_time=reminder_time,
                )

            case TriggerType.ONE_TIME:
                return OneTimeTrigger(
                    id=uuid.UUID(data["id"]),
                    occurrence_date=datetime.date.fromisoformat(
                        data["occurrence_date"]
                    ),
                    reminder_time=reminder_time,
                )

            case TriggerType.WEEKLY:
                return WeeklyTrigger(
                    id=uuid.UUID(data["id"]),
                    weekdays=frozenset(
                        Weekday(weekday) for weekday in data["weekdays"]
                    ),
                    reminder_time=reminder_time,
                )

            case TriggerType.MONTHLY:
                return MonthlyTrigger(
                    id=uuid.UUID(data["id"]),
                    day_of_month=DayOfMonth(data["day_of_month"]),
                    reminder_time=reminder_time,
                )

            case TriggerType.YEARLY:
                return YearlyTrigger(
                    id=uuid.UUID(data["id"]),
                    month=Month(data["month"]),
                    day=DayOfMonth(data["day"]),
                    reminder_time=reminder_time,
                )

            case _:
                raise ValueError(f"Unsupported trigger type: {trigger_type}")

    @staticmethod
    def trigger_to_dict(trigger: Trigger) -> dict[str, Any]:
        reminder_time = getattr(
            trigger,
            "reminder_time",
            None,
        )

        base = {
            "id": str(trigger.id),
            "type": trigger.type.value,
            "reminder_time": (
                reminder_time.isoformat() if reminder_time is not None else None
            ),
        }

        match trigger:
            case OneTimeTrigger():
                return {
                    **base,
                    "occurrence_date": (trigger.occurrence_date.isoformat()),
                }
            case DailyTrigger():
                return base
            case WeeklyTrigger():
                return {
                    **base,
                    "weekdays": [weekday.value for weekday in trigger.weekdays],
                }
            case MonthlyTrigger():
                return {
                    **base,
                    "day_of_month": (trigger.day_of_month.value),
                }
            case YearlyTrigger():
                return {
                    **base,
                    "month": int(trigger.month),
                    "day": trigger.day.value,
                }
            case _:
                raise ValueError(f"Unsupported trigger type: {trigger.type}")
