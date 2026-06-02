import uuid

from application.task_template.schemas import (
    DailyTriggerPayload,
    MonthlyTriggerPayload,
    OneTimeTriggerPayload,
    TriggerPayload,
    WeeklyTriggerPayload,
    YearlyTriggerPayload,
)
from domain.task_template.entities import (
    DailyTrigger,
    MonthlyTrigger,
    OneTimeTrigger,
    Trigger,
    WeeklyTrigger,
    YearlyTrigger,
)
from domain.task_template.value_objects import DayOfMonth, Month, Weekday


class TriggerMapper:
    @staticmethod
    def to_domain(
        payload: TriggerPayload,
    ) -> Trigger:

        match payload:
            case DailyTriggerPayload():
                return DailyTrigger(
                    id=uuid.uuid4(),
                    reminder_time=payload.reminder_time,
                )

            case OneTimeTriggerPayload():
                return OneTimeTrigger(
                    id=uuid.uuid4(),
                    occurrence_date=payload.occurrence_date,
                    reminder_time=payload.reminder_time,
                )

            case WeeklyTriggerPayload():
                return WeeklyTrigger(
                    id=uuid.uuid4(),
                    weekdays=frozenset(Weekday(day) for day in payload.weekdays),
                    reminder_time=payload.reminder_time,
                )

            case MonthlyTriggerPayload():
                return MonthlyTrigger(
                    id=uuid.uuid4(),
                    day_of_month=DayOfMonth(payload.day_of_month),
                    reminder_time=payload.reminder_time,
                )

            case YearlyTriggerPayload():
                return YearlyTrigger(
                    id=uuid.uuid4(),
                    month=Month(payload.month),
                    day=DayOfMonth(payload.day),
                    reminder_time=payload.reminder_time,
                )
            case _:
                raise AssertionError("Trigger type not supported")

    @staticmethod
    def to_model(
        trigger: Trigger,
    ) -> TriggerPayload:

        match trigger:
            case DailyTrigger():
                return DailyTriggerPayload(
                    reminder_time=trigger.reminder_time,
                )

            case OneTimeTrigger():
                return OneTimeTriggerPayload(
                    occurrence_date=trigger.occurrence_date,
                    reminder_time=trigger.reminder_time,
                )

            case WeeklyTrigger():
                return WeeklyTriggerPayload(
                    weekdays=[int(day) for day in trigger.weekdays],
                    reminder_time=trigger.reminder_time,
                )

            case MonthlyTrigger():
                return MonthlyTriggerPayload(
                    day_of_month=trigger.day_of_month.value,
                    reminder_time=trigger.reminder_time,
                )

            case YearlyTrigger():
                return YearlyTriggerPayload(
                    month=int(trigger.month),
                    day=trigger.day.value,
                    reminder_time=trigger.reminder_time,
                )
            case _:
                raise AssertionError("Trigger type not supported")
