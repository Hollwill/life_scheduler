import typing
import uuid

from application.llm.models import ChatMessage
from application.llm.repositories import ConversationHistoryRepository
from infrastructure.memory.database import MemoryDatabase


class MemoryConversationHistoryRepository(ConversationHistoryRepository):
    def __init__(self, db: MemoryDatabase) -> None:
        self.db = db

    async def get(self, user_id: uuid.UUID) -> typing.Iterable[ChatMessage]:
        return self.db.chat_messages_by_user.get(user_id, [])

    async def append(self, user_id: uuid.UUID, message: ChatMessage):
        messages = self.db.chat_messages_by_user.get(user_id, [])

        messages.append(message)

        self.db.chat_messages_by_user[user_id] = messages

    async def clear(self, user_id: uuid.UUID):
        if self.db.chat_messages_by_user.get(user_id):
            del self.db.chat_messages_by_user[user_id]
