import pytest

from domain.user.aggregate import User
from domain.user.value_objects import TimeZone
from tests.factories.user import UserFactory


@pytest.mark.parametrize(
    (
        "telegram_user_id",
        "timezone",
        "name",
    ),
    ((12345, TimeZone("Europe/Moscow"), "test"),),
)
def test_create_user(telegram_user_id: int, timezone: TimeZone, name: str):
    user = User.create(telegram_user_id=telegram_user_id, timezone=timezone, name=name)

    assert user.telegram_user_id == telegram_user_id
    assert user.name == name
    assert user.timezone == timezone


@pytest.mark.parametrize("user", (UserFactory.build(),))
@pytest.mark.parametrize("timezone", (TimeZone("Europe/Moscow"),))
def test_set_timezone(user: User, timezone: TimeZone):

    user.set_timezone(timezone)

    assert user.timezone == timezone
