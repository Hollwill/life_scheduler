import abc
import datetime
import typing

from infrastructure.database.outbox import OutboxModel


class OutboxRepository(abc.ABC):
    @abc.abstractmethod
    async def get_unprocessed(self) -> typing.Collection[OutboxModel]:
        pass

    @abc.abstractmethod
    async def mark_processed(
        self, instance: OutboxModel, now: datetime.datetime
    ) -> None:
        pass
