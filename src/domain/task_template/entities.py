import abc
import datetime
import typing
import uuid

from domain.common import Entity
from domain.task_template.exceptions import (
    EmptyWeekdaysException,
    InvalidYearlyDateException,
)
from domain.task_template.value_objects import DayOfMonth, Month, TriggerType, Weekday


class Trigger(
    abc.ABC,
    Entity[uuid.UUID],
):
    type: typing.ClassVar[TriggerType]

    def __init__(self, id: uuid.UUID):
        super().__init__(id=id)

    @abc.abstractmethod
    def occurs_on(self, day: datetime.date) -> bool:
        pass

    @abc.abstractmethod
    def _calculate_reminder_at(self, day: datetime.date) -> datetime.datetime | None:
        pass

    def reminder_at(self, day: datetime.date) -> datetime.datetime | None:
        if not self.occurs_on(day):
            return None
        return self._calculate_reminder_at(day)


class ReminderTimeTrigger(
    Trigger,
    abc.ABC,
):
    def __init__(self, id: uuid.UUID, reminder_time: datetime.time | None):
        super().__init__(id=id)
        self.reminder_time = reminder_time

    def _calculate_reminder_at(self, day: datetime.date) -> datetime.datetime | None:
        if self.reminder_time is None:
            return None
        return datetime.datetime.combine(date=day, time=self.reminder_time)


class OneTimeTrigger(ReminderTimeTrigger):
    occurrence_date: datetime.date

    type: typing.ClassVar[TriggerType] = TriggerType.ONE_TIME

    def __init__(
        self,
        id: uuid.UUID,
        occurrence_date: datetime.date,
        reminder_time: datetime.time | None = None,
    ):
        super().__init__(id=id, reminder_time=reminder_time)
        self.occurrence_date = occurrence_date

    def occurs_on(self, day: datetime.date) -> bool:
        return day == self.occurrence_date


class DailyTrigger(ReminderTimeTrigger):
    type: typing.ClassVar[TriggerType] = TriggerType.DAILY

    def __init__(self, id: uuid.UUID, reminder_time: datetime.time | None = None):
        super().__init__(id=id, reminder_time=reminder_time)

    def occurs_on(self, day: datetime.date) -> bool:
        return True


class WeeklyTrigger(ReminderTimeTrigger):
    type: typing.ClassVar[TriggerType] = TriggerType.WEEKLY

    def __init__(
        self,
        id: uuid.UUID,
        weekdays: frozenset[Weekday],
        reminder_time: datetime.time | None = None,
    ):
        super().__init__(id=id, reminder_time=reminder_time)
        if not weekdays:
            raise EmptyWeekdaysException()
        self.weekdays = weekdays

    def occurs_on(self, day: datetime.date) -> bool:
        return day.weekday() in self.weekdays


class MonthlyTrigger(ReminderTimeTrigger):
    type: typing.ClassVar[TriggerType] = TriggerType.MONTHLY

    def __init__(
        self,
        id: uuid.UUID,
        day_of_month: DayOfMonth,
        reminder_time: datetime.time | None = None,
    ):
        super().__init__(id=id, reminder_time=reminder_time)
        self.day_of_month = day_of_month

    def occurs_on(self, day: datetime.date) -> bool:
        return day.day == self.day_of_month.value


class YearlyTrigger(ReminderTimeTrigger):
    type: typing.ClassVar[TriggerType] = TriggerType.YEARLY

    def __init__(
        self,
        id: uuid.UUID,
        month: Month,
        day: DayOfMonth,
        reminder_time: datetime.time | None = None,
    ):
        super().__init__(id=id, reminder_time=reminder_time)
        try:
            # Check if date is valid. Use leap year (2000) to allow February 29th.
            datetime.date(2000, month, day.value)
        except ValueError:
            raise InvalidYearlyDateException(
                context={"month": int(month), "day": day.value}
            )
        self.month = month
        self.day = day

    def occurs_on(self, day: datetime.date) -> bool:
        return day.month == self.month and day.day == self.day.value
