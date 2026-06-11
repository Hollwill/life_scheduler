from domain.common.exception import DomainException


class TaskInstanceNotScheduledException(DomainException):
    @property
    def code(self) -> str:
        return "task_instance_not_scheduled"

    @property
    def message_template(self) -> str:
        return "Task template does not occur on {scheduled_day}"


class TaskInstanceInvalidStatusException(DomainException):
    @property
    def code(self) -> str:
        return "task_instance_invalid_status"

    @property
    def message_template(self) -> str:
        return "Cannot call operation {operation} with status  {status}"


class TaskInstanceInvalidPostponeDateException(DomainException):
    @property
    def code(self) -> str:
        return "task_instance_invalid_postpone_date"

    @property
    def message_template(self) -> str:
        return "New occurrence date {new_date} must be greater than today {today}"


class TaskInstanceInvalidReminderDateException(DomainException):
    @property
    def code(self) -> str:
        return "task_instance_invalid_reminder_date"

    @property
    def message_template(self) -> str:
        return "Reminder date {reminder_date} must be equals today {today}"


class TaskInstanceReminderTimeNotComeYet(DomainException):
    @property
    def code(self) -> str:
        return "task_instance_reminder_time_not_come_yet"

    @property
    def message_template(self) -> str:
        return "Reminder time {reminder_time} not come yet"
