from application.common.exceptions import ApplicationException


class TaskTemplateNotFoundException(ApplicationException):
    @property
    def code(self) -> str:
        return "task_template_not_found"

    @property
    def message_template(self) -> str:
        return "Task template with id {task_template_id} not found"
