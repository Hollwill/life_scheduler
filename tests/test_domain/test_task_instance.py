import datetime
import typing
import uuid

import pytest

from domain.task_instance.aggregate import TaskInstance
from domain.task_instance.exceptions import TaskInstanceNotScheduledException
from domain.task_instance.service import TaskInstanceService
from domain.task_template.value_objects import TriggerType, Weekday


@pytest.mark.parametrize(
    "initial_data, completion_offset",
    [
        (
            {
                "title": "Test Task",
                "description": "Test Description",
            },
            datetime.timedelta(minutes=5),
        ),
    ],
)
def test_task_instance_completion(initial_data, completion_offset):
    now = datetime.datetime.now()
    instance = TaskInstance.create(
        task_template_id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title=initial_data["title"],
        description=initial_data["description"],
        occurrence_date=now.date(),
        scheduled_at=now,
        now=now,
    )

    assert not instance.is_completed
    assert instance.completed_at is None

    completion_time = now + completion_offset
    instance.complete(completion_time)

    assert instance.is_completed
    assert instance.completed_at == completion_time


class TaskInstanceServiceSuccessTestCase(typing.NamedTuple):
    task_template_title: str
    task_template_description: str
    task_template_created_at: datetime.datetime
    scheduled_day: datetime.date
    creation_now: datetime.datetime
    expected_scheduled_at: datetime.datetime


@pytest.mark.parametrize(
    "trigger",
    (
        {
            "type": TriggerType.DAILY,
            "reminder_time": datetime.time.fromisoformat("12:00:00"),
        },
    ),
    indirect=True,
)
@pytest.mark.parametrize(
    TaskInstanceServiceSuccessTestCase._fields,
    [
        TaskInstanceServiceSuccessTestCase(
            task_template_title="Template Title",
            task_template_description="Template Description",
            task_template_created_at=datetime.datetime.fromisoformat(
                "2026-01-01T10:00:00"
            ),
            scheduled_day=datetime.date.fromisoformat("2026-05-24"),
            creation_now=datetime.datetime.fromisoformat("2026-05-24T08:00:00"),
            expected_scheduled_at=datetime.datetime.fromisoformat(
                "2026-05-24T12:00:00"
            ),
        ),
    ],
)
def test_create_task_instance_from_template_success(
    task_template,
    task_template_title: str,
    task_template_description: str,
    task_template_created_at: datetime.datetime,
    scheduled_day: datetime.date,
    creation_now: datetime.datetime,
    expected_scheduled_at: datetime.datetime,
):
    instance = TaskInstanceService.create_from_template(
        template=task_template, scheduled_day=scheduled_day, now=creation_now
    )
    assert instance.task_template_id == task_template.id
    assert instance.user_id == task_template.user_id
    assert instance.title == task_template.title
    assert instance.description == task_template.description
    assert instance.occurrence_date == scheduled_day
    assert instance.scheduled_at == expected_scheduled_at
    assert instance.created_at == creation_now
    assert not instance.is_completed


@pytest.mark.parametrize(
    "trigger",
    (
        {
            "type": TriggerType.WEEKLY,
            "weekdays": frozenset([Weekday.MONDAY]),
        },
    ),
    indirect=True,
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
def test_create_task_instance_from_template_not_scheduled(
    task_template, scheduled_day, creation_now
):
    with pytest.raises(TaskInstanceNotScheduledException):
        TaskInstanceService.create_from_template(
            template=task_template, scheduled_day=scheduled_day, now=creation_now
        )


@pytest.mark.parametrize(
    "trigger",
    (
        {
            "type": TriggerType.DAILY,
            "reminder_time": datetime.time.fromisoformat("12:00:00"),
        },
    ),
    indirect=True,
)
@pytest.mark.parametrize(
    ("task_template_title", "new_title"),
    (
        (
            "Original Title",
            "New Title",
        ),
    ),
)
def test_create_task_instance_independence(task_template, new_title):
    scheduled_day = datetime.date.fromisoformat("2026-05-24")
    creation_now = datetime.datetime.fromisoformat("2026-05-24T08:00:00")

    instance = TaskInstanceService.create_from_template(
        template=task_template, scheduled_day=scheduled_day, now=creation_now
    )

    # Change template
    initial_title = task_template.title
    task_template.edit(title=new_title, now=datetime.datetime.now())

    assert instance.title == initial_title
    assert task_template.title == new_title
