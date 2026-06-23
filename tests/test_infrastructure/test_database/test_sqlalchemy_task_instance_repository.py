import datetime
import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.task_instance.aggregate import TaskInstance, TaskStatus
from infrastructure.database.repositories.task_instance import (
    SqlAlchemyTaskInstanceRepository,
)
from tests.factories.task_instance import TaskInstanceFactory


@pytest.mark.parametrize("task_instance", (TaskInstanceFactory.build(),))
async def test_save_task_instance(
    sqlalchemy_task_instance_repository: SqlAlchemyTaskInstanceRepository,
    task_instance: TaskInstance,
):
    await sqlalchemy_task_instance_repository.save(
        task_instance,
    )

    loaded = await sqlalchemy_task_instance_repository.get_by_id(
        task_instance.id,
    )

    assert loaded is not None
    assert loaded.id == task_instance.id
    assert loaded.title == task_instance.title
    assert loaded.description == task_instance.description


@pytest.mark.parametrize(
    "task_instance", (TaskInstanceFactory.build(public_id="00000000"),)
)
async def test_task_instance_get_by_public_id(
    sqlalchemy_task_instance_repository: SqlAlchemyTaskInstanceRepository,
    task_instance: TaskInstance,
):
    await sqlalchemy_task_instance_repository.save(
        task_instance,
    )

    loaded = await sqlalchemy_task_instance_repository.get_by_public_id(
        task_instance.public_id,
    )

    assert loaded is not None
    assert loaded.id == task_instance.id
    assert loaded.title == task_instance.title
    assert loaded.description == task_instance.description


@pytest.mark.parametrize(
    ("original_task_instance", "duplicated_task_instance"),
    (
        (
            TaskInstanceFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                task_template_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
            ),
            TaskInstanceFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                task_template_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
            ),
        ),
    ),
)
async def test_duplicate_task_instance_error(
    sqlalchemy_task_instance_repository: SqlAlchemyTaskInstanceRepository,
    original_task_instance: TaskInstance,
    duplicated_task_instance: TaskInstance,
    session: AsyncSession,
):
    await sqlalchemy_task_instance_repository.save(
        original_task_instance,
    )

    with pytest.raises(IntegrityError):
        await sqlalchemy_task_instance_repository.save(
            duplicated_task_instance,
        )
        await session.flush()


async def test_get_task_instance_by_unknown_id_returns_none(
    sqlalchemy_task_instance_repository: SqlAlchemyTaskInstanceRepository,
):
    loaded = await sqlalchemy_task_instance_repository.get_by_id(
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
    sqlalchemy_task_instance_repository: SqlAlchemyTaskInstanceRepository,
    target_day: datetime.date,
    matching_task_instance: TaskInstance,
    other_task_instance: TaskInstance,
):

    await sqlalchemy_task_instance_repository.save(
        matching_task_instance,
    )

    await sqlalchemy_task_instance_repository.save(
        other_task_instance,
    )

    instances = await sqlalchemy_task_instance_repository.get_all_by_day(
        target_day,
    )

    assert len(instances) == 1
    assert next(iter(instances)).id == (matching_task_instance.id)


@pytest.mark.parametrize(
    "user_id",
    (
        uuid.UUID(
            "00000000-0000-0000-0000-000000000000",
        ),
    ),
)
@pytest.mark.parametrize("target_day", (datetime.date.fromisoformat("2026-05-30"),))
@pytest.mark.parametrize(
    "matching_task_instance",
    (
        TaskInstanceFactory.build(
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            occurrence_date=datetime.date.fromisoformat("2026-05-30"),
        ),
    ),
)
@pytest.mark.parametrize(
    "other_task_instance",
    (
        TaskInstanceFactory.build(
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
            occurrence_date=datetime.date.fromisoformat("2026-05-31"),
        ),
        TaskInstanceFactory.build(
            user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            occurrence_date=datetime.date.fromisoformat("2026-05-30"),
        ),
    ),
)
async def test_get_all_by_user_per_day(
    sqlalchemy_task_instance_repository: SqlAlchemyTaskInstanceRepository,
    user_id: uuid.UUID,
    target_day: datetime.date,
    matching_task_instance: TaskInstance,
    other_task_instance: TaskInstance,
):

    await sqlalchemy_task_instance_repository.save(
        matching_task_instance,
    )

    await sqlalchemy_task_instance_repository.save(
        other_task_instance,
    )

    instances = await sqlalchemy_task_instance_repository.get_all_by_user_per_day(
        user_id,
        target_day,
    )

    assert len(instances) == 1
    assert next(iter(instances)).id == (matching_task_instance.id)


