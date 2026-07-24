import copy

from domain.common.entity import Entity
from domain.common.event import DomainEvent


class _Empty:
    __slots__ = ()

    def __repr__(self) -> str:
        return "EMPTY"


EMPTY = _Empty()


class AggregateRoot[TId](Entity[TId]):
    def __init__(self, id: TId):
        super().__init__(id)
        self._events: list[DomainEvent] = []

    def add_event(self, event: DomainEvent):
        self._events.append(event)

    def flush_events(self) -> list[DomainEvent]:
        events = copy.copy(self._events)
        self._events.clear()
        return events
