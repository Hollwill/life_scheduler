import datetime
import uuid
from dataclasses import dataclass

from domain.common.event import DomainEvent


@dataclass
class OutboxModel:
    id: uuid.UUID
    event_type: str
    payload: dict
    processed_at: datetime.datetime | None

    @classmethod
    def from_event(cls, event: DomainEvent) -> OutboxModel:
        return OutboxModel(
            id=uuid.uuid4(),
            event_type=event.event_type,
            payload=event.payload,
            processed_at=None,
        )
