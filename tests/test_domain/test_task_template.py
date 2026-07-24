import datetime
import uuid
from typing import NamedTuple

import pytest

from domain.common.aggregate_root import EMPTY, _Empty
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import (
    DailyTrigger,
    MonthlyTrigger,
    OneTimeTrigger,
    Trigger,
    WeeklyTrigger,
    YearlyTrigger,
)
from domain.task_template.exceptions import (
    EmptyWeekdaysException,
    InvalidDayOfMonthException,
    InvalidYearlyDateException,
)
from domain.task_template.value_objects import (
    DayOfMonth,
    Month,
    Weekday,
)
from domain.user.aggregate import User
from tests.factories.user import UserFactory


class OneTimeTriggerTestCase(NamedTuple):
    occurrence_date: datetime.date
    reminder_time: datetime.time | None
    check_day: datetime.date
    expected_occurs: bool
    expected_reminder: datetime.datetime | None


@pytest.mark.parametrize("user", (UserFactory.build(),))
@pytest.mark.parametrize(
    OneTimeTriggerTestCase._fields,
    [
        OneTimeTriggerTestCase(
            occurrence_date=datetime.date.fromisoformat("2026-05-19"),
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-19"),
            expected_occurs=True,
            expected_reminder=datetime.datetime.fromisoformat("2026-05-19T12:31:00"),
        ),
        OneTimeTriggerTestCase(
            occurrence_date=datetime.date.fromisoformat("2026-05-19"),
            reminder_time=None,
            check_day=datetime.date.fromisoformat("2026-05-19"),
            expected_occurs=True,
            expected_reminder=None,
        ),
        OneTimeTriggerTestCase(
            occurrence_date=datetime.date.fromisoformat("2026-05-19"),
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-20"),
            expected_occurs=False,
            expected_reminder=None,
        ),
    ],
)
def test_task_template(
    user: User,
    occurrence_date: datetime.date,
    reminder_time: datetime.time | None,
    check_day: datetime.date,
    expected_occurs: bool,
    expected_reminder: datetime.datetime | None,
):
    now = datetime.datetime.now()
    trigger = OneTimeTrigger(
        id=uuid.uuid4(),
        occurrence_date=occurrence_date,
        reminder_time=reminder_time,
    )

    task_template = TaskTemplate.create(
        user_id=user.id, title="test", description="test", trigger=trigger, now=now
    )

    assert task_template.occurs_on(check_day) == expected_occurs
    assert task_template.reminder_at(check_day) == expected_reminder


class EditTaskTemplateTestCase(NamedTuple):
    title: str | _Empty = EMPTY
    description: str | None | _Empty = EMPTY
    trigger: Trigger | _Empty = EMPTY

    expected_title: str = "old title"
    expected_description: str | None = "old description"
    expected_trigger_reminder_time: datetime.time | None = None

    expected_edit_time: datetime.datetime = datetime.datetime.fromisoformat(
        "2026-05-19T11:00"
    )


@pytest.mark.parametrize("user", (UserFactory.build(),))
@pytest.mark.parametrize(
    EditTaskTemplateTestCase._fields,
    [
        EditTaskTemplateTestCase(
            title="new title",
            expected_title="new title",
        ),
        EditTaskTemplateTestCase(
            description="new description",
            expected_description="new description",
        ),
        EditTaskTemplateTestCase(
            description=None,
            expected_description=None,
        ),
        EditTaskTemplateTestCase(
            trigger=DailyTrigger(
                id=uuid.uuid4(),
                reminder_time=datetime.time(12, 0),
            ),
            expected_trigger_reminder_time=datetime.time(12, 0),
        ),
        EditTaskTemplateTestCase(
            expected_edit_time=datetime.datetime.fromisoformat("2026-05-19T10:00"),
        ),
    ],
)
@pytest.mark.parametrize("now", (datetime.datetime.fromisoformat("2026-05-19T10:00"),))
def test_task_template_edit(
    user: User,
    title: str | _Empty,
    description: str | None | _Empty,
    trigger: Trigger | _Empty,
    expected_title: str,
    expected_description: str | None,
    expected_trigger_reminder_time: datetime.time | None,
    expected_edit_time: datetime.datetime,
    now: datetime.datetime,
):

    task_template = TaskTemplate.create(
        user_id=user.id,
        title="old title",
        description="old description",
        trigger=DailyTrigger(
            id=uuid.uuid4(),
            reminder_time=None,
        ),
        now=now,
    )

    edit_time = now + datetime.timedelta(hours=1)

    task_template.edit(
        title=title,
        description=description,
        trigger=trigger,
        now=edit_time,
    )

    assert task_template.title == expected_title
    assert task_template.description == expected_description
    assert isinstance(task_template.trigger, DailyTrigger)
    assert task_template.trigger.reminder_time == expected_trigger_reminder_time
    assert task_template.updated_at == expected_edit_time


