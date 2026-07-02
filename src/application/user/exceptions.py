from application.common.exceptions import ApplicationException


class UserNotFoundException(ApplicationException):
    @property
    def code(self) -> str:
        return "user_not_found"

    @property
    def message_template(self) -> str:
        return "User with id {user_id} not found"
