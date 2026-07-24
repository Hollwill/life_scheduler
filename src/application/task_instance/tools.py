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
)


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
