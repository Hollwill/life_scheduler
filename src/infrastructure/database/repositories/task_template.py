import collections.abc
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.task_template.aggregate import TaskTemplate
from domain.task_template.repository import TaskTemplateRepository
from infrastructure.database.orm import task_template_table


class SqlAlchemyTaskTemplateRepository(TaskTemplateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        task_template_id: uuid.UUID,
    ) -> TaskTemplate | None:

        result = await self.session.execute(
            select(TaskTemplate).where(task_template_table.c.id == task_template_id)
        )
        return result.scalars().first()

    async def get_by_public_id(
        self, task_template_public_id: str
    ) -> TaskTemplate | None:

        result = await self.session.execute(
            select(TaskTemplate).where(
                task_template_table.c.public_id == task_template_public_id
            )
        )
        return result.scalars().first()

    async def save(
        self,
        task_template: TaskTemplate,
    ) -> None:
        self.session.add(task_template)

    async def get_all_active_by_user(
        self, user_id: uuid.UUID
    ) -> collections.abc.Collection[TaskTemplate]:
        stmt = select(TaskTemplate).where(
            task_template_table.c.is_active.is_(True),
            task_template_table.c.user_id == user_id,
        )

        result = await self.session.execute(stmt)

        return list(result.scalars())

    async def get_all_active(
        self,
    ) -> collections.abc.Collection[TaskTemplate]:
        stmt = select(TaskTemplate).where(task_template_table.c.is_active.is_(True))

        result = await self.session.execute(stmt)

        return list(result.scalars())
