import abc

from application.llm.models import ChatMessage, ChatResponse, ToolDefinition


class ChatClient(abc.ABC):
    @abc.abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        tools: list[ToolDefinition],
    ) -> ChatResponse:
        pass
