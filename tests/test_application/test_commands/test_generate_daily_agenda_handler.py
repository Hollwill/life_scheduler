import datetime
import typing

import pytest

from application.task_instance.commands import (
    GenerateDailyAgendaCommand,
    GenerateDailyAgendaHandler,
)
from application.task_instance.events import (
    DailyAgendaRequested,
)
from domain.user.aggregate import User
from infrastructure.memory.repositories import (
    MemoryUserRepository,
)
from infrastructure.memory.unit_of_work import MemoryUnitOfWork
from tests.factories.user import UserFactory


@pytest.mark.parametrize(
    "now", (datetime.datetime.fromisoformat("2021-01-10T08:00:00"),)
)
@pytest.mark.parametrize("users", ((UserFactory.build(), UserFactory.build()),))
async def test_generate_task_reminders_handler_cases(
    memory_user_repository: MemoryUserRepository,
    memory_uow: MemoryUnitOfWork,
    users: typing.Iterable[User],
    now: datetime.datetime,
):
    for user in users:
        await memory_user_repository.save(user)

    handler = GenerateDailyAgendaHandler(uow=memory_uow)

    await handler.handle(GenerateDailyAgendaCommand(day=now.date()))

    outbox_records = await memory_uow.outbox.get_unprocessed()
    assert len(outbox_records) == 2
    assert all(
        outbox_record.event_type == DailyAgendaRequested.event_type
        for outbox_record in outbox_records
    )
    assert {outbox_record.payload["user_id"] for outbox_record in outbox_records} == {
        str(user.id) for user in users
    }
