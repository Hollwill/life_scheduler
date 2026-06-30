import abc
import typing

import pydantic

from application.llm.context import ToolContext


class Tool(abc.ABC):
    input_model: typing.ClassVar[typing.Type[pydantic.BaseModel]]

    name: typing.ClassVar[str]

    description: typing.ClassVar[str]

    @abc.abstractmethod
    async def call(self, arguments: pydantic.BaseModel, context: ToolContext):
        pass
