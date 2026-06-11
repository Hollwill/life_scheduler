from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.common.unit_of_work import UnitOfWork
from domain.common import AggregateRoot
from domain.common.event import DomainEvent
from infrastructure.database.outbox import OutboxModel
from infrastructure.database.repositories.outbox import SqlAlchemyOutboxRepository
from infrastructure.database.repositories.task_instance import (
    SqlAlchemyTaskInstanceRepository,
)
from infrastructure.database.repositories.task_template import (
    SqlAlchemyTaskTemplateRepository,
)
from infrastructure.database.repositories.user import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        super().__init__()
        self._session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        if self.session is not None:
            raise RuntimeError("Unit of Work already used!")

        self.session = self._session_factory()
        assert self.session is not None

        self._task_instances = SqlAlchemyTaskInstanceRepository(self.session)
        self._task_templates = SqlAlchemyTaskTemplateRepository(self.session)
        self._users = SqlAlchemyUserRepository(self.session)
        self._outbox = SqlAlchemyOutboxRepository(self.session)

        return self

    async def commit(self):
        if self.session is None:
            return
        await self.session.commit()

    async def rollback(self):
        if self.session is None:
            return
        await self.session.rollback()

    async def __aexit__(self, exc_type, exc, tb):
        assert self.session is not None
        try:
            if exc_type:
                await self.session.rollback()
            else:
                events = self._collect_events()
                self.session.add_all(map(lambda x: OutboxModel.from_event(x), events))
                await self.session.commit()
        finally:
            await self.session.close()

    def _collect_events(self) -> list[DomainEvent]:
        assert self.session is not None

        events = []

        for obj in [*self.session.dirty, *self.session.new]:
            if isinstance(obj, AggregateRoot):
                events.extend(obj.flush_events())
        return events
