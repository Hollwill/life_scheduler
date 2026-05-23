import abc
import uuid

from domain.user.aggregate import User


class UserRepository(abc.ABC):

    @abc.abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        pass

    @abc.abstractmethod
    async def add(self, user: User) -> None:
        pass
