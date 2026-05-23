import datetime
import typing

import pytest
from pydantic import ValidationError

from application.task_template.schemas import (
    DailyTriggerPayload,
    MonthlyTriggerPayload,
    OneTimeTriggerPayload,
    TriggerPayload,
    WeeklyTriggerPayload,
    YearlyTriggerPayload,
    trigger_payload_adapter,
)
from application.task_template.trigger_mapper import TriggerMapper
from domain.task_template.entities import (
    DailyTrigger,
    MonthlyTrigger,
    OneTimeTrigger,
    Trigger,
    WeeklyTrigger,
    YearlyTrigger,
)
from domain.task_template.exceptions import (
    EmptyWeekdaysException,
    InvalidDayOfMonthException,
    InvalidYearlyDateException,
)
from domain.task_template.value_objects import DayOfMonth, Month, Weekday


@pytest.mark.parametrize(
    "payload_data, expected_class",
    [
        (
            {"type": "DAILY", "reminder_time": "10:00:00"},
            DailyTriggerPayload,
        ),
        (
            {
                "type": "ONE_TIME",
                "occurrence_date": "2026-01-01",
                "reminder_time": "12:00:00",
            },
            OneTimeTriggerPayload,
        ),
        (
            {"type": "WEEKLY", "weekdays": [0, 2, 4], "reminder_time": "08:00:00"},
            WeeklyTriggerPayload,
        ),
        (
            {"type": "MONTHLY", "day_of_month": 15, "reminder_time": "18:00:00"},
            MonthlyTriggerPayload,
        ),
        (
            {"type": "YEARLY", "month": 12, "day": 31, "reminder_time": "23:59:59"},
            YearlyTriggerPayload,
        ),
    ],
)
def test_trigger_payload_validation_success(
    payload_data: dict[str, typing.Any], expected_class: type[TriggerPayload]
):
    result = trigger_payload_adapter.validate_python(payload_data)
    assert isinstance(result, expected_class)
    assert result.type == payload_data["type"]


@pytest.mark.parametrize(
    "payload_data",
    [
        {"type": "UNKNOWN"},  # Неизвестный тип
        {"type": "DAILY", "reminder_time": "invalid"},  # Неверный формат времени
        {
            "type": "ONE_TIME",
            "reminder_time": "10:00:00",
        },  # Отсутствует occurrence_date
        {"type": "WEEKLY", "reminder_time": "10:00:00"},  # Отсутствуют weekdays
        {"type": "MONTHLY", "reminder_time": "10:00:00"},  # Отсутствует day_of_month
        {"type": "YEARLY", "month": 1, "reminder_time": "10:00:00"},  # Отсутствует day
    ],
)
def test_trigger_payload_validation_failure(payload_data: dict[str, typing.Any]):
    with pytest.raises(ValidationError):
        trigger_payload_adapter.validate_python(payload_data)


@pytest.mark.parametrize(
    "payload_dict, expected_domain_class, extra_assertions",
    [
        (
            {"type": "DAILY", "reminder_time": "10:00:00"},
            DailyTrigger,
            lambda domain: domain.reminder_time == datetime.time(10, 0),
        ),
        (
            {
                "type": "ONE_TIME",
                "occurrence_date": "2026-01-01",
                "reminder_time": "12:00:00",
            },
            OneTimeTrigger,
            lambda domain: domain.occurrence_date == datetime.date(2026, 1, 1)
            and domain.reminder_time == datetime.time(12, 0),
        ),
        (
            {"type": "WEEKLY", "weekdays": [0, 6], "reminder_time": "08:00:00"},
            WeeklyTrigger,
            lambda domain: domain.weekdays
            == frozenset([Weekday.MONDAY, Weekday.SUNDAY])
            and domain.reminder_time == datetime.time(8, 0),
        ),
        (
            {"type": "MONTHLY", "day_of_month": 15, "reminder_time": "18:00:00"},
            MonthlyTrigger,
            lambda domain: domain.day_of_month == DayOfMonth(15)
            and domain.reminder_time == datetime.time(18, 0),
        ),
        (
            {"type": "YEARLY", "month": 12, "day": 31, "reminder_time": "23:59:59"},
            YearlyTrigger,
            lambda domain: domain.month == Month.DECEMBER
            and domain.day == DayOfMonth(31)
            and domain.reminder_time == datetime.time(23, 59, 59),
        ),
    ],
)
def test_trigger_mapping_success(
    payload_dict: dict[str, typing.Any],
    expected_domain_class: type[Trigger],
    extra_assertions: typing.Callable[[Trigger], bool],
):
    payload = trigger_payload_adapter.validate_python(payload_dict)
    domain_trigger = TriggerMapper.to_domain(payload)

    assert isinstance(domain_trigger, expected_domain_class)
    assert extra_assertions(domain_trigger)
    assert domain_trigger.id is not None


@pytest.mark.parametrize(
    "payload_dict, expected_exception",
    [
        (
            {"type": "WEEKLY", "weekdays": [], "reminder_time": None},
            EmptyWeekdaysException,
        ),
        (
            {"type": "MONTHLY", "day_of_month": 32, "reminder_time": None},
            InvalidDayOfMonthException,
        ),
        (
            {"type": "YEARLY", "month": 2, "day": 30, "reminder_time": None},
            InvalidYearlyDateException,
        ),
    ],
)
def test_trigger_mapping_exceptions(
    payload_dict: dict[str, typing.Any], expected_exception: type[Exception]
):
    payload = trigger_payload_adapter.validate_python(payload_dict)
    with pytest.raises(expected_exception):
        TriggerMapper.to_domain(payload)
