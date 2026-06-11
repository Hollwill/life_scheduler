from dataclasses import dataclass

from domain.common.event import DomainEvent


@dataclass(
    frozen=True,
)
class TaskReminderRequested(DomainEvent):
    task_instance_id: str

    @property
    def event_type(self) -> str:
        return "task_instance.task_reminder_requested"
