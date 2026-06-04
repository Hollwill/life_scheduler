import collections.abc
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.task_template.aggregate import TaskTemplate
from domain.task_template.repository import TaskTemplateRepository
from infrastructure.database.mappers import (
    task_template_from_orm,
    task_template_to_orm,
    trigger_to_dict,
)
from infrastructure.database.models import TaskTemplateModel


class SqlAlchemyTaskTemplateRepository(TaskTemplateRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self,
        task_template_id: uuid.UUID,
    ) -> TaskTemplate | None:

        result = await self.session.execute(
            select(TaskTemplateModel).where(TaskTemplateModel.id == task_template_id)
        )
        instance = result.scalars().first()

        if instance is None:
            return None

        return task_template_from_orm(instance)

    async def get_by_public_id(
        self, task_template_public_id: str
    ) -> TaskTemplate | None:

        result = await self.session.execute(
            select(TaskTemplateModel).where(
                TaskTemplateModel.public_id == task_template_public_id
            )
        )
        instance = result.scalars().first()

        if instance is None:
            return None

        return task_template_from_orm(instance)

    async def save(
        self,
        task_template: TaskTemplate,
    ) -> None:
        instance = await self.session.get(
            TaskTemplateModel,
            task_template.id,
        )

        if instance is None:
            instance = task_template_to_orm(task_template)
            self.session.add(instance)
            return

        instance.user_id = task_template.user_id
        instance.title = task_template.title
        instance.description = task_template.description
        instance.trigger = trigger_to_dict(task_template.trigger)
        instance.is_active = task_template.is_active
        instance.created_at = task_template.created_at
        instance.updated_at = task_template.updated_at

    async def get_all_active_by_user(
        self, user_id: uuid.UUID
    ) -> collections.abc.Collection[TaskTemplate]:
        stmt = select(TaskTemplateModel).where(
            TaskTemplateModel.is_active.is_(True), TaskTemplateModel.user_id == user_id
        )

        result = await self.session.execute(stmt)

        return [task_template_from_orm(orm) for orm in result.scalars()]

    async def get_all_active(
        self,
    ) -> collections.abc.Collection[TaskTemplate]:
        stmt = select(TaskTemplateModel).where(TaskTemplateModel.is_active.is_(True))

        result = await self.session.execute(stmt)

        return [task_template_from_orm(orm) for orm in result.scalars()]
