import collections
import collections.abc
import copy
import uuid

from domain.task_template.aggregate import TaskTemplate
from domain.task_template.repository import TaskTemplateRepository
from infrastructure.memory.database import MemoryDatabase


class MemoryTaskTemplateRepository(TaskTemplateRepository):
    def __init__(self, db: MemoryDatabase) -> None:
        self.db = db

    async def get_by_id(self, task_template_id: uuid.UUID) -> TaskTemplate | None:
        template = self.db.task_templates.get(task_template_id)
        if template is None:
            return None
        return copy.deepcopy(template)

    async def get_by_public_id(
        self, task_template_public_id: str
    ) -> TaskTemplate | None:
        for task_template in self.db.task_templates.values():
            if task_template_public_id == task_template.public_id:
                return copy.deepcopy(task_template)
        return None

    async def save(self, task_template: TaskTemplate) -> None:
        self.db.task_templates[task_template.id] = copy.deepcopy(task_template)

    async def get_all_active_by_user(
        self, user_id: uuid.UUID
    ) -> collections.abc.Collection[TaskTemplate]:
        return tuple(
            task_template
            for task_template in self.db.task_templates.values()
            if task_template.is_active and task_template.user_id == user_id
        )

    async def get_all_active(self) -> collections.abc.Collection[TaskTemplate]:
        return tuple(
            task_template
            for task_template in self.db.task_templates.values()
            if task_template.is_active
        )
