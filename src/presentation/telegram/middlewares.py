from typing import Any

from aiogram import BaseMiddleware

from application.user.commands import GetOrCreateUserCommand, GetOrCreateUserHandler


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
