import uuid

import pytest

from domain.user.aggregate import User
from infrastructure.memory.repositories.memory_user_repository import (
    MemoryUserRepository,
)
from tests.factories.user import UserFactory


@pytest.mark.parametrize("user", (UserFactory.build(),))
async def test_memory_user_repository_save_and_get(
    memory_user_repository: MemoryUserRepository, user: User
):

    await memory_user_repository.save(user)
    retrieved = await memory_user_repository.get_by_id(user.id)

    assert retrieved is not None
    assert retrieved.id == user.id
    assert retrieved.telegram_user_id == user.telegram_user_id
    assert retrieved.name == user.name
    assert retrieved is not user  # Deepcopy check


async def test_memory_user_repository_get_none(
    memory_user_repository: MemoryUserRepository,
):
    retrieved = await memory_user_repository.get_by_id(uuid.uuid4())
    assert retrieved is None


@pytest.mark.parametrize("user", (UserFactory.build(),))
@pytest.mark.parametrize(
    "name_to_change",
    ("Changed Name",),
)
async def test_memory_user_repository_deepcopy_isolation(
    memory_user_repository: MemoryUserRepository, user: User, name_to_change: str
):
    user_name = user.name

    await memory_user_repository.save(user)

    # Change original object
    user.name = name_to_change

    # Check that repo still has the original data
    retrieved = await memory_user_repository.get_by_id(user.id)
    assert retrieved.name == user_name

    # Change retrieved object
    retrieved.name = name_to_change

    # Check that repo still has the original data
    retrieved_again = await memory_user_repository.get_by_id(user.id)
    assert retrieved_again.name == user_name
