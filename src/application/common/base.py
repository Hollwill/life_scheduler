import abc


class CommandHandler[C, R](abc.ABC):
    @abc.abstractmethod
    async def handle(self, command: C) -> R:
        pass


class QueryHandler[Q, R](abc.ABC):
    @abc.abstractmethod
    async def handle(self, query: Q) -> R:
        pass
