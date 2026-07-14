import pytest

from application.user.commands import (
    SetUserTimezoneCommand,
    SetUserTimezoneHandler,
)
from domain.user.aggregate import User
from domain.user.value_objects import TimeZone
from infrastructure.memory.repositories import MemoryUserRepository
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.user import UserFactory


@pytest.mark.parametrize("user", (UserFactory.build(),))
@pytest.mark.parametrize("timezone", ("Europe/London",))
async def test_set_user_timezone(
    memory_uow: MemoryUnitOfWork,
    timezone: str,
    memory_user_repository: MemoryUserRepository,
    user: User,
):
    await memory_user_repository.save(user)

    handler = SetUserTimezoneHandler(uow=memory_uow)

    command = SetUserTimezoneCommand(user_id=user.id, timezone=timezone)

    result = await handler.handle(command)

    changed_user = await memory_user_repository.get_by_id(user.id)

    assert changed_user
    assert result == {"status": "success", "user_timezone": changed_user.timezone.value}
    assert changed_user.timezone == TimeZone(timezone)
