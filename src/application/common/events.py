import abc
import dataclasses

from application.common.repositories import OutboxRepository
from application.common.unit_of_work import UnitOfWork
from domain.common.event import Event


@dataclasses.dataclass(frozen=True)
class ApplicationEvent(Event, abc.ABC):
    pass


class EventHandler[TEvent](abc.ABC):
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @abc.abstractmethod
    async def handle(self, event: TEvent) -> None:
        pass


class EventDispatcher:
    def __init__(
        self,
        handlers: dict[type[Event], list[EventHandler]],
    ):
        self._handlers = handlers

    async def dispatch(
        self,
        event: Event,
    ) -> None:
        for handler in self._handlers.get(type(event), []):
            await handler.handle(event)


class DispatchOutboxMessagesHandler:
    def __init__(
        self,
        outbox_repository: OutboxRepository,
        uow: UnitOfWork,
        dispatcher: EventDispatcher,
        event_registry: dict[str, type[Event]],
    ):
        self.outbox_repository = outbox_repository
        self.uow = uow
        self.dispatcher = dispatcher
        self.event_registry = event_registry

    async def handle(
        self,
    ):
        outbox_messages = await self.outbox_repository.get_unprocessed()

        for message in outbox_messages:
            async with self.uow:
                event_cls = self.event_registry[message.event_type]
                event = event_cls(**message.payload)

                await self.dispatcher.dispatch(event)

                message.mark_processed()
