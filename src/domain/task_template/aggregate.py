import datetime
import uuid

from domain.common import AggregateRoot
from domain.task_template.entities import Trigger


class TaskTemplate(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        description: str,
        trigger: Trigger,
        is_active: bool,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
    ):
        super().__init__(id)
        self.user_id = user_id
        self.title = title
        self.description = description
        self.trigger = trigger
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def create(
        cls,
        user_id: uuid.UUID,
        title: str,
        description: str,
        trigger: Trigger,
        now: datetime.datetime,
    ):
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            description=description,
            trigger=trigger,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

    def occurs_on(self, day: datetime.date) -> bool:
        return self.trigger.occurs_on(day)

    def reminder_at(self, day: datetime.date) -> datetime.datetime | None:
        return self.trigger.reminder_at(day)

    def change_title(self, title: str, now: datetime.datetime) -> None:
        self.title = title
        self.updated_at = now

    def change_description(self, description: str, now: datetime.datetime) -> None:
        self.description = description
        self.updated_at = now

    def replace_trigger(self, trigger: Trigger, now: datetime.datetime) -> None:
        self.trigger = trigger
        self.updated_at = now

    def edit(
        self,
        now: datetime.datetime,
        title: str | None = None,
        description: str | None = None,
        trigger: Trigger | None = None,
    ) -> None:
        if title is not None:
            self.change_title(title, now)
        if description is not None:
            self.change_description(description, now)
        if trigger is not None:
            self.replace_trigger(trigger, now)

    def activate(self, now: datetime.datetime) -> None:
        self.is_active = True
        self.updated_at = now

    def deactivate(self, now: datetime.datetime) -> None:
        self.is_active = False
        self.updated_at = now
