import datetime
import uuid

import pytest

from domain.task_instance.aggregate import TaskInstance
from infrastructure.database.repositories.task_instance import (
    SqlAlchemyTaskInstanceRepository,
)
from tests.factories.task_instance import TaskInstanceFactory


@pytest.mark.parametrize("task_instance", (TaskInstanceFactory.build(),))
async def test_save_task_instance(
    task_instance_database_repository: SqlAlchemyTaskInstanceRepository,
    task_instance: TaskInstance,
):
    await task_instance_database_repository.save(
        task_instance,
    )

    loaded = await task_instance_database_repository.get_by_id(
        task_instance.id,
    )

    assert loaded is not None
    assert loaded.id == task_instance.id
    assert loaded.title == task_instance.title
    assert loaded.description == task_instance.description


async def test_get_task_instance_by_unknown_id_returns_none(
    task_instance_database_repository: SqlAlchemyTaskInstanceRepository,
):
    loaded = await task_instance_database_repository.get_by_id(
        uuid.uuid4(),
    )

    assert loaded is None


@pytest.mark.parametrize("target_day", (datetime.date.fromisoformat("2026-05-30"),))
@pytest.mark.parametrize(
    "matching_task_instance",
    (
        TaskInstanceFactory.build(
            occurrence_date=datetime.date.fromisoformat("2026-05-30"),
        ),
    ),
)
@pytest.mark.parametrize(
    "other_task_instance",
    (
        TaskInstanceFactory.build(
            occurrence_date=datetime.date.fromisoformat("2026-05-31"),
        ),
    ),
)
async def test_get_all_by_day(
    task_instance_database_repository: SqlAlchemyTaskInstanceRepository,
    target_day: datetime.date,
    matching_task_instance: TaskInstance,
    other_task_instance: TaskInstance,
):

    await task_instance_database_repository.save(
        matching_task_instance,
    )

    await task_instance_database_repository.save(
        other_task_instance,
    )

    instances = await task_instance_database_repository.get_all_by_day(
        target_day,
    )

    assert len(instances) == 1
    assert next(iter(instances)).id == (matching_task_instance.id)
