import datetime
import uuid

from pydantic import BaseModel


class TaskInstanceResponse(BaseModel):
    id: uuid.UUID

    title: str
    description: str | None

    occurrence_date: datetime.date
    scheduled_at: datetime.datetime | None

    status: str
