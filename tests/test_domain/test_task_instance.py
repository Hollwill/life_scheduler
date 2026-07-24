import datetime
import uuid
from typing import NamedTuple

import pytest

from domain.common.aggregate_root import EMPTY, _Empty
from domain.task_instance.aggregate import TaskInstance, TaskStatus
from domain.task_instance.exceptions import (
    TaskInstanceInvalidPostponeDateException,
    TaskInstanceInvalidReminderDateException,
    TaskInstanceInvalidStatusException,
    TaskInstanceReminderTimeNotComeYet,
)
from tests.factories.task_instance import TaskInstanceFactory


@pytest.mark.parametrize(
    (
        "task_template_id",
        "user_id",
        "title",
        "description",
        "occurrence_date",
        "scheduled_at",
    ),
    (
        (
            uuid.uuid4(),
            uuid.uuid4(),
            "task title",
            "task description",
            datetime.date(2026, 7, 25),
            datetime.datetime(2026, 7, 25, 19, 0),
        ),
        (
            None,
            uuid.uuid4(),
            "one time task",
            None,
            datetime.date(2026, 7, 26),
            None,
        ),
    ),
)
def test_task_instance_create(
    task_template_id: uuid.UUID | None,
    user_id: uuid.UUID,
    title: str,
    description: str | None,
    occurrence_date: datetime.date,
    scheduled_at: datetime.datetime | None,
    now: datetime.datetime,
):
    task_instance = TaskInstance.create(
        task_template_id=task_template_id,
        user_id=user_id,
        title=title,
        description=description,
        occurrence_date=occurrence_date,
        scheduled_at=scheduled_at,
        now=now,
    )

    assert task_instance.task_template_id == task_template_id
    assert task_instance.user_id == user_id
    assert task_instance.title == title
    assert task_instance.description == description
    assert task_instance.occurrence_date == occurrence_date
    assert task_instance.scheduled_at == scheduled_at

    assert task_instance.created_at == now
    assert task_instance.status == TaskStatus.PENDING
    assert task_instance.postpone_reason is None
    assert task_instance.reminded_at is None

    assert task_instance.id is not None
    assert task_instance.public_id is not None


class EditTaskInstanceTestCase(NamedTuple):
    title: str | _Empty = EMPTY
    description: str | None | _Empty = EMPTY
    occurrence_date: datetime.date | _Empty = EMPTY
    scheduled_at: datetime.datetime | None | _Empty = EMPTY

    expected_title: str = "old title"
    expected_description: str | None = "old description"
    expected_occurrence_date: datetime.date = datetime.date(2026, 5, 19)
    expected_scheduled_at: datetime.datetime | None = datetime.datetime.fromisoformat(
        "2026-05-19T11:00"
    )


@pytest.mark.parametrize(
    EditTaskInstanceTestCase._fields,
    [
        EditTaskInstanceTestCase(
            title="new title",
            expected_title="new title",
        ),
        EditTaskInstanceTestCase(
            description="new description",
            expected_description="new description",
        ),
        EditTaskInstanceTestCase(
            description=None,
            expected_description=None,
        ),
        EditTaskInstanceTestCase(
            occurrence_date=datetime.date(2026, 5, 20),
            expected_occurrence_date=datetime.date(2026, 5, 20),
        ),
        EditTaskInstanceTestCase(
            scheduled_at=datetime.datetime.fromisoformat("2026-05-19T15:00"),
            expected_scheduled_at=datetime.datetime.fromisoformat("2026-05-19T15:00"),
        ),
        EditTaskInstanceTestCase(
            scheduled_at=None,
            expected_scheduled_at=None,
        ),
    ],
)
def test_task_instance_edit(
    title: str | _Empty,
    description: str | None | _Empty,
    occurrence_date: datetime.date | _Empty,
    scheduled_at: datetime.datetime | None | _Empty,
    expected_title: str,
    expected_description: str | None,
    expected_occurrence_date: datetime.date,
    expected_scheduled_at: datetime.datetime | None,
):
    task_instance = TaskInstance.create(
        task_template_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="old title",
        description="old description",
        occurrence_date=datetime.date(2026, 5, 19),
        scheduled_at=datetime.datetime.fromisoformat("2026-05-19T11:00"),
        now=datetime.datetime.fromisoformat("2026-05-19T10:00"),
    )

    task_instance.edit(
        title=title,
        description=description,
        occurrence_date=occurrence_date,
        scheduled_at=scheduled_at,
    )

    assert task_instance.title == expected_title
    assert task_instance.description == expected_description
    assert task_instance.occurrence_date == expected_occurrence_date
    assert task_instance.scheduled_at == expected_scheduled_at


@pytest.mark.parametrize(
    "task_instance", (TaskInstanceFactory.build(status=TaskStatus.PENDING),)
)
def test_task_instance_completion(
    task_instance: TaskInstance,
):

    assert not task_instance.is_completed

    task_instance.complete()

    assert task_instance.is_completed
    assert task_instance.status == TaskStatus.COMPLETED


@pytest.mark.parametrize(
    "task_instance", (TaskInstanceFactory.build(status=TaskStatus.PENDING),)
)
def test_task_instance_miss(
    task_instance: TaskInstance,
):

    task_instance.miss()

    assert task_instance.status == TaskStatus.MISSED


@pytest.mark.parametrize(
    "task_instance_status",
    (TaskStatus.CANCELLED, TaskStatus.COMPLETED, TaskStatus.MISSED),
)
def test_task_instance_miss_invalid_status_transition(
    task_instance_status: TaskStatus,
):
    task_instance = TaskInstanceFactory.build(status=task_instance_status)

    with pytest.raises(TaskInstanceInvalidStatusException):
        task_instance.miss()


