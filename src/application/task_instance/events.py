import dataclasses
import typing

from application.common.events import ApplicationEvent


@dataclasses.dataclass(
    frozen=True,
)
class ReminderNotificationRequested(ApplicationEvent):
    task_instance_id: str

    event_type: typing.ClassVar[str] = "task_instance.task_reminder_requested"
