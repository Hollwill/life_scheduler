import collections
import copy
import datetime
import uuid

from domain.task_instance.aggregate import TaskInstance, TaskStatus
from domain.task_instance.repository import TaskInstanceRepository
from infrastructure.memory.database import MemoryDatabase


class MemoryTaskInstanceRepository(TaskInstanceRepository):
    def __init__(self, db: MemoryDatabase) -> None:
        self.db = db

    async def get_by_id(self, task_instance_id: uuid.UUID) -> TaskInstance | None:
        instance = self.db.task_instances.get(task_instance_id)
        if instance is None:
            return None
        return copy.deepcopy(instance)

    async def get_by_public_id(
        self, task_instance_public_id: str
    ) -> TaskInstance | None:

        for task_instance in self.db.task_instances.values():
            if task_instance.public_id == task_instance_public_id:
                return copy.deepcopy(task_instance)
        return None

    async def save(self, task_instance: TaskInstance) -> None:
        self.db.task_instances[task_instance.id] = copy.deepcopy(task_instance)

    async def get_all_by_day(
        self, day: datetime.date
    ) -> collections.abc.Collection[TaskInstance]:
        return [
            task_instance
            for task_instance in self.db.task_instances.values()
            if task_instance.occurrence_date == day
        ]

    async def get_all_by_user_per_day(
        self, user_id: uuid.UUID, day: datetime.date
    ) -> collections.abc.Collection[TaskInstance]:
        return [
            task_instance
            for task_instance in self.db.task_instances.values()
            if task_instance.occurrence_date == day and task_instance.user_id == user_id
        ]

    async def get_all_for_remind(
        self, now: datetime.datetime
    ) -> collections.abc.Collection[TaskInstance]:
        return [
            task_instance
            for task_instance in self.db.task_instances.values()
            if task_instance.occurrence_date == now.date()
            and task_instance.scheduled_at
            and task_instance.scheduled_at <= now
            and task_instance.status is TaskStatus.PENDING
            and task_instance.reminded_at is None
        ]

    async def get_all_overdue(
        self, now: datetime.datetime
    ) -> collections.abc.Collection[TaskInstance]:
        return [
            task_instance
            for task_instance in self.db.task_instances.values()
            if task_instance.occurrence_date < now.date()
            and task_instance.status is TaskStatus.PENDING
        ]
