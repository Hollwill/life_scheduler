import copy
import uuid

from domain.task_template.aggregate import TaskTemplate
from domain.task_template.repository import TaskTemplateRepository


class MemoryTaskTemplateRepository(TaskTemplateRepository):
    def __init__(self) -> None:
        self.task_templates: dict[uuid.UUID, TaskTemplate] = {}

    async def get_by_id(self, task_template_id: uuid.UUID) -> TaskTemplate | None:
        template = self.task_templates.get(task_template_id)
        if template is None:
            return None
        return copy.deepcopy(template)

    async def save(self, task_template: TaskTemplate) -> None:
        self.task_templates[task_template.id] = copy.deepcopy(task_template)
