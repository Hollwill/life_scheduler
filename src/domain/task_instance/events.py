import typing
from dataclasses import dataclass

from domain.common.event import DomainEvent


@dataclass(
    frozen=True,
)
class TaskReminderRequested(DomainEvent):
    task_instance_id: str

    event_type: typing.ClassVar[str] = "task_instance.task_reminder_requested"
