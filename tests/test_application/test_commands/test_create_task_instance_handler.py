import datetime

import pytest

from application.task_instance.commands import (
    CreateTaskInstanceCommand,
    CreateTaskInstanceHandler,
)
from domain.user.aggregate import User
from infrastructure.memory.repositories import MemoryUserRepository
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.user import UserFactory


@pytest.mark.parametrize("user", (UserFactory.build(),))
@pytest.mark.parametrize(
    "now", (datetime.datetime.fromisoformat("2021-01-10T10:00:00+00:00"),)
)
async def test_create_task_instance_handler(
    memory_uow: MemoryUnitOfWork,
    memory_user_repository: MemoryUserRepository,
    user: User,
    now: datetime.datetime,
):
    await memory_user_repository.save(user)
    tomorrow = now + datetime.timedelta(days=1)

    handler = CreateTaskInstanceHandler(uow=memory_uow)
    command = CreateTaskInstanceCommand(
        user_id=user.id,
        title="test",
        description="test",
        occurrence_date=tomorrow.date(),
        scheduled_at=tomorrow,
        now=now,
    )
    await handler.handle(command)

    task_instances = await memory_uow.task_instances.get_all_by_day(
        (now + datetime.timedelta(days=1)).date()
    )
    assert len(task_instances) == 1
    task_instance = next(iter(task_instances))
    assert task_instance.title == "test"
    assert task_instance.description == "test"
    assert task_instance.occurrence_date == tomorrow.date()
    assert task_instance.scheduled_at == datetime.datetime.fromisoformat(
        "2021-01-11T07:00:00+00:00"
    )
    assert task_instance.user_id == command.user_id
    assert task_instance.created_at == now
