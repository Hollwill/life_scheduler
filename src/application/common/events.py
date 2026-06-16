import abc

from application.common.repositories import OutboxRepository
from application.common.unit_of_work import UnitOfWork
from domain.common.event import DomainEvent
from domain.task_instance.events import TaskReminderRequested

EVENT_REGISTRY: dict[str, type[DomainEvent]] = {
    TaskReminderRequested.event_type: TaskReminderRequested,
}


class EventHandler[TEvent](abc.ABC):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @abc.abstractmethod
    async def handle(self, event: TEvent) -> None:
        pass


class EventDispatcher:
    def __init__(
        self,
        handlers: dict[type[DomainEvent], list[EventHandler]],
    ):
        self._handlers = handlers

    async def dispatch(
        self,
        event: DomainEvent,
    ) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler.handle(event)


class DispatchOutboxMessagesHandler:
    def __init__(
        self,
        outbox_repository: OutboxRepository,
        uow: UnitOfWork,
        dispatcher: EventDispatcher,
    ):
        self.outbox_repository = outbox_repository
        self.uow = uow
        self.dispatcher = dispatcher

    async def handle(
        self,
    ):
        outbox_messages = await self.outbox_repository.get_unprocessed()

        for message in outbox_messages:
            async with self.uow:
                event_cls = EVENT_REGISTRY[message.event_type]
                event = event_cls(**message.payload)

                await self.dispatcher.dispatch(event)

                message.mark_processed()
