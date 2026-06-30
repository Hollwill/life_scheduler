import datetime
import json
from unittest.mock import AsyncMock, MagicMock

from application.llm.models import (
    ChatMessage,
    ChatResponse,
    ToolCall,
    ToolDefinition,
)
from infrastructure.llm.openai_chat_client import OpenAIChatClient


async def test_chat_returns_assistant_response(now: datetime.datetime):
    client = MagicMock()
    client.chat.completions.create = AsyncMock()

    response = MagicMock()

    message = MagicMock()
    message.content = "Hello!"
    message.tool_calls = None

    choice = MagicMock()
    choice.message = message

    response.choices = [choice]

    client.chat.completions.create.return_value = response

    chat_client = OpenAIChatClient(
        client=client,
        model="gpt-4o-mini",
        instructions="",
    )

    result = await chat_client.chat(
        messages=[
            ChatMessage(
                role="user",
                content="Hi",
                tool_calls=None,
                tool_call_id=None,
                created_at=datetime.datetime.now(),
            ),
        ],
        tools=[],
    )

    assert result == ChatResponse(
        content="Hello!",
        tool_calls=[],
    )


async def test_chat_returns_tool_calls():
    client = MagicMock()
    client.chat.completions.create = AsyncMock()

    tool_call = MagicMock()
    tool_call.id = "call_1"

    function = MagicMock()
    function.name = "create_task"
    function.arguments = json.dumps(
        {
            "title": "Drink water",
        }
    )

    tool_call.function = function

    message = MagicMock()
    message.content = None
    message.tool_calls = [tool_call]

    choice = MagicMock()
    choice.message = message

    response = MagicMock()
    response.choices = [choice]

    client.chat.completions.create.return_value = response

    chat_client = OpenAIChatClient(
        client=client,
        model="gpt-4o-mini",
        instructions="",
    )

    result = await chat_client.chat(
        messages=[],
        tools=[],
    )

    assert result == ChatResponse(
        content="",
        tool_calls=[
            ToolCall(
                id="call_1",
                name="create_task",
                arguments={
                    "title": "Drink water",
                },
            ),
        ],
    )


async def test_chat_serializes_messages_and_tools():
    client = MagicMock()
    client.chat.completions.create = AsyncMock()

    response = MagicMock()

    message = MagicMock()
    message.content = "Done"
    message.tool_calls = None

    choice = MagicMock()
    choice.message = message

    response.choices = [choice]

    client.chat.completions.create.return_value = response

    chat_client = OpenAIChatClient(
        client=client,
        model="gpt-4o-mini",
        instructions="system prompt",
    )

    await chat_client.chat(
        messages=[
            ChatMessage(
                role="user",
                content="Hello",
                tool_calls=None,
                tool_call_id=None,
                created_at=datetime.datetime.now(),
            ),
        ],
        tools=[
            ToolDefinition(
                type="function",
                name="create_task",
                description="Creates task",
                parameters={
                    "type": "object",
                },
            ),
        ],
    )

    client.chat.completions.create.assert_awaited_once()

    kwargs = client.chat.completions.create.await_args.kwargs

    assert kwargs["model"] == "gpt-4o-mini"

    assert kwargs["messages"] == [
        {
            "role": "user",
            "content": "Hello",
        }
    ]

    assert kwargs["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "create_task",
                "description": "Creates task",
                "parameters": {
                    "type": "object",
                },
            },
        }
    ]
