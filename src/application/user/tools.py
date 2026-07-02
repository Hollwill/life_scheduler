import pydantic

from application.llm.base import Tool
from application.llm.context import ToolContext
from application.user.queries import GetUserNowHandler, GetUserNowQuery


class GetUserNowToolInput(pydantic.BaseModel):
    pass


class GetUserNowTool(Tool):
    input_model = GetUserNowToolInput

    name = "get_user_now"
    description = "Get current user datetime"

    def __init__(self, handler: GetUserNowHandler):
        self.handler = handler

    async def call(self, arguments: pydantic.BaseModel, context: ToolContext) -> str:

        return await self.handler.handle(
            GetUserNowQuery(user_id=context.user_id, now=context.now)
        )
