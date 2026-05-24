from domain.common.exception import DomainException


class TaskInstanceNotScheduledException(DomainException):
    @property
    def code(self) -> str:
        return "task_instance_not_scheduled"

    @property
    def message_template(self) -> str:
        return "Task template does not occur on {scheduled_day}"