@pytest.mark.parametrize(
    "task_instance", (TaskInstanceFactory.build(status=TaskStatus.PENDING),)
)
def test_task_instance_cancellation(task_instance: TaskInstance):

    task_instance.cancel()

    assert not task_instance.is_completed
    assert task_instance.status == TaskStatus.CANCELLED


@pytest.mark.parametrize(
    "task_instance", (TaskInstanceFactory.build(status=TaskStatus.PENDING),)
)
def test_task_instance_invalid_completion_transition(task_instance: TaskInstance):

    task_instance.cancel()

    with pytest.raises(TaskInstanceInvalidStatusException):
        task_instance.complete()


@pytest.mark.parametrize(
    "task_instance", (TaskInstanceFactory.build(status=TaskStatus.PENDING),)
)
def test_task_instance_invalid_cancellation_transition(task_instance: TaskInstance):

    task_instance.complete()

    with pytest.raises(TaskInstanceInvalidStatusException):
        task_instance.cancel()


@pytest.mark.parametrize(
    "task_instance", (TaskInstanceFactory.build(status=TaskStatus.PENDING),)
)
def test_task_instance_postpone_success(
    task_instance: TaskInstance,
    now: datetime.datetime,
):
    task_instance_occurrence_date = task_instance.occurrence_date

    new_date = task_instance_occurrence_date + datetime.timedelta(days=1)
    task_instance.postpone(new_occurrence_date=new_date, now=now, reason="Too busy")

    assert task_instance.occurrence_date == new_date
    assert task_instance.status == TaskStatus.PENDING


@pytest.mark.parametrize(
    "task_instance", (TaskInstanceFactory.build(status=TaskStatus.PENDING),)
)
def test_task_instance_postpone_invalid_transition(task_instance: TaskInstance, now):

    task_instance.complete()

    with pytest.raises(TaskInstanceInvalidStatusException):
        task_instance.postpone(
            new_occurrence_date=now.date() + datetime.timedelta(days=1), now=now
        )


@pytest.mark.parametrize(
    "task_instance", (TaskInstanceFactory.build(status=TaskStatus.PENDING),)
)
@pytest.mark.parametrize(
    "postpone_offset", (datetime.timedelta(days=0), datetime.timedelta(days=-1))
)
def test_task_instance_postpone_invalid_date(
    task_instance: TaskInstance,
    now: datetime.datetime,
    postpone_offset: datetime.timedelta,
):

    with pytest.raises(TaskInstanceInvalidPostponeDateException):
        task_instance.postpone(
            new_occurrence_date=now.date() + postpone_offset, now=now
        )


def test_task_instance_mark_reminded(
    now: datetime.datetime,
):
    task_instance: TaskInstance = TaskInstanceFactory.build(
        status=TaskStatus.PENDING,
        occurrence_date=now.date(),
        scheduled_at=now - datetime.timedelta(minutes=1),
        reminded_at=None,
    )

    task_instance.mark_reminded(now)

    assert task_instance.reminded_at == now

    events = task_instance.flush_events()
    assert len(events) == 0


def test_task_instance_mark_reminded_skips_if_scheduled_at_is_none(
    now: datetime.datetime,
):
    task_instance: TaskInstance = TaskInstanceFactory.build(
        status=TaskStatus.PENDING,
        occurrence_date=now.date(),
        scheduled_at=None,
        reminded_at=None,
    )

    task_instance.mark_reminded(now)

    assert task_instance.reminded_at is None
    assert task_instance.flush_events() == []


def test_task_instance_mark_reminded_skips_if_already_reminded(
    now: datetime.datetime,
):
    reminded_at = now - datetime.timedelta(hours=1)

    task_instance: TaskInstance = TaskInstanceFactory.build(
        status=TaskStatus.PENDING,
        occurrence_date=now.date(),
        scheduled_at=now - datetime.timedelta(minutes=1),
        reminded_at=reminded_at,
    )

    task_instance.mark_reminded(now)

    assert task_instance.reminded_at == reminded_at
    assert len(task_instance.flush_events()) == 0


@pytest.mark.parametrize(
    "status",
    (
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED,
    ),
)
def test_task_instance_mark_reminded_invalid_status(
    status: TaskStatus,
    now: datetime.datetime,
):
    task_instance: TaskInstance = TaskInstanceFactory.build(
        status=status,
        occurrence_date=now.date(),
        scheduled_at=now - datetime.timedelta(minutes=1),
        reminded_at=None,
    )

    with pytest.raises(TaskInstanceInvalidStatusException):
        task_instance.mark_reminded(now)


def test_task_instance_mark_reminded_invalid_date(
    now: datetime.datetime,
):
    task_instance: TaskInstance = TaskInstanceFactory.build(
        status=TaskStatus.PENDING,
        occurrence_date=now.date() + datetime.timedelta(days=1),
        scheduled_at=now - datetime.timedelta(minutes=1),
        reminded_at=None,
    )

    with pytest.raises(TaskInstanceInvalidReminderDateException):
        task_instance.mark_reminded(now)


def test_task_instance_mark_reminded_time_not_come_yet(
    now: datetime.datetime,
):
    task_instance: TaskInstance = TaskInstanceFactory.build(
        status=TaskStatus.PENDING,
        occurrence_date=now.date(),
        scheduled_at=now + datetime.timedelta(minutes=1),
        reminded_at=None,
    )

    with pytest.raises(TaskInstanceReminderTimeNotComeYet):
        task_instance.mark_reminded(now)
