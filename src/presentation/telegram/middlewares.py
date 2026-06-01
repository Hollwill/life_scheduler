import logging
import uuid
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message

from application.user.commands import GetOrCreateUserCommand, GetOrCreateUserHandler

logger = logging.getLogger(__name__)


class CurrentUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event,
        data: dict[str, Any],
    ):
        user_handler = await data["dishka_container"].get(GetOrCreateUserHandler)
        user_id = await user_handler.handle(
            GetOrCreateUserCommand(telegram_user_id=event.from_user.id)
        )
        data["user_id"] = user_id
        return await handler(event, data)


class CommonErrorMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event: Message,
        data: dict[str, Any],
    ):
        try:
            return await handler(event, data)
        except Exception:
            error_id = uuid.uuid4()
            logger.exception(error_id)
            await event.answer(f"Something went wrong.\nError id: {error_id}.")
