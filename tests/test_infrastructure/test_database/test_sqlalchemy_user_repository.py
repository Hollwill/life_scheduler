import typing

import pytest

from domain.user.aggregate import User
from infrastructure.database.repositories.user import SqlAlchemyUserRepository
from tests.factories.user import UserFactory


@pytest.mark.parametrize(
    "users",
    ((UserFactory.build(), UserFactory.build()),),
)
async def test_sqlalchemy_user_repository_get_all(
    sqlalchemy_user_repository: SqlAlchemyUserRepository, users: typing.Iterable[User]
):

    for user in users:
        await sqlalchemy_user_repository.save(user)
    retrieved = await sqlalchemy_user_repository.get_all()

    assert retrieved is not None
    assert len(retrieved) == 2

    assert {user.id for user in retrieved} == {user.id for user in users}


@pytest.mark.parametrize("user", (UserFactory.build(),))
async def test_save_user(
    user: User,
    sqlalchemy_user_repository: SqlAlchemyUserRepository,
):
    await sqlalchemy_user_repository.save(
        user,
    )

    loaded = await sqlalchemy_user_repository.get_by_id(
        user.id,
    )

    assert loaded is not None
    assert loaded.id == user.id
    assert loaded.telegram_user_id == user.telegram_user_id
    assert loaded.name == user.name
    assert loaded.timezone == user.timezone
