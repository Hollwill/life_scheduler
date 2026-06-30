import pydantic

from application.llm.base import Tool
from application.llm.context import ToolContext
from application.llm.models import ToolDefinition


class ToolDispatcher:
    def __init__(
        self,
        tools: dict[str, Tool],
    ):
        self.tools = tools

    async def dispatch(
        self,
        tool_name: str,
        raw_arguments: dict,
        context: ToolContext,
    ):
        tool = self.tools[tool_name]

        arguments = tool.input_model.model_validate(raw_arguments)

        return await tool.call(arguments, context=context)

    @staticmethod
    def _create_tool_definition(
        name: str,
        description: str,
        model: type[pydantic.BaseModel],
    ) -> ToolDefinition:
        return ToolDefinition(
            type="function",
            name=name,
            description=description,
            parameters=model.model_json_schema(),
        )

    def get_tool_definitions(self) -> list[ToolDefinition]:
        return [
            self._create_tool_definition(
                name=tool.name, description=tool.description, model=tool.input_model
            )
            for tool in self.tools.values()
        ]
