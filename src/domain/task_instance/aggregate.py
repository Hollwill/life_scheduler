import datetime
import uuid
from enum import Enum

from domain.common import AggregateRoot
from domain.common.aggregate_root import EMPTY
from domain.common.utils import generate_public_id
from domain.task_instance.exceptions import (
    TaskInstanceInvalidPostponeDateException,
    TaskInstanceInvalidReminderDateException,
    TaskInstanceInvalidStatusException,
    TaskInstanceReminderTimeNotComeYet,
)


class TaskStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    MISSED = "MISSED"


class TaskInstance(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        public_id: str,
        task_template_id: uuid.UUID | None,
        user_id: uuid.UUID,
        title: str,
        description: str | None,
        occurrence_date: datetime.date,
        scheduled_at: datetime.datetime | None,
        created_at: datetime.datetime,
        status: TaskStatus,
        postpone_reason: str | None,
        reminded_at: datetime.datetime | None,
    ):
        super().__init__(id)
        self.public_id = public_id
        self.task_template_id = task_template_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.occurrence_date = occurrence_date
        self.scheduled_at = scheduled_at
        self.created_at = created_at
        self.status = status
        self.postpone_reason = postpone_reason
        self.reminded_at = reminded_at

    @classmethod
    def create(
        cls,
        task_template_id: uuid.UUID | None,
        user_id: uuid.UUID,
        title: str,
        description: str | None,
        occurrence_date: datetime.date,
        scheduled_at: datetime.datetime | None,
        now: datetime.datetime,
    ) -> "TaskInstance":
        return cls(
            id=uuid.uuid4(),
            public_id=generate_public_id(),
            task_template_id=task_template_id,
            user_id=user_id,
            title=title,
            description=description,
            occurrence_date=occurrence_date,
            scheduled_at=scheduled_at,
            created_at=now,
            status=TaskStatus.PENDING,
            postpone_reason=None,
            reminded_at=None,
        )

    def edit(
        self,
        title: str | object = EMPTY,
        description: str | None | object = EMPTY,
        occurrence_date: datetime.date | object = EMPTY,
        scheduled_at: datetime.datetime | None | object = EMPTY,
    ) -> None:
        if title is not EMPTY:
            assert isinstance(title, str)
            self.title = title
        if description is not EMPTY:
            assert isinstance(description, str | None)
            self.description = description
        if occurrence_date is not EMPTY:
            assert isinstance(occurrence_date, datetime.date)
            self.occurrence_date = occurrence_date
        if scheduled_at is not EMPTY:
            assert isinstance(scheduled_at, None | datetime.datetime)
            self.scheduled_at = scheduled_at

    @property
    def is_completed(self) -> bool:
        return self.status == TaskStatus.COMPLETED

    def complete(self) -> None:
        if self.status != TaskStatus.PENDING:
            raise TaskInstanceInvalidStatusException(
                context={"operation": "create", "status": self.status}
            )
        self.status = TaskStatus.COMPLETED

    def cancel(self) -> None:
        if self.status != TaskStatus.PENDING:
            raise TaskInstanceInvalidStatusException(
                context={"operation": "cancel", "status": self.status}
            )
        self.status = TaskStatus.CANCELLED

    def miss(self) -> None:
        if self.status != TaskStatus.PENDING:
            raise TaskInstanceInvalidStatusException(
                context={"operation": "miss", "status": self.status}
            )
        self.status = TaskStatus.MISSED

    def postpone(
        self,
        new_occurrence_date: datetime.date,
        now: datetime.datetime,
        reason: str | None = None,
    ) -> None:
        if self.status != TaskStatus.PENDING:
            raise TaskInstanceInvalidStatusException(
                context={"operation": "postpone", "status": self.status}
            )

        if new_occurrence_date <= now.date():
            raise TaskInstanceInvalidPostponeDateException(
                context={"new_date": new_occurrence_date, "today": now.date()}
            )

        self.occurrence_date = new_occurrence_date
        self.postpone_reason = reason

    def mark_reminded(self, now: datetime.datetime):
        if self.scheduled_at is None:
            return

        if self.reminded_at:
            return

        if self.status != TaskStatus.PENDING:
            raise TaskInstanceInvalidStatusException(
                context={"operation": "mark_reminded", "status": self.status}
            )
        if self.occurrence_date != now.date():
            raise TaskInstanceInvalidReminderDateException(
                context={
                    "reminder_date": self.occurrence_date.isoformat(),
                    "today": now.date().isoformat(),
                }
            )
        if self.scheduled_at is not None and now < self.scheduled_at:
            raise TaskInstanceReminderTimeNotComeYet(
                context={"reminder_time": self.scheduled_at}
            )

        self.reminded_at = now
