import dataclasses
import uuid

from application.common.base import CommandHandler
from domain.user.aggregate import User
from domain.user.repository import UserRepository


@dataclasses.dataclass
class GetOrCreateUserCommand:
    telegram_user_id: int
    name: str | None = None


class GetOrCreateUserHandler(CommandHandler[GetOrCreateUserCommand, uuid.UUID]):
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def handle(self, command: GetOrCreateUserCommand) -> uuid.UUID:
        user = await self.user_repository.get_by_telegram_user_id(
            command.telegram_user_id
        )

        if not user:
            user = User.create(
                telegram_user_id=command.telegram_user_id, name=command.name
            )
            await self.user_repository.save(user)
        return user.id
