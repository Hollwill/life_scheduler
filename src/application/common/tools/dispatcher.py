import typing

import pydantic

from application.common.tools.base import Tool
from application.common.tools.context import ToolContext


class ToolDispatcher:
    def __init__(
        self,
        tools: dict[str, Tool],
    ):
        self.tools = tools

    async def dispatch_tool(
        self,
        tool_name: str,
        raw_arguments: dict,
        context: ToolContext,
    ):
        tool = self.tools[tool_name]

        arguments = tool.input_model.model_validate(raw_arguments)

        return await tool.call(arguments, context=context)

    @staticmethod
    def _create_tool_schema(
        name: str,
        description: str,
        model: type[pydantic.BaseModel],
    ) -> dict[str, typing.Any]:
        return {
            "type": "function",
            "name": name,
            "description": description,
            "parameters": model.model_json_schema(),
        }

    def get_schemas(self) -> list[dict[str, typing.Any]]:
        return [
            self._create_tool_schema(
                name=tool.name, description=tool.description, model=tool.input_model
            )
            for tool in self.tools.values()
        ]