@pytest.mark.parametrize(
    "now", (datetime.datetime.fromisoformat("2021-01-10T08:00:00"),)
)
@pytest.mark.parametrize(
    ("task_instance", "is_returned"),
    (
        # happy path
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
                status=TaskStatus.PENDING,
                reminded_at=None,
            ),
            True,
        ),
        # другой день
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-09"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
                status=TaskStatus.PENDING,
                reminded_at=None,
            ),
            False,
        ),
        # scheduled_at отсутствует
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=None,
                status=TaskStatus.PENDING,
                reminded_at=None,
            ),
            False,
        ),
        # scheduled_at позже now
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T09:00:00"),
                status=TaskStatus.PENDING,
                reminded_at=None,
            ),
            False,
        ),
        # scheduled_at раньше now
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T07:00:00"),
                status=TaskStatus.PENDING,
                reminded_at=None,
            ),
            True,
        ),
        # уже напомнили
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
                status=TaskStatus.PENDING,
                reminded_at=datetime.datetime.fromisoformat("2021-01-10T08:05:00"),
            ),
            False,
        ),
        # completed
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
                status=TaskStatus.COMPLETED,
                reminded_at=None,
            ),
            False,
        ),
        # cancelled
        (
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                scheduled_at=datetime.datetime.fromisoformat("2021-01-10T08:00:00"),
                status=TaskStatus.CANCELLED,
                reminded_at=None,
            ),
            False,
        ),
    ),
)
async def test_get_all_for_remind(
    sqlalchemy_task_instance_repository: SqlAlchemyTaskInstanceRepository,
    task_instance: TaskInstance,
    is_returned: bool,
    now: datetime.datetime,
):
    await sqlalchemy_task_instance_repository.save(task_instance)

    result = await sqlalchemy_task_instance_repository.get_all_for_remind(now)
    assert (
        task_instance.id in {task_instance.id for task_instance in result}
    ) == is_returned


@pytest.mark.parametrize(
    "now", (datetime.datetime.fromisoformat("2021-01-10T08:00:00"),)
)
@pytest.mark.parametrize(
    ("task_instance", "is_returned"),
    (
        (
            # Просроченная задача должна возвращаться
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-09"),
                status=TaskStatus.PENDING,
            ),
            True,
        ),
        (
            # Позавчерашняя задача возвращается
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-08"),
                status=TaskStatus.PENDING,
            ),
            True,
        ),
        (
            # Задача на текущую дату не возвращается
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                status=TaskStatus.PENDING,
            ),
            False,
        ),
        (
            # Задача в статусе отличном от pending не возвращается
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                status=TaskStatus.COMPLETED,
            ),
            False,
        ),
        (
            # Задача в статусе отличном от pending не возвращается
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                status=TaskStatus.MISSED,
            ),
            False,
        ),
        (
            # Задача в статусе отличном от pending не возвращается
            TaskInstanceFactory.build(
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
                status=TaskStatus.CANCELLED,
            ),
            False,
        ),
    ),
)
async def test_get_all_overdue(
    sqlalchemy_task_instance_repository: SqlAlchemyTaskInstanceRepository,
    task_instance: TaskInstance,
    now: datetime.datetime,
    is_returned: bool,
):
    await sqlalchemy_task_instance_repository.save(task_instance)

    result = await sqlalchemy_task_instance_repository.get_all_overdue(now=now)
    assert (
        task_instance.id in {task_instance.id for task_instance in result}
    ) == is_returned
