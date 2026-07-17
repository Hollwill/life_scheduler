import typing
import uuid

from application.llm.models import ChatMessage
from domain.common.event import Event
from domain.task_instance.aggregate import TaskInstance
from domain.task_template.aggregate import TaskTemplate
from domain.user.aggregate import User
from infrastructure.database.outbox import OutboxModel


class MemoryDatabase:
    def __init__(self):
        self.task_instances: dict[uuid.UUID, TaskInstance] = {}
        self.task_templates: dict[uuid.UUID, TaskTemplate] = {}
        self.users: dict[uuid.UUID, User] = {}
        self.outbox: dict[uuid.UUID, OutboxModel] = {}
        self.chat_messages_by_user: dict[uuid.UUID, list[ChatMessage]] = {}

    def collect_events(self) -> typing.Collection[Event]:
        events = []
        for entity in (
            *self.task_instances.values(),
            *self.task_templates.values(),
            *self.users.values(),
        ):
            events.extend(entity.flush_events())
        return events
