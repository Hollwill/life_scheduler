import pytest

from domain.user.aggregate import User
from infrastructure.database.repositories.user import SqlAlchemyUserRepository
from tests.factories.user import UserFactory


@pytest.mark.parametrize("user", (UserFactory.build(),))
async def test_save_user(
    user: User,
    user_database_repository: SqlAlchemyUserRepository,
):
    await user_database_repository.save(
        user,
    )

    loaded = await user_database_repository.get_by_id(
        user.id,
    )

    assert loaded is not None
    assert loaded.id == user.id
    assert loaded.telegram_user_id == user.telegram_user_id
    assert loaded.name == user.name
