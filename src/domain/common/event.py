from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DomainEvent:
    @property
    def event_type(self) -> str:
        raise NotImplementedError

    @property
    def payload(self) -> dict:
        return asdict(self)
