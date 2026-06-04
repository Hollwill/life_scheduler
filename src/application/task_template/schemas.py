import datetime
import typing

from pydantic import BaseModel, Field, TypeAdapter


class ReminderTimeTriggerPayload(BaseModel):
    reminder_time: datetime.time | None = None


class DailyTriggerPayload(ReminderTimeTriggerPayload):
    type: typing.Literal["DAILY"] = "DAILY"


class OneTimeTriggerPayload(ReminderTimeTriggerPayload):
    type: typing.Literal["ONE_TIME"] = "ONE_TIME"

    occurrence_date: datetime.date


class WeeklyTriggerPayload(ReminderTimeTriggerPayload):
    type: typing.Literal["WEEKLY"] = "WEEKLY"

    weekdays: list[int]


class MonthlyTriggerPayload(ReminderTimeTriggerPayload):
    type: typing.Literal["MONTHLY"] = "MONTHLY"

    day_of_month: int


class YearlyTriggerPayload(ReminderTimeTriggerPayload):
    type: typing.Literal["YEARLY"] = "YEARLY"

    month: int
    day: int


TriggerPayload: typing.TypeAlias = typing.Annotated[
    (
        DailyTriggerPayload
        | OneTimeTriggerPayload
        | WeeklyTriggerPayload
        | MonthlyTriggerPayload
        | YearlyTriggerPayload
    ),
    Field(discriminator="type"),
]

trigger_payload_adapter = TypeAdapter(TriggerPayload)


class TaskTemplateResponse(BaseModel):
    public_id: str
    title: str
    description: str | None
    trigger: TriggerPayload
