import typing

import pydantic

from application.llm.base import Tool
from application.llm.context import ToolContext
from application.task_template.commands import (
    CreateTaskTemplateCommand,
    CreateTaskTemplateHandler,
)
from application.task_template.queries import (
    GetTaskTemplatesHandler,
    GetTaskTemplatesQuery,
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

    async def call(
        self, payload: CreateTaskTemplateToolInput, context: ToolContext
    ) -> dict[str, typing.Any]:

        command = CreateTaskTemplateCommand(
            user_id=context.user_id,
            title=payload.title,
            description=payload.description,
            trigger_payload=payload.trigger_payload,
            now=context.now,
        )

        return await self.handler.handle(command=command)


class GetTaskTemplatesToolInput(pydantic.BaseModel):
    pass


class GetTaskTemplatesTool(Tool):
    input_model = GetTaskTemplatesToolInput

    name = "get_task_templates"
    description = "Get all task templates"

    def __init__(
        self,
        handler: GetTaskTemplatesHandler,
    ):
        self.handler = handler

    async def call(
        self, payload: GetTaskTemplatesToolInput, context: ToolContext
    ) -> list[dict[str, typing.Any]]:

        query = GetTaskTemplatesQuery(
            user_id=context.user_id,
        )

        return [
            task_template.model_dump()
            for task_template in await self.handler.handle(query=query)
        ]
