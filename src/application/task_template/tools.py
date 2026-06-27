import pydantic

from application.common.tools.base import Tool
from application.common.tools.context import ToolContext
from application.task_template.commands import (
    CreateTaskTemplateCommand,
    CreateTaskTemplateHandler,
)
from application.task_template.schemas import TriggerPayload


class CreateTaskTemplateToolInput(pydantic.BaseModel):
    title: str
    description: str | None
    trigger_payload: TriggerPayload


class CreateTaskTemplateTool(Tool):
    input_model = CreateTaskTemplateToolInput

    name = "create_task_template"
    description = "Create a new task template"

    def __init__(
        self,
        handler: CreateTaskTemplateHandler,
    ):
        self.handler = handler

    async def call(self, payload: CreateTaskTemplateToolInput, context: ToolContext):

        command = CreateTaskTemplateCommand(
            user_id=context.user_id,
            title=payload.title,
            description=payload.description,
            trigger_payload=payload.trigger_payload,
            now=context.now,
        )

        await self.handler.handle(command=command)
