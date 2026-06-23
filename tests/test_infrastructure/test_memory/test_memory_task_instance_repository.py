import datetime
import uuid

import pytest

from domain.task_instance.aggregate import TaskInstance, TaskStatus
from infrastructure.memory.repositories import (
    MemoryTaskInstanceRepository,
)
from tests.factories.task_instance import TaskInstanceFactory


@pytest.mark.parametrize("task_instance", (TaskInstanceFactory.build(),))
async def test_memory_task_instance_repository_save_and_get(
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    task_instance: TaskInstance,
):

    await memory_task_instance_repository.save(task_instance)
    retrieved = await memory_task_instance_repository.get_by_id(task_instance.id)

    assert retrieved is not None
    assert retrieved.id == task_instance.id
    assert retrieved.title == task_instance.title
    assert retrieved is not task_instance  # Deepcopy check


async def test_memory_task_instance_repository_get_none(
    memory_task_instance_repository: MemoryTaskInstanceRepository,
):
    retrieved = await memory_task_instance_repository.get_by_id(uuid.uuid4())
    assert retrieved is None


@pytest.mark.parametrize("task_instance", (TaskInstanceFactory.build(),))
@pytest.mark.parametrize(
    "title_to_change",
    [
        "Changed Title",
    ],
)
async def test_memory_task_instance_repository_deepcopy_isolation(
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    task_instance: TaskInstance,
    title_to_change: str,
):
    task_instance_title = task_instance.title

    await memory_task_instance_repository.save(task_instance)

    # Change original object
    task_instance.title = title_to_change

    # Check that repo still has the original data
    retrieved = await memory_task_instance_repository.get_by_id(task_instance.id)
    assert retrieved.title == task_instance_title

    # Change retrieved object
    retrieved.title = title_to_change

    # Check that repo still has the original data
    retrieved_again = await memory_task_instance_repository.get_by_id(task_instance.id)
    assert retrieved_again.title == task_instance_title


@pytest.mark.parametrize(
    "task_instances",
    (
        (
            TaskInstanceFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
            ),
            TaskInstanceFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                occurrence_date=datetime.date.fromisoformat("2021-01-10"),
            ),
            TaskInstanceFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
                occurrence_date=datetime.date.fromisoformat("2021-01-11"),
            ),
            TaskInstanceFactory.build(
                id=uuid.UUID("00000000-0000-0000-0000-000000000003"),
                occurrence_date=datetime.date.fromisoformat("2021-01-09"),
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    "expected_ids_in_result",
    (
        (
            uuid.UUID("00000000-0000-0000-0000-000000000000"),
            uuid.UUID("00000000-0000-0000-0000-000000000001"),
        ),
    ),
)
@pytest.mark.parametrize("search_by_day", (datetime.date.fromisoformat("2021-01-10"),))
async def test_memory_task_instance_get_all_by_day(
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    task_instances: tuple[TaskInstance, ...],
    expected_ids_in_result: tuple[str, ...],
    search_by_day: datetime.date,
):
    for task_instance in task_instances:
        await memory_task_instance_repository.save(task_instance)

    result = await memory_task_instance_repository.get_all_by_day(day=search_by_day)

    ids_in_result = {task_instance.id for task_instance in result}
    assert ids_in_result == set(expected_ids_in_result)


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
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    task_instance: TaskInstance,
    is_returned: bool,
    now: datetime.datetime,
):
    await memory_task_instance_repository.save(task_instance)

    result = await memory_task_instance_repository.get_all_for_remind(now)
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
    memory_task_instance_repository: MemoryTaskInstanceRepository,
    task_instance: TaskInstance,
    now: datetime.datetime,
    is_returned: bool,
):
    await memory_task_instance_repository.save(task_instance)

    result = await memory_task_instance_repository.get_all_overdue(now=now)
    assert (
        task_instance.id in {task_instance.id for task_instance in result}
    ) == is_returned
