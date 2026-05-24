import datetime
import uuid

import pytest
from pytest import FixtureRequest

from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import (
    DailyTrigger,
    MonthlyTrigger,
    OneTimeTrigger,
    Trigger,
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


@pytest.fixture
def task_template_title() -> str:
    return "Default Title"


@pytest.fixture
def task_template_description() -> str:
    return "Default Description"


@pytest.fixture
def task_template_is_active() -> bool:
    return True


@pytest.fixture
def task_template_created_at() -> datetime.datetime:
    return datetime.datetime.now()


@pytest.fixture
def task_template_updated_at(
    task_template_created_at: datetime.datetime,
) -> datetime.datetime:
    return task_template_created_at


@pytest.fixture
def task_template(
    user_id: uuid.UUID,
    task_template_title: str,
    task_template_description: str,
    trigger: Trigger,
    task_template_is_active: bool,
    task_template_created_at: datetime.datetime,
    task_template_updated_at: datetime.datetime,
) -> TaskTemplate:
    return TaskTemplate(
        id=uuid.uuid4(),
        user_id=user_id,
        title=task_template_title,
        description=task_template_description,
        trigger=trigger,
        is_active=task_template_is_active,
        created_at=task_template_created_at,
        updated_at=task_template_updated_at,
    )
