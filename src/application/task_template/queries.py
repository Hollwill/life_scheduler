import dataclasses
import uuid

from pydantic import TypeAdapter

from application.common.base import QueryHandler
from application.task_template.schemas import TaskTemplateResponse
from application.task_template.trigger_mapper import TriggerMapper
from domain.task_template.repository import TaskTemplateRepository


@dataclasses.dataclass
class GetTaskTemplatesQuery:
    user_id: uuid.UUID


class GetTaskTemplatesHandler(
    QueryHandler[GetTaskTemplatesQuery, TaskTemplateResponse]
):
    def __init__(self, task_template_repository: TaskTemplateRepository) -> None:
        super().__init__()
        self.task_template_repository = task_template_repository

    async def handle(self, query: GetTaskTemplatesQuery) -> list[TaskTemplateResponse]:
        task_templates = await self.task_template_repository.get_all_active_by_user(
            user_id=query.user_id
        )

        return TypeAdapter(list[TaskTemplateResponse]).validate_python(
            TaskTemplateResponse(
                public_id=task_template.public_id,
                title=task_template.title,
                description=task_template.description,
                trigger=TriggerMapper.to_model(task_template.trigger),
            )
            for task_template in task_templates
        )
