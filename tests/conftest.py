import datetime
import uuid

import pytest

from domain.task_instance.aggregate import TaskInstance, TaskStatus
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
    user: User,
    task_instance_title: str,
    task_instance_description: str,
    task_instance_occurrence_date: datetime.date,
    task_instance_scheduled_at: datetime.datetime,
    task_instance_created_at: datetime.datetime,
    task_instance_status: TaskStatus,
    task_instance_postpone_reason: str | None,
):
    task_template = TaskTemplateFactory.build()

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
