import datetime
import uuid

import factory

from domain.task_template.entities import (
    DailyTrigger,
    MonthlyTrigger,
    OneTimeTrigger,
    WeeklyTrigger,
    YearlyTrigger,
)
from domain.task_template.value_objects import (
    DayOfMonth,
    Month,
    Weekday,
)


class OneTimeTriggerFactory(factory.Factory):
    class Meta:
        model = OneTimeTrigger

    id = factory.LazyFunction(uuid.uuid4)

    occurrence_date = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=1)
    )

    reminder_time = factory.LazyFunction(lambda: datetime.time.fromisoformat("09:00"))


class DailyTriggerFactory(factory.Factory):
    class Meta:
        model = DailyTrigger

    id = factory.LazyFunction(uuid.uuid4)

    reminder_time = factory.LazyFunction(lambda: datetime.time.fromisoformat("09:00"))


class WeeklyTriggerFactory(factory.Factory):
    class Meta:
        model = WeeklyTrigger

    id = factory.LazyFunction(uuid.uuid4)

    weekdays = factory.LazyFunction(
        lambda: frozenset(
            {
                Weekday.MONDAY,
                Weekday.WEDNESDAY,
            }
        )
    )

    reminder_time = factory.LazyFunction(lambda: datetime.time.fromisoformat("09:00"))


class MonthlyTriggerFactory(factory.Factory):
    class Meta:
        model = MonthlyTrigger

    id = factory.LazyFunction(uuid.uuid4)

    day_of_month = factory.LazyFunction(lambda: DayOfMonth(1))

    reminder_time = factory.LazyFunction(lambda: datetime.time.fromisoformat("09:00"))


class YearlyTriggerFactory(factory.Factory):
    class Meta:
        model = YearlyTrigger

    id = factory.LazyFunction(uuid.uuid4)

    month = factory.LazyFunction(lambda: Month.JANUARY)

    day = factory.LazyFunction(lambda: DayOfMonth(1))

    reminder_time = factory.LazyFunction(lambda: datetime.time.fromisoformat("09:00"))