@pytest.mark.parametrize(
    OneTimeTriggerTestCase._fields,
    [
        OneTimeTriggerTestCase(
            occurrence_date=datetime.date.fromisoformat("2026-05-19"),
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-19"),
            expected_occurs=True,
            expected_reminder=datetime.datetime.fromisoformat("2026-05-19T12:31:00"),
        ),
        OneTimeTriggerTestCase(
            occurrence_date=datetime.date.fromisoformat("2026-05-19"),
            reminder_time=None,
            check_day=datetime.date.fromisoformat("2026-05-19"),
            expected_occurs=True,
            expected_reminder=None,
        ),
        OneTimeTriggerTestCase(
            occurrence_date=datetime.date.fromisoformat("2026-05-19"),
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-20"),
            expected_occurs=False,
            expected_reminder=None,
        ),
    ],
)
def test_one_time_trigger(
    occurrence_date: datetime.date,
    reminder_time: datetime.time | None,
    check_day: datetime.date,
    expected_occurs: bool,
    expected_reminder: datetime.datetime | None,
):
    trigger = OneTimeTrigger(
        id=uuid.uuid4(),
        occurrence_date=occurrence_date,
        reminder_time=reminder_time,
    )
    assert trigger.occurs_on(check_day) == expected_occurs
    assert trigger.reminder_at(check_day) == expected_reminder


class DailyTriggerTestCase(NamedTuple):
    reminder_time: datetime.time | None
    check_day: datetime.date
    expected_occurs: bool
    expected_reminder: datetime.datetime | None


@pytest.mark.parametrize(
    DailyTriggerTestCase._fields,
    [
        DailyTriggerTestCase(
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-18"),
            expected_occurs=True,
            expected_reminder=datetime.datetime.fromisoformat("2026-05-18T12:31:00"),
        ),
        DailyTriggerTestCase(
            reminder_time=None,
            check_day=datetime.date.fromisoformat("2026-05-18"),
            expected_occurs=True,
            expected_reminder=None,
        ),
    ],
)
def test_daily_trigger(
    reminder_time: datetime.time | None,
    check_day: datetime.date,
    expected_occurs: bool,
    expected_reminder: datetime.datetime | None,
):
    trigger = DailyTrigger(id=uuid.uuid4(), reminder_time=reminder_time)
    assert trigger.occurs_on(check_day) == expected_occurs
    assert trigger.reminder_at(check_day) == expected_reminder


class WeeklyTriggerTestCase(NamedTuple):
    weekdays: frozenset[Weekday]
    reminder_time: datetime.time | None
    check_day: datetime.date
    expected_occurs: bool
    expected_reminder: datetime.datetime | None


@pytest.mark.parametrize(
    WeeklyTriggerTestCase._fields,
    [
        WeeklyTriggerTestCase(
            weekdays=frozenset({Weekday.TUESDAY}),
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-19"),  # Вторник
            expected_occurs=True,
            expected_reminder=datetime.datetime.fromisoformat("2026-05-19T12:31:00"),
        ),
        WeeklyTriggerTestCase(
            weekdays=frozenset({Weekday.TUESDAY}),
            reminder_time=None,
            check_day=datetime.date.fromisoformat("2026-05-19"),  # Вторник
            expected_occurs=True,
            expected_reminder=None,
        ),
        WeeklyTriggerTestCase(
            weekdays=frozenset({Weekday.WEDNESDAY}),
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-19"),  # Вторник
            expected_occurs=False,
            expected_reminder=None,
        ),
        WeeklyTriggerTestCase(
            weekdays=frozenset({Weekday.MONDAY, Weekday.FRIDAY}),
            reminder_time=datetime.time.fromisoformat("10:00:00"),
            check_day=datetime.date.fromisoformat("2026-05-22"),  # Пятница
            expected_occurs=True,
            expected_reminder=datetime.datetime.fromisoformat("2026-05-22T10:00:00"),
        ),
    ],
)
def test_weekly_trigger(
    weekdays: frozenset[Weekday],
    reminder_time: datetime.time | None,
    check_day: datetime.date,
    expected_occurs: bool,
    expected_reminder: datetime.datetime | None,
):
    trigger = WeeklyTrigger(
        id=uuid.uuid4(), weekdays=weekdays, reminder_time=reminder_time
    )
    assert trigger.occurs_on(check_day) == expected_occurs
    assert trigger.reminder_at(check_day) == expected_reminder


