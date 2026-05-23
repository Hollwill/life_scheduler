import datetime
import typing

from pydantic import BaseModel, Field, TypeAdapter


class DailyTriggerPayload(BaseModel):
    type: typing.Literal["DAILY"]

    reminder_time: datetime.time | None = None


class OneTimeTriggerPayload(BaseModel):
    type: typing.Literal["ONE_TIME"]

    occurrence_date: datetime.date
    reminder_time: datetime.time | None = None


class WeeklyTriggerPayload(BaseModel):
    type: typing.Literal["WEEKLY"]

    weekdays: list[int]
    reminder_time: datetime.time | None = None


class MonthlyTriggerPayload(BaseModel):
    type: typing.Literal["MONTHLY"]

    day_of_month: int
    reminder_time: datetime.time | None = None


class YearlyTriggerPayload(BaseModel):
    type: typing.Literal["YEARLY"]

    month: int
    day: int
    reminder_time: datetime.time | None = None


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
