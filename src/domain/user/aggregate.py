import uuid

from domain.common import AggregateRoot


class User(AggregateRoot[uuid.UUID]):
    def __init__(self, id: uuid.UUID, telegram_user_id: int, name: str | None = None):
        (super().__init__(id),)
        self.telegram_user_id = telegram_user_id
        self.name = name

    @classmethod
    def create(cls, telegram_user_id: int, name: str | None = None) -> User:
        return cls(id=uuid.uuid4(), telegram_user_id=telegram_user_id, name=name)
