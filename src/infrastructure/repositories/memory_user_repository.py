import uuid

from domain.user.aggregate import User
from domain.user.repository import UserRepository


class MemoryUserRepository(UserRepository):

    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.users.get(user_id)

    async def add(self, user: User) -> None:
        self.users[user.id] = user
