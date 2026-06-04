import datetime

from pydantic import BaseModel


class TaskInstanceResponse(BaseModel):
    public_id: str

    title: str
    description: str | None

    occurrence_date: datetime.date
    scheduled_at: datetime.datetime | None

    status: str
