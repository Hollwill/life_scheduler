import datetime
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class ToolContext:
    user_id: uuid.UUID
    now: datetime.datetime