class MonthlyTriggerTestCase(NamedTuple):
    day_of_month: int
    reminder_time: datetime.time | None
    check_day: datetime.date
    expected_occurs: bool
    expected_reminder: datetime.datetime | None


@pytest.mark.parametrize(
    MonthlyTriggerTestCase._fields,
    [
        MonthlyTriggerTestCase(
            day_of_month=19,
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-19"),
            expected_occurs=True,
            expected_reminder=datetime.datetime.fromisoformat("2026-05-19T12:31:00"),
        ),
        MonthlyTriggerTestCase(
            day_of_month=19,
            reminder_time=None,
            check_day=datetime.date.fromisoformat("2026-05-19"),
            expected_occurs=True,
            expected_reminder=None,
        ),
        MonthlyTriggerTestCase(
            day_of_month=19,
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-20"),
            expected_occurs=False,
            expected_reminder=None,
        ),
    ],
)
def test_monthly_trigger(
    day_of_month: int,
    reminder_time: datetime.time | None,
    check_day: datetime.date,
    expected_occurs: bool,
    expected_reminder: datetime.datetime | None,
):
    trigger = MonthlyTrigger(
        id=uuid.uuid4(),
        day_of_month=DayOfMonth(day_of_month),
        reminder_time=reminder_time,
    )
    assert trigger.occurs_on(check_day) == expected_occurs
    assert trigger.reminder_at(check_day) == expected_reminder


class YearlyTriggerTestCase(NamedTuple):
    month: Month
    day: int
    reminder_time: datetime.time | None
    check_day: datetime.date
    expected_occurs: bool
    expected_reminder: datetime.datetime | None


@pytest.mark.parametrize(
    YearlyTriggerTestCase._fields,
    [
        YearlyTriggerTestCase(
            month=Month.MAY,
            day=19,
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-19"),
            expected_occurs=True,
            expected_reminder=datetime.datetime.fromisoformat("2026-05-19T12:31:00"),
        ),
        YearlyTriggerTestCase(
            month=Month.MAY,
            day=19,
            reminder_time=datetime.time.fromisoformat("12:31:00"),
            check_day=datetime.date.fromisoformat("2026-05-20"),
            expected_occurs=False,
            expected_reminder=None,
        ),
        YearlyTriggerTestCase(
            month=Month.JUNE,
            day=1,
            reminder_time=None,
            check_day=datetime.date.fromisoformat("2026-06-01"),
            expected_occurs=True,
            expected_reminder=None,
        ),
    ],
)
def test_yearly_trigger(
    month: Month,
    day: int,
    reminder_time: datetime.time | None,
    check_day: datetime.date,
    expected_occurs: bool,
    expected_reminder: datetime.datetime | None,
):
    trigger = YearlyTrigger(
        id=uuid.uuid4(),
        month=month,
        day=DayOfMonth(day),
        reminder_time=reminder_time,
    )
    assert trigger.occurs_on(check_day) == expected_occurs
    assert trigger.reminder_at(check_day) == expected_reminder


def test_monthly_trigger_invalid_day():
    with pytest.raises(
        InvalidDayOfMonthException,
        match="Day of month must be between 1 and 31, but got 32",
    ):
        DayOfMonth(32)
    with pytest.raises(
        InvalidDayOfMonthException,
        match="Day of month must be between 1 and 31, but got 0",
    ):
        DayOfMonth(0)


def test_yearly_trigger_invalid_day():
    # Validation is now inside DayOfMonth
    with pytest.raises(
        InvalidDayOfMonthException,
        match="Day of month must be between 1 and 31, but got 32",
    ):
        DayOfMonth(32)


@pytest.mark.parametrize(
    "month, day",
    [
        (Month.FEBRUARY, 30),
        (Month.FEBRUARY, 31),
        (Month.APRIL, 31),
        (Month.JUNE, 31),
        (Month.SEPTEMBER, 31),
        (Month.NOVEMBER, 31),
    ],
)
def test_yearly_trigger_impossible_date(month: Month, day: int):
    with pytest.raises(
        InvalidYearlyDateException,
        match=f"Invalid date for YearlyTrigger: month {int(month)}, day {day}",
    ):
        YearlyTrigger(id=uuid.uuid4(), month=month, day=DayOfMonth(day))


def test_yearly_trigger_feb_29_is_valid():
    # Should NOT raise for Feb 29 (leap year support)
    YearlyTrigger(id=uuid.uuid4(), month=Month.FEBRUARY, day=DayOfMonth(29))


def test_weekly_trigger_empty_weekdays():
    with pytest.raises(
        EmptyWeekdaysException,
        match="At least one weekday must be specified for WeeklyTrigger",
    ):
        WeeklyTrigger(id=uuid.uuid4(), weekdays=frozenset())
