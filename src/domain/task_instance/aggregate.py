import datetime
import uuid

from domain.common import AggregateRoot


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
        completed_at: datetime.datetime | None = None,
    ):
        super().__init__(id)
        self.task_template_id = task_template_id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.occurrence_date = occurrence_date
        self.scheduled_at = scheduled_at
        self.created_at = created_at
        self.completed_at = completed_at

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
        )

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    def complete(self, now: datetime.datetime) -> None:
        self.completed_at = now
