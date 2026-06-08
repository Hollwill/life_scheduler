import copy
import uuid

from domain.user.aggregate import User
from domain.user.repository import UserRepository
from infrastructure.memory.database import MemoryDatabase


class MemoryUserRepository(UserRepository):
    def __init__(self, db: MemoryDatabase) -> None:
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        user = self.db.users.get(user_id)
        if user is None:
            return None
        return copy.deepcopy(user)

    async def get_by_telegram_user_id(self, telegram_user_id: int) -> User | None:
        for user in self.db.users.values():
            if user.telegram_user_id == telegram_user_id:
                return copy.deepcopy(user)
        return None

    async def save(self, user: User) -> None:
        self.db.users[user.id] = copy.deepcopy(user)
