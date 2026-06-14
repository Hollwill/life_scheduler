from zoneinfo import ZoneInfo

from domain.common import ValueObject
from domain.user.exceptions import InvalidZoneInfoException


class TimeZone(ValueObject):
    value: str

    def __init__(self, value: str):
        self.value = value

        try:
            self.to_zoneinfo()
        except ValueError:
            raise InvalidZoneInfoException()

    def to_zoneinfo(self) -> ZoneInfo:
        return ZoneInfo(self.value)

    def __composite_values__(self):
        return (self.value,)
