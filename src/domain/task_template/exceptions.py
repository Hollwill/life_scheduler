from domain.common import DomainException


class InvalidDayOfMonthException(DomainException):
    @property
    def code(self) -> str:
        return "invalid_day_of_month"

    @property
    def message_template(self) -> str:
        return "Day of month must be between 1 and 31, but got {value}"


class EmptyWeekdaysException(DomainException):
    @property
    def code(self) -> str:
        return "empty_weekdays"

    @property
    def message_template(self) -> str:
        return "At least one weekday must be specified for WeeklyTrigger"


class InvalidYearlyDateException(DomainException):
    @property
    def code(self) -> str:
        return "invalid_yearly_date"

    @property
    def message_template(self) -> str:
        return "Invalid date for YearlyTrigger: month {month}, day {day}"
