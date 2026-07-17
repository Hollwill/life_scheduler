import datetime
import typing

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from application.common.repositories import OutboxRepository
from domain.common.event import Event
from infrastructure.database.orm import outbox_table
from infrastructure.database.outbox import OutboxModel


class SqlAlchemyOutboxRepository(OutboxRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, instance: OutboxModel):
        self.session.add(instance)

    async def save_from_event(self, event: Event):
        instance = OutboxModel.from_event(event)
        await self.save(instance)

    async def get_unprocessed(self) -> typing.Collection[OutboxModel]:
        stmt = select(OutboxModel).where(outbox_table.c.processed_at.is_(None))
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def mark_processed(
        self, instance: OutboxModel, now: datetime.datetime
    ) -> None:
        instance.processed_at = now
