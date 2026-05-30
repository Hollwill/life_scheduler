import datetime
import uuid
from typing import Any

import pytest

from domain.task_template.entities import Trigger
from domain.task_template.value_objects import DayOfMonth, Month, TriggerType, Weekday
from infrastructure.database.mappers import trigger_from_dict, trigger_to_dict
from tests.factories.trigger import (
    DailyTriggerFactory,
    MonthlyTriggerFactory,
    OneTimeTriggerFactory,
    WeeklyTriggerFactory,
    YearlyTriggerFactory,
)


@pytest.mark.parametrize(
    ("trigger", "dict_trigger_representation"),
    (
        (
            OneTimeTriggerFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                reminder_time=datetime.time.fromisoformat("08:00:00"),
            ),
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "type": TriggerType.ONE_TIME.value,
                "occurrence_date": "2021-01-10",
                "reminder_time": "08:00:00",
            },
        ),
        (
            DailyTriggerFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                reminder_time=datetime.time.fromisoformat("08:00:00"),
            ),
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "type": TriggerType.DAILY.value,
                "reminder_time": "08:00:00",
            },
        ),
        (
            DailyTriggerFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                reminder_time=None,
            ),
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "type": TriggerType.DAILY.value,
                "reminder_time": None,
            },
        ),
        (
            WeeklyTriggerFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                weekdays=frozenset({Weekday.MONDAY, Weekday.TUESDAY}),
                reminder_time=datetime.time.fromisoformat("08:00:00"),
            ),
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "type": TriggerType.WEEKLY.value,
                "reminder_time": "08:00:00",
                "weekdays": [Weekday.MONDAY.value, Weekday.TUESDAY.value],
            },
        ),
        (
            MonthlyTriggerFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                day_of_month=DayOfMonth(15),
                reminder_time=datetime.time.fromisoformat("08:00:00"),
            ),
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "type": TriggerType.MONTHLY.value,
                "reminder_time": "08:00:00",
                "day_of_month": 15,
            },
        ),
        (
            YearlyTriggerFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                month=Month.JANUARY,
                day=DayOfMonth(15),
                reminder_time=datetime.time.fromisoformat("08:00:00"),
            ),
            {
                "id": "00000000-0000-0000-0000-000000000000",
                "type": TriggerType.YEARLY.value,
                "reminder_time": "08:00:00",
                "day": 15,
                "month": Month.JANUARY.value,
            },
        ),
    ),
)
def test_trigger_to_dict(trigger: Trigger, dict_trigger_representation: dict[str, Any]):

    assert trigger_to_dict(trigger) == dict_trigger_representation

    assert trigger_from_dict(dict_trigger_representation) == trigger
