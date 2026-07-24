import abc
import collections
import datetime
import uuid

from domain.task_instance.aggregate import TaskInstance


class TaskInstanceRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, task_instance_id: uuid.UUID) -> TaskInstance | None:
        pass

    @abc.abstractmethod
    async def get_by_public_id(
        self, task_instance_public_id: str
    ) -> TaskInstance | None:
        pass

    @abc.abstractmethod
    async def save(self, task_instance: TaskInstance) -> None:
        pass

    @abc.abstractmethod
    async def get_all_by_day(
        self, day: datetime.date
    ) -> collections.abc.Collection[TaskInstance]:
        pass

    @abc.abstractmethod
    async def get_all_by_user(
        self,
        user_id: uuid.UUID,
        from_date: datetime.date,
        to_date: datetime.date | None = None,
    ) -> collections.abc.Collection[TaskInstance]:
        pass

    @abc.abstractmethod
    async def get_all_for_remind(
        self, now: datetime.datetime
    ) -> collections.abc.Collection[TaskInstance]:
        pass

    @abc.abstractmethod
    async def get_all_overdue(
        self, now: datetime.datetime
    ) -> collections.abc.Collection[TaskInstance]:
        pass
