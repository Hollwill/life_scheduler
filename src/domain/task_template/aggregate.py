import datetime
import uuid

from domain.common import AggregateRoot
from domain.task_template.entities import Trigger


class TaskTemplate(AggregateRoot[uuid.UUID]):
    title: str
    description: str | None

    trigger: Trigger

    active: bool

    created_at: datetime.datetime
    updated_at: datetime.datetime
