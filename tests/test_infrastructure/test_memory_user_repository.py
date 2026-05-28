import uuid

import pytest

from domain.user.aggregate import User
from infrastructure.repositories.memory_user_repository import MemoryUserRepository
from tests.factories.user import UserFactory


@pytest.mark.parametrize("user", (UserFactory.build(),))
async def test_memory_user_repository_save_and_get(user: User):
    repo = MemoryUserRepository()

    await repo.save(user)
    retrieved = await repo.get_by_id(user.id)

    assert retrieved is not None
    assert retrieved.id == user.id
    assert retrieved.name == user.name
    assert retrieved is not user  # Deepcopy check


async def test_memory_user_repository_get_none():
    repo = MemoryUserRepository()
    retrieved = await repo.get_by_id(uuid.uuid4())
    assert retrieved is None


@pytest.mark.parametrize("user", (UserFactory.build(),))
@pytest.mark.parametrize(
    "name_to_change",
    ("Changed Name",),
)
async def test_memory_user_repository_deepcopy_isolation(
    user: User, name_to_change: str
):
    user_name = user.name
    repo = MemoryUserRepository()

    await repo.save(user)

    # Change original object
    user.name = name_to_change

    # Check that repo still has the original data
    retrieved = await repo.get_by_id(user.id)
    assert retrieved.name == user_name

    # Change retrieved object
    retrieved.name = name_to_change

    # Check that repo still has the original data
    retrieved_again = await repo.get_by_id(user.id)
    assert retrieved_again.name == user_name
