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
