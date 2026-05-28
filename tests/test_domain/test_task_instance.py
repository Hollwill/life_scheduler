import datetime
import typing

import pytest

from domain.task_instance.aggregate import TaskInstance, TaskStatus
from domain.task_instance.exceptions import (
    TaskInstanceInvalidPostponeDateException,
    TaskInstanceInvalidStatusException,
    TaskInstanceNotScheduledException,
)
from domain.task_instance.service import TaskGenerationService
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.value_objects import Weekday
from tests.factories.task_instance import TaskInstanceFactory
from tests.factories.task_template import TaskTemplateFactory
from tests.factories.trigger import DailyTriggerFactory, WeeklyTriggerFactory


class TaskInstanceTestCase(typing.NamedTuple):
    title: str
    description: str


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


@pytest.mark.parametrize(
    "task_template",
    (
        TaskTemplateFactory.build(
            title="Template Title",
            description="Template Description",
            created_at=datetime.datetime.fromisoformat("2026-01-01T10:00:00"),
            trigger=DailyTriggerFactory.build(
                reminder_time=datetime.time.fromisoformat("12:00:00")
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    ("scheduled_day", "now", "expected_scheduled_at"),
    (
        (
            datetime.date.fromisoformat("2026-05-24"),
            datetime.datetime.fromisoformat("2026-05-24T08:00:00"),
            datetime.datetime.fromisoformat("2026-05-24T12:00:00"),
        ),
    ),
)
def test_generate_task_instance_from_template_success(
    task_template,
    scheduled_day: datetime.date,
    now: datetime.datetime,
    expected_scheduled_at: datetime.datetime,
):
    instance = TaskGenerationService.generate_from_template(
        template=task_template, scheduled_day=scheduled_day, now=now
    )
    assert instance.task_template_id == task_template.id
    assert instance.user_id == task_template.user_id
    assert instance.title == task_template.title
    assert instance.description == task_template.description
    assert instance.occurrence_date == scheduled_day
    assert instance.scheduled_at == expected_scheduled_at
    assert instance.created_at == now
    assert not instance.is_completed


@pytest.mark.parametrize(
    "task_template",
    (
        TaskTemplateFactory.build(
            trigger=WeeklyTriggerFactory.build(
                weekdays=frozenset([Weekday.MONDAY]),
            )
        ),
    ),
)
@pytest.mark.parametrize(
    ("scheduled_day", "creation_now"),
    (
        (
            datetime.date.fromisoformat("2026-05-24"),  # Sunday
            datetime.datetime.fromisoformat("2026-05-24T08:00:00"),
        ),
    ),
)
def test_generate_task_instance_from_template_not_scheduled(
    task_template, scheduled_day, creation_now
):
    with pytest.raises(TaskInstanceNotScheduledException):
        TaskGenerationService.generate_from_template(
            template=task_template, scheduled_day=scheduled_day, now=creation_now
        )


@pytest.mark.parametrize(
    "task_template",
    (
        TaskTemplateFactory.build(
            title="Template Title",
            trigger=DailyTriggerFactory.build(
                reminder_time=datetime.time.fromisoformat("12:00:00")
            ),
        ),
    ),
)
@pytest.mark.parametrize("new_title", ("New Title",))
@pytest.mark.parametrize(
    ("scheduled_day", "now"),
    (
        (
            datetime.date.fromisoformat("2026-05-24"),
            datetime.datetime.fromisoformat("2026-05-24T08:00:00"),
        ),
    ),
)
def test_generate_task_instance_independence(
    task_template: TaskTemplate,
    new_title: str,
    scheduled_day: datetime.date,
    now: datetime.datetime,
):

    instance = TaskGenerationService.generate_from_template(
        template=task_template, scheduled_day=scheduled_day, now=now
    )

    # Change template
    initial_title = task_template.title
    task_template.edit(title=new_title, now=datetime.datetime.now())

    assert instance.title == initial_title
    assert task_template.title == new_title
