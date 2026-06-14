from domain.common import DomainException


class InvalidZoneInfoException(DomainException):
    @property
    def code(self) -> str:
        return "invalid_zoneinfo"

    @property
    def message_template(self) -> str:
        return "Invalid zoneinfo"
