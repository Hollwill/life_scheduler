import datetime
import typing

import pytest

from domain.task_instance.aggregate import TaskInstance, TaskStatus
from domain.task_instance.events import TaskReminderRequested
from domain.task_instance.exceptions import (
    TaskInstanceInvalidPostponeDateException,
    TaskInstanceInvalidReminderDateException,
    TaskInstanceInvalidStatusException,
    TaskInstanceReminderTimeNotComeYet,
)
from domain.task_template.aggregate import TaskTemplate
from tests.factories.task_instance import TaskInstanceFactory
from tests.factories.task_template import TaskTemplateFactory


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


# @pytest.mark.parametrize(
#     "task_template",
#     (
#         TaskTemplateFactory.build(
#             title="Template Title",
#             description="Template Description",
#             created_at=datetime.datetime.fromisoformat("2026-01-01T10:00:00"),
#             trigger=DailyTriggerFactory.build(
#                 reminder_time=datetime.time.fromisoformat("12:00:00")
#             ),
#         ),
#     ),
# )
# @pytest.mark.parametrize(
#     ("generate_day", "now", "expected_scheduled_at"),
#     (
#         (
#             datetime.date.fromisoformat("2026-05-24"),
#             datetime.datetime.fromisoformat("2026-05-24T08:00:00"),
#             datetime.datetime.fromisoformat("2026-05-24T12:00:00"),
#         ),
#     ),
# )
# def test_generate_task_instance_from_template_success(
#     task_template,
#     generate_day: datetime.date,
#     now: datetime.datetime,
#     expected_scheduled_at: datetime.datetime,
# ):
#     instance = TaskGenerationService.generate_from_template(
#         template=task_template, day=generate_day, now=now
#     )
#     assert instance.task_template_id == task_template.id
#     assert instance.user_id == task_template.user_id
#     assert instance.title == task_template.title
#     assert instance.description == task_template.description
#     assert instance.occurrence_date == generate_day
#     assert instance.scheduled_at == expected_scheduled_at
#     assert instance.created_at == now
#     assert not instance.is_completed


# @pytest.mark.parametrize(
#     "task_template",
#     (
#         TaskTemplateFactory.build(
#             trigger=WeeklyTriggerFactory.build(
#                 weekdays=frozenset([Weekday.MONDAY]),
#             )
#         ),
#     ),
# )
# @pytest.mark.parametrize(
#     ("generate_day", "creation_now"),
#     (
#         (
#             datetime.date.fromisoformat("2026-05-24"),  # Sunday
#             datetime.datetime.fromisoformat("2026-05-24T08:00:00"),
#         ),
#     ),
# )
# def test_generate_task_instance_from_template_not_scheduled(
#     task_template, generate_day: datetime.date, creation_now: datetime.datetime
# ):
#     task_instance = TaskGenerationService.generate_from_template(
#         template=task_template, day=generate_day, now=creation_now
#     )
#     assert task_instance is None


# @pytest.mark.parametrize(
#     "task_template",
#     (
#         TaskTemplateFactory.build(
#             title="Template Title",
#             trigger=DailyTriggerFactory.build(
#                 reminder_time=datetime.time.fromisoformat("12:00:00")
#             ),
#         ),
#     ),
# )
# @pytest.mark.parametrize("new_title", ("New Title",))
# @pytest.mark.parametrize(
#     ("generate_day", "now"),
#     (
#         (
#             datetime.date.fromisoformat("2026-05-24"),
#             datetime.datetime.fromisoformat("2026-05-24T08:00:00"),
#         ),
#     ),
# )
# def test_generate_task_instance_independence(
#     task_template: TaskTemplate,
#     new_title: str,
#     generate_day: datetime.date,
#     now: datetime.datetime,
# ):
#
#     instance = TaskGenerationService.generate_from_template(
#         template=task_template, day=generate_day, now=now
#     )
#
#     # Change template
#     initial_title = task_template.title
#     task_template.edit(title=new_title, now=datetime.datetime.now())
#
#     assert instance.title == initial_title
#     assert task_template.title == new_title


@pytest.mark.parametrize(
    "task_template",
    (TaskTemplateFactory.build(),),
)
@pytest.mark.parametrize(
    ("updated_field", "new_value", "check_attribute", "non_changed_attributes"),
    (
        (
            "title",
            "new_title",
            "title",
            ("description", "trigger"),
        ),
        (
            "description",
            "new_description",
            "description",
            ("title", "trigger"),
        ),
    ),
)
def test_task_template_edit(
    task_template: TaskTemplate,
    updated_field: str,
    new_value: typing.Any,
    check_attribute: str,
    non_changed_attributes: tuple[str, ...],
    now: datetime.datetime,
):
    original_values = {
        attr: getattr(task_template, attr)
        for attr in (check_attribute, *non_changed_attributes)
    }

    task_template.edit(**{updated_field: new_value}, now=now)

    assert getattr(task_template, check_attribute) == new_value

    for attr in non_changed_attributes:
        assert getattr(task_template, attr) == original_values[attr]


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
    assert len(events) == 1

    event = events[0]

    assert isinstance(event, TaskReminderRequested)
    assert event.task_instance_id == str(task_instance.id)


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
