import uuid

import factory

from domain.user.aggregate import User
from domain.user.value_objects import TimeZone


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.LazyFunction(uuid.uuid4)
    telegram_user_id = factory.Sequence(lambda n: n)
    timezone = TimeZone("Europe/Moscow")
    name = factory.Sequence(lambda n: f"User-{n}")
