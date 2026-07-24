import datetime
import typing

import pydantic

from application.llm.base import Tool
from application.llm.context import ToolContext
from application.task_instance.commands import (
    CompleteTaskInstanceCommand,
    CompleteTaskInstanceHandler,
    CreateTaskInstanceCommand,
    CreateTaskInstanceHandler,
    UpdateTaskInstanceCommand,
    UpdateTaskInstanceHandler,
)
from application.task_instance.queries import (
    GetTaskInstancesHandler,
    GetTaskInstancesQuery,
)
from domain.common.aggregate_root import EMPTY


class CreateTaskInstanceToolInput(pydantic.BaseModel):
    title: str
    description: str | None = None
    occurrence_date: datetime.date
    scheduled_at: datetime.datetime | None = None


class CreateTaskInstanceTool(Tool):
    input_model = CreateTaskInstanceToolInput

    name = "create_task_instance"
    description = (
        "Create a one-time task. "
        "Use this when the user asks to create a task that should happen only once, "
        "for example 'remind me tomorrow to buy milk' or "
        "'create a task for next Monday'. "
        "Do not use this tool for recurring tasks."
    )

    def __init__(
        self,
        handler: CreateTaskInstanceHandler,
    ):
        self.handler = handler

    async def call(
        self,
        payload: CreateTaskInstanceToolInput,
        context: ToolContext,
    ) -> dict[str, typing.Any]:
        command = CreateTaskInstanceCommand(
            user_id=context.user_id,
            title=payload.title,
            description=payload.description,
            occurrence_date=payload.occurrence_date,
            scheduled_at=payload.scheduled_at,
            now=context.now,
        )

        await self.handler.handle(command)

        return {
            "status": "success",
            "title": payload.title,
            "occurrence_date": payload.occurrence_date.isoformat(),
            "scheduled_at": (
                payload.scheduled_at.isoformat() if payload.scheduled_at else None
            ),
        }


class UpdateTaskInstanceToolInput(pydantic.BaseModel):
    task_instance_public_id: str
    title: str | None = None
    description: str | None = None
    occurrence_date: datetime.date | None = None
    scheduled_at: datetime.datetime | None = None


class UpdateTaskInstanceTool(Tool):
    input_model = UpdateTaskInstanceToolInput

    name = "update_task_instance"
    description = "update a task instance"

    def __init__(
        self,
        handler: UpdateTaskInstanceHandler,
    ):
        self.handler = handler

    async def call(
        self,
        payload: UpdateTaskInstanceToolInput,
        context: ToolContext,
    ) -> dict[str, typing.Any]:

        command = UpdateTaskInstanceCommand(
            task_instance_public_id=payload.task_instance_public_id,
            title=(payload.title if "title" in payload.model_fields_set else EMPTY),
            description=(
                payload.description
                if "description" in payload.model_fields_set
                else EMPTY
            ),
            occurrence_date=(
                payload.occurrence_date
                if "occurrence_date" in payload.model_fields_set
                else EMPTY
            ),
            scheduled_at=(
                payload.scheduled_at
                if "scheduled_at" in payload.model_fields_set
                else EMPTY
            ),
            now=context.now,
        )

        return await self.handler.handle(command=command)


class CompleteTaskInstanceToolInput(pydantic.BaseModel):
    task_instance_public_id: str


class CompleteTaskInstanceTool(Tool):
    input_model = CompleteTaskInstanceToolInput

    name = "complete_task_instance"
    description = (
        "Mark a task as completed. "
        "Use this when the user says they have completed, finished, or done a one-time task."
    )

    def __init__(
        self,
        handler: CompleteTaskInstanceHandler,
    ):
        self.handler = handler

    async def call(
        self,
        payload: CompleteTaskInstanceToolInput,
        context: ToolContext,
    ) -> dict[str, typing.Any]:
        command = CompleteTaskInstanceCommand(
            task_instance_public_id=payload.task_instance_public_id,
        )

        await self.handler.handle(command)

        return {
            "status": "success",
            "task_instance_public_id": payload.task_instance_public_id,
        }


class GetTaskInstancesToolInput(pydantic.BaseModel):
    day: datetime.date


class GetTaskInstancesTool(Tool):
    input_model = GetTaskInstancesToolInput

    name = "get_task_instances"
    description = (
        "Retrieve all task instances for a specific day. "
        "Use this when the user asks about today's, tomorrow's, yesterday's, "
        "or any specific day's tasks. "
        "Also use it before completing or modifying a task if you need to identify "
        "the correct task instance."
    )

    def __init__(
        self,
        handler: GetTaskInstancesHandler,
    ):
        self.handler = handler

    async def call(
        self,
        payload: GetTaskInstancesToolInput,
        context: ToolContext,
    ) -> list[dict[str, typing.Any]]:
        query = GetTaskInstancesQuery(
            user_id=context.user_id,
            day=payload.day,
        )

        task_instances = await self.handler.handle(query)

        return [
            task_instance.model_dump(mode="json") for task_instance in task_instances
        ]
