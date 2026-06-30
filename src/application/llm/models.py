import dataclasses
import datetime
import typing


@dataclasses.dataclass
class ChatMessage:
    role: typing.Literal["system", "user", "assistant", "tool"]
    content: str
    created_at: datetime.datetime

    tool_calls: list[ToolCall] | None = None

    tool_call_id: str | None = None


@dataclasses.dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclasses.dataclass(frozen=True)
class ChatResponse:
    content: str
    tool_calls: list[ToolCall]


@dataclasses.dataclass(frozen=True)
class ToolDefinition:
    type: str
    name: str
    description: str
    parameters: dict
