import pytest

from application.user.commands import GetOrCreateUserCommand, GetOrCreateUserHandler
from domain.user.aggregate import User
from infrastructure.memory.repositories import MemoryUserRepository
from tests.factories.user import UserFactory


@pytest.mark.parametrize("user", (UserFactory.build(),))
async def test_get_or_create_user(user: User):
    user_repository = MemoryUserRepository()
    await user_repository.save(user)

    handler = GetOrCreateUserHandler(user_repository=user_repository)

    command = GetOrCreateUserCommand(
        telegram_user_id=user.telegram_user_id, name=user.name
    )

    result = await handler.handle(command)

    assert result == user.id


@pytest.mark.parametrize("telegram_user_id", (123456789,))
@pytest.mark.parametrize(
    "name",
    ("Test User", None),
)
async def test_get_or_create_user_user_created(telegram_user_id: int, name: str | None):
    user_repository = MemoryUserRepository()

    handler = GetOrCreateUserHandler(user_repository=user_repository)

    command = GetOrCreateUserCommand(telegram_user_id=telegram_user_id, name=name)

    result = await handler.handle(command)

    user = await user_repository.get_by_id(result)

    assert user is not None
    assert user.telegram_user_id == telegram_user_id
    assert user.name == name
