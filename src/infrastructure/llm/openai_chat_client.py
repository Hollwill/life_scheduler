import json
import typing

from openai import AsyncOpenAI

from application.llm.chat_client import ChatClient
from application.llm.models import (
    ChatMessage,
    ChatResponse,
    ToolCall,
    ToolDefinition,
)


class OpenAIChatClient(ChatClient):
    def __init__(
        self,
        client: AsyncOpenAI,
        model: str,
        instructions: str,
    ) -> None:
        self._client = client
        self._model = model
        self._instructions = instructions

    async def chat(
        self,
        messages: list[ChatMessage],
        tools: list[ToolDefinition],
    ) -> ChatResponse:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[self._serialize_message(message) for message in messages],
            tools=[
                {
                    "type": tool.type,
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
                for tool in tools
            ],
        )

        choice = response.choices[0]
        message = choice.message

        tool_calls = []

        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=json.loads(tool_call.function.arguments),
                    )
                )

        return ChatResponse(
            content=message.content or "",
            tool_calls=tool_calls,
        )

    @staticmethod
    def _serialize_message(
        message: ChatMessage,
    ) -> dict:
        result: dict[str, typing.Any] = {
            "role": message.role,
        }

        if message.content is not None:
            result["content"] = message.content

        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.name,
                        "arguments": json.dumps(tool_call.arguments),
                    },
                }
                for tool_call in message.tool_calls
            ]

        if message.tool_call_id:
            result["tool_call_id"] = message.tool_call_id

        return result
