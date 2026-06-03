import datetime
import uuid

import pytest

from application.task_template.commands import CreateTaskTemplateCommand
from application.task_template.schemas import (
    DailyTriggerPayload,
    MonthlyTriggerPayload,
    OneTimeTriggerPayload,
    WeeklyTriggerPayload,
    YearlyTriggerPayload,
)
from presentation.telegram.exceptions import ParseError
from presentation.telegram.parsers import (
    parse_create_daily,
    parse_create_monthly,
    parse_create_one_time,
    parse_create_weekly,
    parse_create_yearly,
)


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
@pytest.mark.parametrize(
    ("command_raw", "expected_command"),
    (
        (
            # Full command case
            "09:00 Drink water | Just because",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because",
                trigger_payload=DailyTriggerPayload(
                    type="DAILY", reminder_time=datetime.time.fromisoformat("09:00")
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            # many spaces  between and inside of arguments case
            "09:00       Drink  water     |    Just  because     ",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink  water",
                description="Just  because",
                trigger_payload=DailyTriggerPayload(
                    type="DAILY", reminder_time=datetime.time.fromisoformat("09:00")
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            # description with split case
            "09:00 Drink water| Just because| with dot in description",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because| with dot in description",
                trigger_payload=DailyTriggerPayload(
                    type="DAILY", reminder_time=datetime.time.fromisoformat("09:00")
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            # no reminder time case
            "Drink water| Just because",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because",
                trigger_payload=DailyTriggerPayload(type="DAILY", reminder_time=None),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            # only title case
            "Drink",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink",
                description=None,
                trigger_payload=DailyTriggerPayload(type="DAILY", reminder_time=None),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
    ),
)
@pytest.mark.parametrize("now", (datetime.datetime.fromisoformat("2021-01-10"),))
def test_parse_create_daily(
    user_id: uuid.UUID,
    command_raw: str,
    expected_command: CreateTaskTemplateCommand,
    now: datetime.datetime,
):
    result_command = parse_create_daily(
        user_id=user_id, command_raw=command_raw, now=now
    )

    assert result_command == expected_command


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
@pytest.mark.parametrize(
    "command_raw",
    ("", "09:00", "09:99 Drink", "09:00 |"),
)
@pytest.mark.parametrize("now", (datetime.datetime.fromisoformat("2021-01-10"),))
def test_parse_create_daily_parse_error(
    user_id: uuid.UUID,
    command_raw: str,
    now: datetime.datetime,
):
    with pytest.raises(ParseError):
        parse_create_daily(user_id=user_id, command_raw=command_raw, now=now)


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
@pytest.mark.parametrize(
    ("command_raw", "expected_command"),
    (
        (
            # full command
            "09:00 2026-05-15 Drink water | Just because",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because",
                trigger_payload=OneTimeTriggerPayload(
                    type="ONE_TIME",
                    occurrence_date=datetime.date.fromisoformat("2026-05-15"),
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            # no reminder time
            "2026-05-15 Drink water | Just because",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because",
                trigger_payload=OneTimeTriggerPayload(
                    type="ONE_TIME",
                    occurrence_date=datetime.date.fromisoformat("2026-05-15"),
                    reminder_time=None,
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            # only title
            "2026-05-15 Drink water",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description=None,
                trigger_payload=OneTimeTriggerPayload(
                    type="ONE_TIME",
                    occurrence_date=datetime.date.fromisoformat("2026-05-15"),
                    reminder_time=None,
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            # many spaces
            "09:00     2026-05-15      Drink water     |     Just because",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because",
                trigger_payload=OneTimeTriggerPayload(
                    type="ONE_TIME",
                    occurrence_date=datetime.date.fromisoformat("2026-05-15"),
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            # description contains separator
            "09:00 2026-05-15 Drink water | Just because | more text",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because | more text",
                trigger_payload=OneTimeTriggerPayload(
                    type="ONE_TIME",
                    occurrence_date=datetime.date.fromisoformat("2026-05-15"),
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10"),),
)
def test_parse_create_one_time(
    user_id: uuid.UUID,
    command_raw: str,
    expected_command: CreateTaskTemplateCommand,
    now: datetime.datetime,
):
    result_command = parse_create_one_time(
        user_id=user_id,
        command_raw=command_raw,
        now=now,
    )

    assert result_command == expected_command


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
@pytest.mark.parametrize(
    "command_raw",
    (
        "",
        "09:00",
        "2026-05-15",
        "09:00 2026-05-15",
        "09:99 2026-05-15 Drink",
        "2026-99-15 Drink",
        "2026-05-99 Drink",
        "Drink water",
        "09:00 Drink water",
        "2026-05-15 |",
        "09:00 2026-05-15 |",
    ),
)
@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10"),),
)
def test_parse_create_one_time_parse_error(
    user_id: uuid.UUID,
    command_raw: str,
    now: datetime.datetime,
):
    with pytest.raises(ParseError):
        parse_create_one_time(
            user_id=user_id,
            command_raw=command_raw,
            now=now,
        )


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
@pytest.mark.parametrize(
    ("command_raw", "expected_command"),
    (
        (
            "09:00 mon,tue Drink water | Just because",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because",
                trigger_payload=WeeklyTriggerPayload(
                    type="WEEKLY",
                    weekdays=[0, 1],
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            "09:00      mon,tue      Drink water     |     Just because",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because",
                trigger_payload=WeeklyTriggerPayload(
                    type="WEEKLY",
                    weekdays=[0, 1],
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            "mon,tue Drink water",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description=None,
                trigger_payload=WeeklyTriggerPayload(
                    type="WEEKLY",
                    weekdays=[0, 1],
                    reminder_time=None,
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            "09:00 mon,tue Drink water | Just because | more",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because | more",
                trigger_payload=WeeklyTriggerPayload(
                    type="WEEKLY",
                    weekdays=[0, 1],
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10"),),
)
def test_parse_create_weekly(
    user_id: uuid.UUID,
    command_raw: str,
    expected_command: CreateTaskTemplateCommand,
    now: datetime.datetime,
):
    result = parse_create_weekly(
        user_id=user_id,
        command_raw=command_raw,
        now=now,
    )

    assert result == expected_command


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
@pytest.mark.parametrize(
    "command_raw",
    (
        "",
        "09:00",
        "mon",
        "09:00 mon",
        "monday Drink",
        "monn Drink",
        "09:99 mon Drink",
        "|",
    ),
)
@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10"),),
)
def test_parse_create_weekly_parse_error(
    user_id: uuid.UUID,
    command_raw: str,
    now: datetime.datetime,
):
    with pytest.raises(ParseError):
        parse_create_weekly(
            user_id=user_id,
            command_raw=command_raw,
            now=now,
        )


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
@pytest.mark.parametrize(
    ("command_raw", "expected_command"),
    (
        (
            "09:00 15 Drink water | Just because",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because",
                trigger_payload=MonthlyTriggerPayload(
                    type="MONTHLY",
                    day_of_month=15,
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            "15 Drink water",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description=None,
                trigger_payload=MonthlyTriggerPayload(
                    type="MONTHLY",
                    day_of_month=15,
                    reminder_time=None,
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            "09:00 15 Drink water | Just because | more",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Drink water",
                description="Just because | more",
                trigger_payload=MonthlyTriggerPayload(
                    type="MONTHLY",
                    day_of_month=15,
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10"),),
)
def test_parse_create_monthly(
    user_id: uuid.UUID,
    command_raw: str,
    expected_command: CreateTaskTemplateCommand,
    now: datetime.datetime,
):
    result = parse_create_monthly(
        user_id=user_id,
        command_raw=command_raw,
        now=now,
    )

    assert result == expected_command


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
@pytest.mark.parametrize(
    "command_raw",
    (
        # "",
        # "09:00",
        # "15",
        "0 Drink",
        "32 Drink",
        "99 Drink",
        # "09:99 15 Drink",
        # "|",
    ),
)
@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10"),),
)
def test_parse_create_monthly_parse_error(
    user_id: uuid.UUID,
    command_raw: str,
    now: datetime.datetime,
):
    with pytest.raises(ParseError):
        parse_create_monthly(
            user_id=user_id,
            command_raw=command_raw,
            now=now,
        )


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
@pytest.mark.parametrize(
    ("command_raw", "expected_command"),
    (
        (
            "09:00 jan 15 Buy gifts | Birthday",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Buy gifts",
                description="Birthday",
                trigger_payload=YearlyTriggerPayload(
                    type="YEARLY",
                    month=1,
                    day=15,
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            "jan 15 Buy gifts",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Buy gifts",
                description=None,
                trigger_payload=YearlyTriggerPayload(
                    type="YEARLY",
                    month=1,
                    day=15,
                    reminder_time=None,
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
        (
            "09:00 jan 15 Buy gifts | Birthday | more",
            CreateTaskTemplateCommand(
                user_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                title="Buy gifts",
                description="Birthday | more",
                trigger_payload=YearlyTriggerPayload(
                    type="YEARLY",
                    month=1,
                    day=15,
                    reminder_time=datetime.time.fromisoformat("09:00"),
                ),
                now=datetime.datetime.fromisoformat("2021-01-10"),
            ),
        ),
    ),
)
@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10"),),
)
def test_parse_create_yearly(
    user_id: uuid.UUID,
    command_raw: str,
    expected_command: CreateTaskTemplateCommand,
    now: datetime.datetime,
):
    result = parse_create_yearly(
        user_id=user_id,
        command_raw=command_raw,
        now=now,
    )

    assert result == expected_command


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
@pytest.mark.parametrize(
    "command_raw",
    (
        "",
        "09:00",
        "jan",
        "jan 15",
        "foo 15 Drink",
        "jan 99 Drink",
        "09:99 jan 15 Drink",
        "|",
    ),
)
@pytest.mark.parametrize(
    "now",
    (datetime.datetime.fromisoformat("2021-01-10"),),
)
def test_parse_create_yearly_parse_error(
    user_id: uuid.UUID,
    command_raw: str,
    now: datetime.datetime,
):
    with pytest.raises(ParseError):
        parse_create_yearly(
            user_id=user_id,
            command_raw=command_raw,
            now=now,
        )
