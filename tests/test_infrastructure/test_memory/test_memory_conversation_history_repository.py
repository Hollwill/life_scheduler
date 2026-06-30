import datetime
import uuid

import pytest

from application.llm.models import ChatMessage
from infrastructure.memory.database import MemoryDatabase
from infrastructure.memory.repositories.memory_conversation_history_repository import (
    MemoryConversationHistoryRepository,
)


@pytest.mark.parametrize(
    ("user_id", "expected_messages"),
    (
        (
            uuid.UUID("00000000-0000-0000-0000-000000000000"),
            [],
        ),
    ),
)
async def test_get_empty_history(
    user_id: uuid.UUID,
    expected_messages: list[ChatMessage],
):
    repository = MemoryConversationHistoryRepository(MemoryDatabase())

    messages = await repository.get(user_id)

    assert list(messages) == expected_messages


@pytest.mark.parametrize(
    ("user_id", "messages"),
    (
        (
            uuid.UUID("00000000-0000-0000-0000-000000000000"),
            [
                ChatMessage(
                    role="user",
                    content="Hello",
                    created_at=datetime.datetime.fromisoformat(
                        "2021-01-10T12:00:00+00:00"
                    ),
                ),
                ChatMessage(
                    role="assistant",
                    content="Hi!",
                    created_at=datetime.datetime.fromisoformat(
                        "2021-01-10T12:00:01+00:00"
                    ),
                ),
            ],
        ),
    ),
)
async def test_append_messages(
    user_id: uuid.UUID,
    messages: list[ChatMessage],
):
    repository = MemoryConversationHistoryRepository(MemoryDatabase())

    for message in messages:
        await repository.append(user_id, message)

    actual = await repository.get(user_id)

    assert list(actual) == messages


@pytest.mark.parametrize(
    ("user_id", "messages"),
    (
        (
            uuid.UUID("00000000-0000-0000-0000-000000000000"),
            [
                ChatMessage(
                    role="user",
                    content="Hello",
                    created_at=datetime.datetime.fromisoformat(
                        "2021-01-10T12:00:00+00:00"
                    ),
                ),
            ],
        ),
    ),
)
async def test_clear_history(
    user_id: uuid.UUID,
    messages: list[ChatMessage],
):
    repository = MemoryConversationHistoryRepository(MemoryDatabase())

    for message in messages:
        await repository.append(user_id, message)

    await repository.clear(user_id)

    actual = await repository.get(user_id)

    assert list(actual) == []


@pytest.mark.parametrize(
    ("existing_user_id", "another_user_id"),
    (
        (
            uuid.UUID("00000000-0000-0000-0000-000000000000"),
            uuid.UUID("00000000-0000-0000-0000-000000000001"),
        ),
    ),
)
async def test_clear_does_not_affect_other_users(
    existing_user_id: uuid.UUID,
    another_user_id: uuid.UUID,
):
    repository = MemoryConversationHistoryRepository(MemoryDatabase())

    message = ChatMessage(
        role="user",
        content="Hello",
        created_at=datetime.datetime.fromisoformat("2021-01-10T12:00:00+00:00"),
    )

    await repository.append(existing_user_id, message)
    await repository.append(another_user_id, message)

    await repository.clear(existing_user_id)

    assert list(await repository.get(existing_user_id)) == []
    assert list(await repository.get(another_user_id)) == [message]
