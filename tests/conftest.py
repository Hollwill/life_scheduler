import uuid

import pytest
from pytest import FixtureRequest

from domain.task_template.entities import (
    DailyTrigger,
    MonthlyTrigger,
    OneTimeTrigger,
    WeeklyTrigger,
    YearlyTrigger,
)
from domain.task_template.value_objects import DayOfMonth, TriggerType
from domain.user.aggregate import User


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def user_name() -> str:
    return "test"


@pytest.fixture
def user(user_id: uuid.UUID, user_name: str) -> User:
    return User(id=user_id, name=user_name)


@pytest.fixture
def trigger(request: FixtureRequest):

    params = request.param

    trigger_type: TriggerType = params["type"]

    match trigger_type:

        case TriggerType.DAILY:
            return DailyTrigger(
                id=uuid.uuid4(),
                reminder_time=params.get("reminder_time"),
            )

        case TriggerType.ONE_TIME:
            return OneTimeTrigger(
                id=uuid.uuid4(),
                occurrence_date=params["occurrence_date"],
                reminder_time=params.get("reminder_time"),
            )

        case TriggerType.WEEKLY:
            return WeeklyTrigger(
                id=uuid.uuid4(),
                weekdays=frozenset(params["weekdays"]),
                reminder_time=params.get("reminder_time"),
            )

        case TriggerType.MONTHLY:
            return MonthlyTrigger(
                id=uuid.uuid4(),
                day_of_month=DayOfMonth(params["day_of_month"]),
                reminder_time=params.get("reminder_time"),
            )

        case TriggerType.YEARLY:
            return YearlyTrigger(
                id=uuid.uuid4(),
                month=params["month"],
                day=DayOfMonth(params["day"]),
                reminder_time=params.get("reminder_time"),
            )
        case _:
            raise ValueError(f"Unknown trigger type: {trigger_type}")
