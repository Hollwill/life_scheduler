import datetime
import uuid
from dataclasses import dataclass

from domain.common.event import Event


@dataclass
class OutboxModel:
    id: uuid.UUID
    event_type: str
    payload: dict
    processed_at: datetime.datetime | None

    @classmethod
    def from_event(cls, event: Event) -> OutboxModel:
        return OutboxModel(
            id=uuid.uuid4(),
            event_type=event.event_type,
            payload=event.payload,
            processed_at=None,
        )

    def mark_processed(self) -> None:
        self.processed_at = datetime.datetime.now()
