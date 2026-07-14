import dataclasses
import enum

from domain.common import ValueObject
from domain.task_template.exceptions import InvalidDayOfMonthException


class TriggerType(enum.Enum):
    ONE_TIME = "ONE_TIME"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    RELATIVE = "RELATIVE"


class Weekday(enum.IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Month(enum.IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


@dataclasses.dataclass(frozen=True)
class DayOfMonth(ValueObject):
    value: int

    def __post_init__(self):
        if not 1 <= self.value <= 31:
            raise InvalidDayOfMonthException(context={"value": self.value})

    def __composite_values__(self):
        return (self.value,)
