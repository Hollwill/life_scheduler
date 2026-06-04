import datetime
import re
import uuid

from application.task_template.commands import CreateTaskTemplateCommand
from application.task_template.schemas import (
    DailyTriggerPayload,
    MonthlyTriggerPayload,
    OneTimeTriggerPayload,
    WeeklyTriggerPayload,
    YearlyTriggerPayload,
)
from presentation.telegram.exceptions import ParseError

TIME_PATTERN = re.compile(r"^\d{2}:\d{2}$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

WEEKDAYS_MAPPING = {
    "mon": 0,
    "tue": 1,
    "wed": 2,
    "thu": 3,
    "fri": 4,
    "sat": 5,
    "sun": 6,
}
MONTHS_MAPPING = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def _parse_reminder_time_optional(
    command_raw: str | None,
) -> tuple[str, datetime.time | None]:
    if not command_raw:
        raise ParseError("Empty command")

    parts = command_raw.split(maxsplit=1)

    if re.fullmatch(TIME_PATTERN, parts[0]):
        try:
            reminder_time = datetime.time.fromisoformat(parts[0])
        except ValueError:
            raise ParseError("Invalid reminder time")
    else:
        return command_raw, None

    return (parts[1] if len(parts) > 1 else ""), reminder_time


def _parse_title_with_description(command_raw: str) -> tuple[str, str | None]:
    split_payload = [part.strip() for part in command_raw.split("|", maxsplit=1)]

    title = split_payload[0]

    if not title:
        raise ParseError("Title cannot be empty")

    description = None

    if len(split_payload) == 2:
        description = split_payload[1]

    return title, description


def _parse_occurrence_date(command_raw: str) -> tuple[str, datetime.date]:
    if not command_raw:
        raise ParseError("Cannot parse occurrence_date")
    parts = command_raw.split(maxsplit=1)

    if re.fullmatch(DATE_PATTERN, parts[0]):
        try:
            occurrence_date = datetime.date.fromisoformat(parts[0])
        except ValueError:
            raise ParseError("Invalid occurrence date")
    else:
        raise ParseError("Occurrence date should be passed")

    return (parts[1] if len(parts) > 1 else ""), occurrence_date


def _parse_weekdays(command_raw: str) -> tuple[str, list[int]]:
    if not command_raw:
        raise ParseError("Cannot parse weekdays")
    parts = command_raw.split(maxsplit=1)
    weekdays = parts[0].split(",")
    weekdays_result = []
    for weekday in weekdays:
        try:
            weekdays_result.append(WEEKDAYS_MAPPING[weekday])
        except KeyError:
            raise ParseError(f"Invalid weekday {weekday}")
    return (parts[1] if len(parts) > 1 else ""), weekdays_result


def _parse_day_of_month(command_raw: str) -> tuple[str, int]:
    if not command_raw:
        raise ParseError("Cannot parse day of month")
    parts = command_raw.split(maxsplit=1)

    possible_day_of_month = parts[0].strip()
    if not possible_day_of_month.isdigit():
        raise ParseError("Invalid day of month")

    day_of_month = int(possible_day_of_month)

    return (parts[1] if len(parts) > 1 else ""), day_of_month


def _parse_month(command_raw: str) -> tuple[str, int]:
    if not command_raw:
        raise ParseError("Cannot parse month")
    parts = command_raw.split(maxsplit=1)

    possible_month = parts[0].strip()
    try:
        parsed_month = MONTHS_MAPPING[possible_month]
    except KeyError:
        raise ParseError(f"Invalid month {possible_month}")

    return (parts[1] if len(parts) > 1 else ""), parsed_month


def parse_create_daily(
    user_id: uuid.UUID, command_raw: str | None, now: datetime.datetime
) -> CreateTaskTemplateCommand:

    remaining_command_raw, reminder_time = _parse_reminder_time_optional(command_raw)

    title, description = _parse_title_with_description(remaining_command_raw)

    return CreateTaskTemplateCommand(
        user_id=user_id,
        title=title,
        description=description,
        trigger_payload=DailyTriggerPayload(
            type="DAILY",
            reminder_time=reminder_time,
        ),
        now=now,
    )


def parse_create_one_time(
    user_id: uuid.UUID, command_raw: str | None, now: datetime.datetime
) -> CreateTaskTemplateCommand:

    remaining_command_raw, reminder_time = _parse_reminder_time_optional(command_raw)

    remaining_command_raw, occurrence_date = _parse_occurrence_date(
        remaining_command_raw
    )

    title, description = _parse_title_with_description(remaining_command_raw)

    return CreateTaskTemplateCommand(
        user_id=user_id,
        title=title,
        description=description,
        trigger_payload=OneTimeTriggerPayload(
            type="ONE_TIME",
            occurrence_date=occurrence_date,
            reminder_time=reminder_time,
        ),
        now=now,
    )


def parse_create_weekly(
    user_id: uuid.UUID,
    command_raw: str | None,
    now: datetime.datetime,
) -> CreateTaskTemplateCommand:

    remaining_command_raw, reminder_time = _parse_reminder_time_optional(command_raw)

    remaining_command_raw, weekdays = _parse_weekdays(
        remaining_command_raw,
    )

    title, description = _parse_title_with_description(
        remaining_command_raw,
    )

    return CreateTaskTemplateCommand(
        user_id=user_id,
        title=title,
        description=description,
        trigger_payload=WeeklyTriggerPayload(
            type="WEEKLY",
            weekdays=weekdays,
            reminder_time=reminder_time,
        ),
        now=now,
    )


def parse_create_monthly(
    user_id: uuid.UUID,
    command_raw: str | None,
    now: datetime.datetime,
) -> CreateTaskTemplateCommand:

    remaining_command_raw, reminder_time = _parse_reminder_time_optional(command_raw)

    remaining_command_raw, day_of_month = _parse_day_of_month(
        remaining_command_raw,
    )

    title, description = _parse_title_with_description(
        remaining_command_raw,
    )

    return CreateTaskTemplateCommand(
        user_id=user_id,
        title=title,
        description=description,
        trigger_payload=MonthlyTriggerPayload(
            type="MONTHLY",
            day_of_month=day_of_month,
            reminder_time=reminder_time,
        ),
        now=now,
    )


def parse_create_yearly(
    user_id: uuid.UUID,
    command_raw: str | None,
    now: datetime.datetime,
) -> CreateTaskTemplateCommand:

    remaining_command_raw, reminder_time = _parse_reminder_time_optional(
        command_raw,
    )

    remaining_command_raw, month = _parse_month(
        remaining_command_raw,
    )

    remaining_command_raw, day_of_month = _parse_day_of_month(
        remaining_command_raw,
    )

    title, description = _parse_title_with_description(
        remaining_command_raw,
    )

    return CreateTaskTemplateCommand(
        user_id=user_id,
        title=title,
        description=description,
        trigger_payload=YearlyTriggerPayload(
            type="YEARLY",
            month=month,
            day=day_of_month,
            reminder_time=reminder_time,
        ),
        now=now,
    )
