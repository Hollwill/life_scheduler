import collections
import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.task_instance.aggregate import TaskInstance, TaskStatus
from domain.task_instance.repository import TaskInstanceRepository
from infrastructure.database.orm import task_instance_table


class SqlAlchemyTaskInstanceRepository(TaskInstanceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, task_instance_id: uuid.UUID) -> TaskInstance | None:
        result = await self.session.execute(
            select(TaskInstance).where(task_instance_table.c.id == task_instance_id)
        )
        return result.scalars().first()

    async def get_by_public_id(
        self, task_instance_public_id: str
    ) -> TaskInstance | None:
        result = await self.session.execute(
            select(TaskInstance).where(
                task_instance_table.c.public_id == task_instance_public_id
            )
        )
        return result.scalars().first()

    async def save(self, task_instance: TaskInstance) -> None:
        self.session.add(task_instance)

    async def get_all_by_day(
        self, day: datetime.date
    ) -> collections.abc.Collection[TaskInstance]:
        stmt = select(TaskInstance).where(task_instance_table.c.occurrence_date == day)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_all_by_user(
        self,
        user_id: uuid.UUID,
        from_date: datetime.date,
        to_date: datetime.date | None = None,
    ) -> collections.abc.Collection[TaskInstance]:
        conditions = [
            task_instance_table.c.user_id == user_id,
            task_instance_table.c.occurrence_date >= from_date,
        ]

        if to_date:
            conditions.append(task_instance_table.c.occurrence_date <= to_date)
        stmt = select(TaskInstance).where(*conditions)
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_all_for_remind(
        self, now: datetime.datetime
    ) -> collections.abc.Collection[TaskInstance]:
        stmt = select(TaskInstance).where(
            task_instance_table.c.occurrence_date == now.date(),
            task_instance_table.c.scheduled_at.isnot(None),
            task_instance_table.c.scheduled_at <= now,
            task_instance_table.c.status == TaskStatus.PENDING,
            task_instance_table.c.reminded_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def get_all_overdue(
        self, now: datetime.datetime
    ) -> collections.abc.Collection[TaskInstance]:
        stmt = select(TaskInstance).where(
            task_instance_table.c.occurrence_date < now.date(),
            task_instance_table.c.status == TaskStatus.PENDING,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars())
