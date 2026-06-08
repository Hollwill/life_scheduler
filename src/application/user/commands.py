import dataclasses
import uuid

from application.common.base import CommandHandler
from application.common.unit_of_work import UnitOfWork
from domain.user.aggregate import User


@dataclasses.dataclass
class GetOrCreateUserCommand:
    telegram_user_id: int
    name: str | None = None


class GetOrCreateUserHandler(CommandHandler[GetOrCreateUserCommand, uuid.UUID]):
    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self.uow = uow

    async def handle(self, command: GetOrCreateUserCommand) -> uuid.UUID:
        async with self.uow:
            user = await self.uow.users.get_by_telegram_user_id(
                command.telegram_user_id
            )

            if not user:
                user = User.create(
                    telegram_user_id=command.telegram_user_id, name=command.name
                )
                await self.uow.users.save(user)
            return user.id
