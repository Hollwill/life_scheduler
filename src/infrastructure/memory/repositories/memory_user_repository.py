import copy
import uuid

from domain.user.aggregate import User
from domain.user.repository import UserRepository


class MemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        user = self.users.get(user_id)
        if user is None:
            return None
        return copy.deepcopy(user)

    async def save(self, user: User) -> None:
        self.users[user.id] = copy.deepcopy(user)
