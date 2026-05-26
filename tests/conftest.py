import datetime
import typing
import uuid

import pytest
from pytest import FixtureRequest

from domain.task_instance.aggregate import TaskInstance, TaskStatus
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
from tests.factories.task_template import TaskTemplateFactory


@pytest.fixture
def now() -> datetime.datetime:
    return datetime.datetime.now()


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

    trigger_type: TriggerType | None = None
    params: dict[str, typing.Any] = {}
    if getattr(request, "param", None):
        params = request.param

        trigger_type = params.get("type")
    else:
        trigger_type = TriggerType.DAILY

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
    return TaskTemplateFactory.build(
        user_id=user_id,
        title=task_template_title,
        description=task_template_description,
        trigger=trigger,
        is_active=task_template_is_active,
        created_at=task_template_created_at,
        updated_at=task_template_updated_at,
    )


@pytest.fixture
def task_instance_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def task_instance_title() -> str:
    return "Default Title"


@pytest.fixture
def task_instance_description() -> str:
    return "Default Description"


@pytest.fixture
def task_instance_occurrence_date(now: datetime.datetime) -> datetime.date:
    return now.date()


@pytest.fixture
def task_instance_scheduled_at(now: datetime.datetime) -> datetime.datetime:
    return now


@pytest.fixture
def task_instance_created_at(now: datetime.datetime) -> datetime.datetime:
    return now


@pytest.fixture
def task_instance_status() -> TaskStatus:
    return TaskStatus.PENDING


@pytest.fixture
def task_instance_postpone_reason() -> str | None:
    return None


@pytest.fixture
def task_instance(
    task_instance_id: uuid.UUID,
    task_template: TaskTemplate,
    user: User,
    task_instance_title: str,
    task_instance_description: str,
    task_instance_occurrence_date: datetime.date,
    task_instance_scheduled_at: datetime.datetime,
    task_instance_created_at: datetime.datetime,
    task_instance_status: TaskStatus,
    task_instance_postpone_reason: str | None,
):

    return TaskInstance(
        id=task_instance_id,
        task_template_id=task_template.id,
        user_id=user.id,
        title=task_instance_title,
        description=task_instance_description,
        occurrence_date=task_instance_occurrence_date,
        scheduled_at=task_instance_scheduled_at,
        created_at=task_instance_created_at,
        status=task_instance_status,
        postpone_reason=task_instance_postpone_reason,
    )
