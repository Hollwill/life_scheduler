import collections
import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.task_instance.aggregate import TaskInstance
from domain.task_instance.repository import TaskInstanceRepository
from infrastructure.database.mappers import task_instance_from_orm, task_instance_to_orm
from infrastructure.database.models import TaskInstanceModel


class SqlAlchemyTaskInstanceRepository(TaskInstanceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_instance_id: uuid.UUID) -> TaskInstance | None:
        result = await self.session.execute(
            select(TaskInstanceModel).where(TaskInstanceModel.id == task_instance_id)
        )
        instance = result.scalars().first()
        if instance is None:
            return None

        return task_instance_from_orm(instance)

    async def save(self, task_instance: TaskInstance) -> None:
        instance = await self.session.get(TaskInstanceModel, task_instance.id)

        if instance is None:
            instance = task_instance_to_orm(task_instance)
            self.session.add(instance)
            return

        instance.user_id = task_instance.user_id
        instance.task_template_id = task_instance.task_template_id
        instance.title = task_instance.title
        instance.description = task_instance.description
        instance.occurrence_date = task_instance.occurrence_date
        instance.scheduled_at = task_instance.scheduled_at
        instance.status = task_instance.status
        instance.created_at = task_instance.created_at
        instance.postpone_reason = task_instance.postpone_reason

    async def get_all_by_day(
        self, day: datetime.date
    ) -> collections.abc.Collection[TaskInstance]:
        stmt = select(TaskInstanceModel).where(TaskInstanceModel.occurrence_date == day)
        result = await self.session.execute(stmt)
        return [task_instance_from_orm(orm) for orm in result.scalars()]
