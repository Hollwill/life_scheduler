import abc
import typing
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DomainEvent(abc.ABC):
    event_type: typing.ClassVar[str] = "define_it"

    @property
    def payload(self) -> dict:
        payload_dict = asdict(self)
        return payload_dict
