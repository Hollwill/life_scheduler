import uuid

from domain.common import AggregateRoot
from domain.user.value_objects import TimeZone


class User(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        telegram_user_id: int,
        timezone: TimeZone,
        name: str | None = None,
    ):
        (super().__init__(id),)
        self.telegram_user_id = telegram_user_id
        self.timezone = timezone
        self.name = name

    @classmethod
    def create(
        cls,
        telegram_user_id: int,
        timezone: TimeZone | None = None,
        name: str | None = None,
    ) -> User:
        if not timezone:
            timezone = TimeZone("UTC")
        return cls(
            id=uuid.uuid4(),
            telegram_user_id=telegram_user_id,
            timezone=timezone,
            name=name,
        )

    def set_timezone(self, timezone: TimeZone) -> None:

        self.timezone = timezone
