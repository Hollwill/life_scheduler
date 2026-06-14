import datetime
import uuid

import pytest

from application.task_instance.queries import (
    GetTaskInstancesHandler,
    GetTaskInstancesQuery,
)
from application.task_instance.schemas import TaskInstanceResponse
from domain.task_instance.aggregate import TaskInstance, TaskStatus
from domain.user.value_objects import TimeZone
from infrastructure.memory.repositories import (
    MemoryTaskInstanceRepository,
    MemoryUserRepository,
)
from tests.factories.task_instance import TaskInstanceFactory
from tests.factories.user import UserFactory


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
@pytest.mark.parametrize(
    "day",
    (datetime.date.fromisoformat("2021-01-10"),),
)
@pytest.mark.parametrize(
    (
        "task_instance",
        "expected_response",
    ),
    (
        (
            TaskInstanceFactory.build(
                public_id="00000000",
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description=None,
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=None,
                status=TaskStatus.PENDING,
            ),
            [
                TaskInstanceResponse(
                    public_id="00000000",
                    title="Drink water",
                    description=None,
                    occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                    scheduled_at=None,
                    status="PENDING",
                ),
            ],
        ),
        (
            TaskInstanceFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
            ),
            [],
        ),
        (
            TaskInstanceFactory.build(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                occurrence_date=datetime.date.fromisoformat("2021-01-11"),
            ),
            [],
        ),
    ),
)
async def test_get_task_instances(
    user_id: uuid.UUID,
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    memory_user_repository: MemoryUserRepository,
    day: datetime.date,
    task_instance: TaskInstance,
    expected_response: list[TaskInstanceResponse],
):

    await memory_task_instance_repository.save(task_instance)

    handler = GetTaskInstancesHandler(
        task_instance_repository=memory_task_instance_repository,
        user_repository=memory_user_repository,
    )

    response = await handler.handle(
        GetTaskInstancesQuery(
            user_id=user_id,
            day=day,
        )
    )

    assert response == expected_response


@pytest.mark.parametrize(
    ("timezone", "scheduled_at_utc", "expected_scheduled_at"),
    (
        (
            TimeZone("Asia/Tokyo"),
            datetime.datetime.fromisoformat("2021-01-09T23:00:00+00:00"),
            datetime.datetime.fromisoformat("2021-01-10T08:00:00+09:00"),
        ),
        (
            TimeZone("Europe/Berlin"),
            datetime.datetime.fromisoformat("2021-01-10T07:00:00+00:00"),
            datetime.datetime.fromisoformat("2021-01-10T08:00:00+01:00"),
        ),
        (
            TimeZone("Europe/Moscow"),
            datetime.datetime.fromisoformat("2021-01-10T05:00:00+00:00"),
            datetime.datetime.fromisoformat("2021-01-10T08:00:00+03:00"),
        ),
    ),
)
async def test_get_task_instances_converts_scheduled_at_to_user_timezone(
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    memory_user_repository: MemoryUserRepository,
    timezone: TimeZone,
    scheduled_at_utc: datetime.datetime,
    expected_scheduled_at: datetime.datetime,
):
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

    user = UserFactory.build(
        id=user_id,
        timezone=timezone,
    )

    task_instance = TaskInstanceFactory.build(
        public_id="00000000",
        user_id=user_id,
        occurrence_date=datetime.date.fromisoformat("2021-01-10"),
        scheduled_at=scheduled_at_utc,
    )

    await memory_user_repository.save(user)
    await memory_task_instance_repository.save(task_instance)

    response = await GetTaskInstancesHandler(
        task_instance_repository=memory_task_instance_repository,
        user_repository=memory_user_repository,
    ).handle(
        GetTaskInstancesQuery(
            user_id=user_id,
            day=datetime.date.fromisoformat("2021-01-10"),
        )
    )

    assert response == [
        TaskInstanceResponse(
            public_id=task_instance.public_id,
            title=task_instance.title,
            description=task_instance.description,
            occurrence_date=task_instance.occurrence_date,
            scheduled_at=expected_scheduled_at,
            status=task_instance.status.value,
        )
    ]
