from application.common.events import (
    DispatchOutboxMessagesHandler,
    EventDispatcher,
    EventHandler,
)
from application.common.unit_of_work import UnitOfWork
from domain.task_instance.events import TaskReminderRequested
from infrastructure.database.outbox import OutboxModel
from infrastructure.memory.repositories.memory_outbox_repository import (
    MemoryOutboxRepository,
)
from infrastructure.memory.unit_of_work import MemoryUnitOfWork


class FakeHandler(EventHandler[TaskReminderRequested]):
    def __init__(self, uow: UnitOfWork):
        super().__init__(uow)
        self.events: list[TaskReminderRequested] = []

    async def handle(self, event: TaskReminderRequested) -> None:
        self.events.append(event)


class FakeDispatcher:
    def __init__(self):
        self.events = []

    async def dispatch(self, event):
        self.events.append(event)


async def test_event_dispatcher_calls_all_handlers(memory_uow: MemoryUnitOfWork):
    event = TaskReminderRequested(
        task_instance_id="123",
    )

    handler1 = FakeHandler(memory_uow)
    handler2 = FakeHandler(memory_uow)

    dispatcher = EventDispatcher(
        handlers={
            TaskReminderRequested: [
                handler1,
                handler2,
            ]
        }
    )

    await dispatcher.dispatch(event)

    assert handler1.events == [event]
    assert handler2.events == [event]


async def test_event_dispatcher_ignores_unknown_event():
    event = TaskReminderRequested(
        task_instance_id="123",
    )

    dispatcher = EventDispatcher(handlers={})

    await dispatcher.dispatch(event)


async def test_dispatch_outbox_messages(
    memory_outbox_repository: MemoryOutboxRepository,
    memory_uow: MemoryUnitOfWork,
):
    event = TaskReminderRequested(
        task_instance_id="123",
    )

    message = OutboxModel.from_event(event)

    dispatcher = FakeDispatcher()

    await memory_outbox_repository.save(message)

    handler = DispatchOutboxMessagesHandler(
        outbox_repository=memory_outbox_repository,
        uow=memory_uow,
        dispatcher=dispatcher,
    )

    await handler.handle()

    assert dispatcher.events == [event]

    messages = await memory_outbox_repository.get_unprocessed()

    assert messages == []


async def test_dispatch_outbox_messages_skips_processed(
    memory_outbox_repository: MemoryOutboxRepository,
    memory_uow: MemoryUnitOfWork,
):
    event = TaskReminderRequested(
        task_instance_id="123",
    )

    message = OutboxModel.from_event(event)
    message.mark_processed()

    await memory_outbox_repository.save(message)

    dispatcher = FakeDispatcher()

    handler = DispatchOutboxMessagesHandler(
        outbox_repository=memory_outbox_repository,
        uow=memory_uow,
        dispatcher=dispatcher,
    )

    await handler.handle()

    assert dispatcher.events == []


async def test_dispatch_outbox_restores_domain_event(
    memory_outbox_repository: MemoryOutboxRepository,
    memory_uow: MemoryUnitOfWork,
):
    event = TaskReminderRequested(
        task_instance_id="123",
    )

    message = OutboxModel.from_event(event)

    await memory_outbox_repository.save(message)

    dispatcher = FakeDispatcher()

    handler = DispatchOutboxMessagesHandler(
        outbox_repository=memory_outbox_repository,
        uow=memory_uow,
        dispatcher=dispatcher,
    )

    await handler.handle()

    restored_event = dispatcher.events[0]

    assert isinstance(
        restored_event,
        TaskReminderRequested,
    )
    assert restored_event.task_instance_id == "123"
