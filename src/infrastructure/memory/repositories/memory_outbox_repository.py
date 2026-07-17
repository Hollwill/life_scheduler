import copy
import datetime
import typing

from application.common.repositories import OutboxRepository
from domain.common.event import Event
from infrastructure.database.outbox import OutboxModel
from infrastructure.memory.database import MemoryDatabase


class MemoryOutboxRepository(OutboxRepository):
    def __init__(self, db: MemoryDatabase) -> None:
        self.db = db

    async def save(self, instance: OutboxModel):
        self.db.outbox[instance.id] = copy.deepcopy(instance)

    async def save_from_event(self, event: Event):
        instance = OutboxModel.from_event(event)
        await self.save(instance)

    async def get_unprocessed(self) -> typing.Collection[OutboxModel]:
        return [
            outbox_instance
            for outbox_instance in self.db.outbox.values()
            if outbox_instance.processed_at is None
        ]

    async def mark_processed(
        self, instance: OutboxModel, now: datetime.datetime
    ) -> None:
        db_instance = self.db.outbox[instance.id]
        db_instance.processed_at = now
