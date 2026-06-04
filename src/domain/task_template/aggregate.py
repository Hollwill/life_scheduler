import datetime
import typing
import uuid

from domain.common import AggregateRoot
from domain.common.utils import generate_public_id
from domain.task_template.entities import Trigger

EMPTY = object()


class TaskTemplate(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        public_id: str,
        user_id: uuid.UUID,
        title: str,
        description: str | None,
        trigger: Trigger,
        is_active: bool,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
    ):
        super().__init__(id)
        self.public_id = public_id
        self.user_id: uuid.UUID = user_id
        self.title: str = title
        self.description: str | None = description
        self.trigger: Trigger = trigger
        self.is_active: bool = is_active
        self.created_at: datetime.datetime = created_at
        self.updated_at: datetime.datetime = updated_at

    @classmethod
    def create(
        cls,
        user_id: uuid.UUID,
        title: str,
        description: str | None,
        trigger: Trigger,
        now: datetime.datetime,
    ) -> typing.Self:
        return cls(
            id=uuid.uuid4(),
            public_id=generate_public_id(),
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

    def change_description(
        self, description: str | None, now: datetime.datetime
    ) -> None:
        self.description = description
        self.updated_at = now

    def replace_trigger(self, trigger: Trigger, now: datetime.datetime) -> None:
        self.trigger = trigger
        self.updated_at = now

    def edit(
        self,
        now: datetime.datetime,
        title: str | object = EMPTY,
        description: str | None | object = EMPTY,
        trigger: Trigger | object = EMPTY,
    ) -> None:
        if title is not EMPTY:
            assert isinstance(title, str)
            self.change_title(title, now)
        if description is not EMPTY:
            assert isinstance(description, str | None)
            self.change_description(description, now)
        if trigger is not EMPTY:
            assert isinstance(trigger, Trigger)
            self.replace_trigger(trigger, now)

    def activate(self, now: datetime.datetime) -> None:
        self.is_active = True
        self.updated_at = now

    def deactivate(self, now: datetime.datetime) -> None:
        self.is_active = False
        self.updated_at = now
