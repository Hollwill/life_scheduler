import abc
import typing


class DomainException(Exception, abc.ABC):
    """Base domain exception"""

    @property
    @abc.abstractmethod
    def code(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def message_template(self) -> str:
        pass

    @property
    def message(self) -> str:
        return self._formatted_message

    @typing.final
    def __init__(self, context: dict[str, typing.Any] | None = None):
        template: str = self.message_template

        if context:
            try:
                self._formatted_message = template.format(**context)
            except KeyError as e:
                raise ValueError(
                    f"Ошибка форматирования {self.__class__.__name__}: "
                    f"ключ {e} отсутствует в контексте"
                ) from e
        else:
            self._formatted_message = template

        super().__init__(f"[{self.code}] {self._formatted_message}")
