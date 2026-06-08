from application.common.unit_of_work import UnitOfWork
from infrastructure.memory.database import MemoryDatabase
from infrastructure.memory.repositories import (
    MemoryTaskInstanceRepository,
    MemoryTaskTemplateRepository,
    MemoryUserRepository,
)


class MemoryUnitOfWork(UnitOfWork):
    def __init__(self, memory_db: MemoryDatabase):
        super().__init__()
        self.memory_db = memory_db
        self.committed = False

    async def __aenter__(self):
        self._task_instances = MemoryTaskInstanceRepository(self.memory_db)
        self._task_templates = MemoryTaskTemplateRepository(self.memory_db)
        self._users = MemoryUserRepository(self.memory_db)

        self.committed = False
        return self

    async def commit(self):
        self.committed = True

    async def rollback(self):
        self.committed = False

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.rollback()
