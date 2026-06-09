import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.user.aggregate import User
from domain.user.repository import UserRepository
from infrastructure.database.orm import user_table


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(user_table.c.id == user_id)
        )
        return result.scalars().first()

    async def get_by_telegram_user_id(self, telegram_user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(user_table.c.telegram_user_id == telegram_user_id)
        )
        return result.scalars().first()

    async def save(self, user: User) -> None:
        instance = await self.session.get(User, user.id)

        if instance is None:
            self.session.add(user)
            return

        instance.telegram_user_id = user.telegram_user_id
        instance.name = user.name
