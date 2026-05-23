import abc


class CommandHandler[C, R](abc.ABC):
    @abc.abstractmethod
    async def handle(self, command: C) -> R:
        pass
