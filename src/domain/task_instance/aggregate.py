import datetime
import uuid
from enum import Enum

from domain.common import AggregateRoot
from domain.task_instance.exceptions import (
    TaskInstanceInvalidPostponeDateException,
    TaskInstanceInvalidStatusException,
)


class TaskStatus(Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TaskInstance(AggregateRoot[uuid.UUID]):
    def __init__(
        self,
        id: uuid.UUID,
        task_template_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        description: str,
        occurrence_date: datetime.date,
        scheduled_at: datetime.datetime | None,
        created_at: datetime.datetime,
        status: TaskStatus,
        postpone_reason: str | None,
    ):
        super().__init__(id)
        self.task_template_id = task_template_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.occurrence_date = occurrence_date
        self.scheduled_at = scheduled_at
        self.created_at = created_at
        self.status = status
        self.postpone_reason = postpone_reason

    @classmethod
    def create(
        cls,
        task_template_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        description: str,
        occurrence_date: datetime.date,
        scheduled_at: datetime.datetime | None,
        now: datetime.datetime,
    ) -> "TaskInstance":
        return cls(
            id=uuid.uuid4(),
            task_template_id=task_template_id,
            user_id=user_id,
            title=title,
            description=description,
            occurrence_date=occurrence_date,
            scheduled_at=scheduled_at,
            created_at=now,
            status=TaskStatus.PENDING,
            postpone_reason=None,
        )

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
