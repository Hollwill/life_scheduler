import typing

import pydantic

from application.llm.base import Tool
from application.llm.context import ToolContext
from application.task_template.commands import (
    CreateTaskTemplateCommand,
    CreateTaskTemplateHandler,
    DeactivateTaskTemplateCommand,
    DeactivateTaskTemplateHandler,
    UpdateTaskTemplateCommand,
    UpdateTaskTemplateHandler,
)
from application.task_template.queries import (
    GetTaskTemplatesHandler,
    GetTaskTemplatesQuery,
)
from application.task_template.schemas import TriggerPayload
from domain.common.aggregate_root import EMPTY


class UpdateTaskTemplateToolInput(pydantic.BaseModel):
    task_template_public_id: str
    title: str | None = None
    description: str | None = None
    trigger_payload: TriggerPayload | None = None


class UpdateTaskTemplateTool(Tool):
    input_model = UpdateTaskTemplateToolInput

    name = "update_task_template"
    description = "update a task template"

    def __init__(
        self,
        handler: UpdateTaskTemplateHandler,
    ):
        self.handler = handler

    async def call(
        self, payload: UpdateTaskTemplateToolInput, context: ToolContext
    ) -> dict[str, typing.Any]:

        command = UpdateTaskTemplateCommand(
            task_template_public_id=payload.task_template_public_id,
            title=payload.title if "title" in payload.model_fields_set else EMPTY,
            description=(
                payload.description
                if "description" in payload.model_fields_set
                else EMPTY
            ),
            trigger_payload=(
                payload.trigger_payload
                if "trigger_payload" in payload.model_fields_set
                else EMPTY
            ),
            now=context.now,
        )

        return await self.handler.handle(command=command)


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


class DeactivateTaskTemplateToolInput(pydantic.BaseModel):
    task_template_public_id: str


class DeactivateTaskTemplateTool(Tool):
    input_model = DeactivateTaskTemplateToolInput

    name = "deactivate_task_template"
    description = (
        "Deactivate an existing task template. "
        "Use this when the user asks to delete, remove, disable, "
        "or stop a recurring task."
    )

    def __init__(
        self,
        handler: DeactivateTaskTemplateHandler,
    ):
        self.handler = handler

    async def call(
        self, payload: DeactivateTaskTemplateToolInput, context: ToolContext
    ) -> dict[str, typing.Any]:

        command = DeactivateTaskTemplateCommand(
            task_template_public_id=payload.task_template_public_id,
            now=context.now,
        )

        await self.handler.handle(command=command)
        return {
            "status": "success",
            "task_template_public_id": payload.task_template_public_id,
        }
