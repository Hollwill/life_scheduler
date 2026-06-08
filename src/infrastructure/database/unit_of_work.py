from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from application.common.unit_of_work import UnitOfWork
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
                await self.session.commit()
        finally:
            await self.session.close()
