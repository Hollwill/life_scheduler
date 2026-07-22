import datetime
import uuid

from application.task_instance.commands import (
    CreateTaskInstanceCommand,
    CreateTaskInstanceHandler,
)
from infrastructure.memory.unit_of_work import MemoryUnitOfWork


async def test_create_task_instance_handler(
    memory_uow: MemoryUnitOfWork,
    now: datetime.datetime,
):
    tomorrow = now + datetime.timedelta(days=1)

    handler = CreateTaskInstanceHandler(uow=memory_uow)
    command = CreateTaskInstanceCommand(
        user_id=uuid.uuid4(),
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
    assert task_instance.scheduled_at == tomorrow
    assert task_instance.user_id == command.user_id
    assert task_instance.created_at == now
