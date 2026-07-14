import typing

import pydantic

from application.llm.base import Tool
from application.llm.context import ToolContext
from application.user.commands import SetUserTimezoneCommand, SetUserTimezoneHandler


class SetUserTimezoneToolInput(pydantic.BaseModel):
    timezone: str


class SetUserTimezoneTool(Tool):
    input_model = SetUserTimezoneToolInput

    name = "set_user_timezone"
    description = "Set user timezone"

    def __init__(
        self,
        handler: SetUserTimezoneHandler,
    ):
        self.handler = handler

    async def call(
        self, payload: SetUserTimezoneToolInput, context: ToolContext
    ) -> dict[str, typing.Any]:

        command = SetUserTimezoneCommand(
            user_id=context.user_id,
            timezone=payload.timezone,
        )

        return await self.handler.handle(command=command)
