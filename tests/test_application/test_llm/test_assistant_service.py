import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from application.llm.assistant_service import AssistantService
from application.llm.context import ToolContext
from application.llm.models import (
    ChatMessage,
    ChatResponse,
    ToolCall,
    ToolDefinition,
)
from application.llm.prompt_builder import PromptBuilder
from application.llm.repositories import ConversationHistoryRepository
from domain.user.aggregate import User
from domain.user.repository import UserRepository
from tests.factories.user import UserFactory


@pytest.mark.parametrize(
    "user",
    (UserFactory.build(),),
)
async def test_reply_returns_assistant_response_and_saves_messages(
    memory_user_repository: UserRepository,
    memory_conversation_history_repository: ConversationHistoryRepository,
    user: User,
):
    chat_client = AsyncMock()
    tool_dispatcher = Mock()

    await memory_user_repository.save(user)

    now = datetime.datetime.now(datetime.UTC)

    tools = [
        ToolDefinition(
            type="function",
            name="create_task",
            description="Create task",
            parameters={},
        )
    ]

    chat_client.chat.return_value = ChatResponse(
        content="Hello!",
        tool_calls=[],
    )

    tool_dispatcher.get_tool_definitions.return_value = tools

    service = AssistantService(
        user_repository=memory_user_repository,
        history_repository=memory_conversation_history_repository,
        chat_client=chat_client,
        tool_dispatcher=tool_dispatcher,
        prompt_builder=PromptBuilder(),
    )

    result = await service.reply(
        message="Hi",
        context=ToolContext(
            user_id=user.id,
            now=now,
        ),
    )

    assert result == "Hello!"

    messages = await memory_conversation_history_repository.get(user.id)

    assert len(messages) == 2

    assert messages == [
        ChatMessage(
            role="user",
            content="Hi",
            created_at=now,
        ),
        ChatMessage(
            role="assistant",
            content="Hello!",
            created_at=now,
        ),
    ]

    chat_client.chat.assert_awaited_once()

    kwargs = chat_client.chat.await_args.kwargs

    assert kwargs["messages"] == [
        ChatMessage(
            role="user",
            content="Hi",
            created_at=now,
        )
    ]

    assert kwargs["tools"] == tools


@pytest.mark.parametrize(
    "user",
    (UserFactory.build(),),
)
async def test_reply_executes_tool_and_then_returns_final_response(
    memory_user_repository: UserRepository,
    memory_conversation_history_repository: ConversationHistoryRepository,
    user: User,
):
    chat_client = AsyncMock()
    tool_dispatcher = AsyncMock()

    await memory_user_repository.save(user)

    now = datetime.datetime.now(datetime.UTC)

    chat_client.chat.side_effect = [
        ChatResponse(
            content="",
            tool_calls=[
                ToolCall(
                    id="call_1",
                    name="create_task",
                    arguments={
                        "title": "Buy milk",
                    },
                )
            ],
        ),
        ChatResponse(
            content="Task created",
            tool_calls=[],
        ),
    ]

    tool_dispatcher.dispatch.return_value = {"task_id": "123"}

    service = AssistantService(
        history_repository=memory_conversation_history_repository,
        user_repository=memory_user_repository,
        chat_client=chat_client,
        tool_dispatcher=tool_dispatcher,
        prompt_builder=PromptBuilder(),
    )

    result = await service.reply(
        message="Create task",
        context=ToolContext(
            user_id=user.id,
            now=now,
        ),
    )

    assert result == "Task created"

    tool_dispatcher.dispatch.assert_awaited_once_with(
        tool_name="create_task",
        raw_arguments={
            "title": "Buy milk",
        },
        context=ToolContext(
            user_id=user.id,
            now=now,
        ),
    )

    assert chat_client.chat.await_count == 2

    messages = await memory_conversation_history_repository.get(user.id)
    assert len(messages) == 4

    assert (
        ChatMessage(
            role="tool",
            content=str({"task_id": "123"}),
            tool_call_id="call_1",
            created_at=now,
        )
        in messages
    )


@pytest.mark.parametrize(
    "user",
    (UserFactory.build(),),
)
async def test_reply_uses_existing_history(
    memory_user_repository: UserRepository,
    memory_conversation_history_repository: ConversationHistoryRepository,
    user: User,
):
    chat_client = AsyncMock()
    tool_dispatcher = AsyncMock()

    await memory_user_repository.save(user)

    now = datetime.datetime.now(datetime.UTC)

    previous_message = ChatMessage(
        role="user",
        content="Previous",
        created_at=now,
    )
    await memory_conversation_history_repository.append(user.id, previous_message)

    chat_client.chat.return_value = ChatResponse(
        content="Answer",
        tool_calls=[],
    )

    service = AssistantService(
        history_repository=memory_conversation_history_repository,
        user_repository=memory_user_repository,
        chat_client=chat_client,
        tool_dispatcher=tool_dispatcher,
        prompt_builder=PromptBuilder(),
    )

    await service.reply(
        message="New message",
        context=ToolContext(
            user_id=user.id,
            now=now,
        ),
    )

    messages = await memory_conversation_history_repository.get(user.id)

    assert messages == [
        ChatMessage(
            role="user",
            content="Previous",
            created_at=now,
        ),
        ChatMessage(
            role="user",
            content="New message",
            created_at=now,
        ),
        ChatMessage(
            role="assistant",
            content="Answer",
            created_at=now,
        ),
    ]


@pytest.mark.parametrize(
    "user",
    (UserFactory.build(),),
)
async def test_reply_clears_history_when_ttl_expired(
    memory_user_repository: UserRepository,
    memory_conversation_history_repository: ConversationHistoryRepository,
    user: User,
):
    chat_client = AsyncMock()
    tool_dispatcher = AsyncMock()

    await memory_user_repository.save(user)

    now = datetime.datetime(
        2026,
        6,
        28,
        12,
        tzinfo=datetime.UTC,
    )

    old_message = ChatMessage(
        role="user",
        content="Old",
        created_at=datetime.datetime(
            2026,
            6,
            28,
            10,
            tzinfo=datetime.UTC,
        ),
    )

    await memory_conversation_history_repository.append(user.id, old_message)

    chat_client.chat.return_value = ChatResponse(
        content="New answer",
        tool_calls=[],
    )

    service = AssistantService(
        history_repository=memory_conversation_history_repository,
        user_repository=memory_user_repository,
        chat_client=chat_client,
        tool_dispatcher=tool_dispatcher,
        prompt_builder=PromptBuilder(),
    )

    await service.reply(
        message="Hello",
        context=ToolContext(
            user_id=user.id,
            now=now,
        ),
    )

    messages = await memory_conversation_history_repository.get(user.id)

    # old messages has cleared
    assert messages == [
        ChatMessage(
            role="user",
            content="Hello",
            created_at=now,
        ),
        ChatMessage(
            role="assistant",
            content="New answer",
            created_at=now,
        ),
    ]
