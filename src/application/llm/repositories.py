import abc
import typing
import uuid

from application.llm.models import ChatMessage


class ConversationHistoryRepository(abc.ABC):
    @abc.abstractmethod
    async def get(self, user_id: uuid.UUID) -> typing.Collection[ChatMessage]:
        raise NotImplementedError

    @abc.abstractmethod
    async def append(self, user_id: uuid.UUID, message: ChatMessage):
        raise NotImplementedError

    @abc.abstractmethod
    async def clear(self, user_id: uuid.UUID):
        raise NotImplementedError
