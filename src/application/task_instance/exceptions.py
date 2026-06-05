from application.common.exceptions import ApplicationException


class TaskInstanceNotFoundException(ApplicationException):
    @property
    def code(self) -> str:
        return "task_instance_not_found"

    @property
    def message_template(self) -> str:
        return "Task instance with id {task_instance_public_id} not found"
