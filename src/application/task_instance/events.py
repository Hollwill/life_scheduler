import dataclasses
import typing

from application.common.events import ApplicationEvent


@dataclasses.dataclass(
    frozen=True,
)
class ReminderNotificationRequested(ApplicationEvent):
    event_type: typing.ClassVar[str] = "task_instance.task_reminder_requested"

    task_instance_id: str


@dataclasses.dataclass(
    frozen=True,
)
class DailyAgendaRequested(ApplicationEvent):
    event_type: typing.ClassVar[str] = "task_instance.daily_agenda_requested"

    user_id: str
    day: str
