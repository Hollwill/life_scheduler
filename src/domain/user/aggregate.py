import uuid

from domain.common import AggregateRoot


class User(AggregateRoot[uuid.UUID]):

    def __init__(self, id: uuid.UUID, name: str | None = None):
        super().__init__(id)
        self.name = name

    @classmethod
    def create(cls, name: str | None = None) -> User:
        return cls(id=uuid.uuid4(), name=name)
