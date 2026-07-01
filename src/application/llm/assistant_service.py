import datetime
import logging
import uuid

from application.llm.chat_client import ChatClient
from application.llm.context import ToolContext
from application.llm.dispatcher import ToolDispatcher
from application.llm.models import ChatMessage
from application.llm.repositories import ConversationHistoryRepository
from domain.user.repository import UserRepository

logger = logging.getLogger(__name__)


class AssistantService:
    DIALOG_TTL = datetime.timedelta(hours=1)

    def __init__(
        self,
        user_repository: UserRepository,
        history_repository: ConversationHistoryRepository,
        chat_client: ChatClient,
        tool_dispatcher: ToolDispatcher,
    ) -> None:
        self._user_repository = user_repository
        self._history_repository = history_repository
        self._chat_client = chat_client
        self._tool_dispatcher = tool_dispatcher

    async def reply(
        self,
        message: str,
        context: ToolContext,
    ) -> str:
        logger.info("Replying to user %s with message: %s", context.user_id, message)
        user_id = context.user_id

        await self._clear_old_history(user_id, context.now)

        user_message = ChatMessage(
            role="user",
            content=message,
            created_at=context.now,
        )

        await self._history_repository.append(user_id, user_message)

        while True:
            history = await self._load_history(
                user_id=user_id,
                now=context.now,
            )

            response = await self._chat_client.chat(
                messages=history,
                tools=self._tool_dispatcher.get_tool_definitions(),
            )
            logger.info("Received response from LLM for history: %s", history)
            logger.info("Received response from LLM: %s", response.content)
            logger.info("Received tool calls: %s", response.tool_calls)

            assistant_message = ChatMessage(
                role="assistant",
                content=response.content,
                tool_calls=response.tool_calls if response.tool_calls else None,
                created_at=context.now,
            )

            await self._history_repository.append(
                user_id,
                assistant_message,
            )

            if not response.tool_calls:
                current_history = await self._history_repository.get(user_id)
                logger.info("Current history: %s", current_history)

                return response.content

            for tool_call in response.tool_calls:
                tool_result = await self._tool_dispatcher.dispatch(
                    tool_name=tool_call.name,
                    raw_arguments=tool_call.arguments,
                    context=context,
                )
                logger.info("Received %s tool result: %s", tool_call.name, tool_result)

                tool_message = ChatMessage(
                    role="tool",
                    tool_call_id=tool_call.id,
                    content=str(tool_result),
                    created_at=context.now,
                )

                await self._history_repository.append(
                    user_id,
                    tool_message,
                )

    async def _load_history(
        self,
        user_id: uuid.UUID,
        now: datetime.datetime,
    ) -> list[ChatMessage]:
        await self._clear_old_history(user_id, now)

        history = list(await self._history_repository.get(user_id))

        return history

    async def _clear_old_history(
        self,
        user_id: uuid.UUID,
        now: datetime.datetime,
    ):
        history = list(await self._history_repository.get(user_id))

        if history and now - history[-1].created_at > self.DIALOG_TTL:
            await self._history_repository.clear(user_id)
