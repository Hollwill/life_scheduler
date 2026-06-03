import datetime
import uuid

import pytest

from application.task_instance.queries import (
    GetTaskInstancesHandler,
    GetTaskInstancesQuery,
)
from application.task_instance.schemas import TaskInstanceResponse
from domain.task_instance.aggregate import TaskInstance, TaskStatus
from infrastructure.memory.repositories import MemoryTaskInstanceRepository
from tests.factories.task_instance import TaskInstanceFactory


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
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description=None,
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=None,
                status=TaskStatus.PENDING,
            ),
            [
                TaskInstanceResponse(
                    id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
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
    day: datetime.date,
    task_instance: TaskInstance,
    expected_response: list[TaskInstanceResponse],
):
    repository = MemoryTaskInstanceRepository()

    await repository.save(task_instance)

    handler = GetTaskInstancesHandler(
        task_instance_repository=repository,
    )

    response = await handler.handle(
        GetTaskInstancesQuery(
            user_id=user_id,
            day=day,
        )
    )

    assert response == expected_response
