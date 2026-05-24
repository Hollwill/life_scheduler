import uuid

import pytest

from domain.user.aggregate import User
from infrastructure.repositories.memory_user_repository import MemoryUserRepository


@pytest.mark.parametrize(
    "name",
    [
        ("Test User"),
    ],
)
async def test_memory_user_repository_save_and_get(name: str):
    repo = MemoryUserRepository()
    user_id = uuid.uuid4()
    user = User(id=user_id, name=name)

    await repo.save(user)
    retrieved = await repo.get_by_id(user_id)

    assert retrieved is not None
    assert retrieved.id == user.id
    assert retrieved.name == user.name
    assert retrieved is not user  # Deepcopy check


async def test_memory_user_repository_get_none():
    repo = MemoryUserRepository()
    retrieved = await repo.get_by_id(uuid.uuid4())
    assert retrieved is None


@pytest.mark.parametrize(
    "name",
    [
        ("Original Name"),
    ],
)
async def test_memory_user_repository_deepcopy_isolation(name: str):
    repo = MemoryUserRepository()
    user = User(id=uuid.uuid4(), name=name)

    await repo.save(user)

    # Change original object
    user.name = "Changed Name"

    # Check that repo still has the original data
    retrieved = await repo.get_by_id(user.id)
    assert retrieved.name == name

    # Change retrieved object
    retrieved.name = "Changed Again"

    # Check that repo still has the original data
    retrieved_again = await repo.get_by_id(user.id)
    assert retrieved_again.name == name
