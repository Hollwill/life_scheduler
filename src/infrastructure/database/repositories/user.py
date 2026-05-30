import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.user.aggregate import User
from domain.user.repository import UserRepository
from infrastructure.database.mappers import user_from_orm, user_to_orm
from infrastructure.database.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        instance = result.scalars().first()

        if instance is None:
            return None

        return user_from_orm(instance)

    async def save(self, user: User) -> None:
        instance = await self.session.get(UserModel, user.id)

        if instance is None:
            instance = user_to_orm(user)
            self.session.add(instance)
            return

        instance.name = user.name
