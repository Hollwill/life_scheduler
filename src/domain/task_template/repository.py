import abc
import collections
import collections.abc
import uuid

from domain.task_template.aggregate import TaskTemplate


class TaskTemplateRepository(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, task_template_id: uuid.UUID) -> TaskTemplate | None:
        pass

    @abc.abstractmethod
    async def save(self, task_template: TaskTemplate) -> None:
        pass

    @abc.abstractmethod
    async def get_all_active(self) -> collections.abc.Collection[TaskTemplate]:
        pass
