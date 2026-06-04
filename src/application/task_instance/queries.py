import dataclasses
import datetime
import uuid

from pydantic import TypeAdapter

from application.common.base import QueryHandler
from application.task_instance.schemas import TaskInstanceResponse
from domain.task_instance.repository import TaskInstanceRepository


@dataclasses.dataclass
class GetTaskInstancesQuery:
    user_id: uuid.UUID
    day: datetime.date


class GetTaskInstancesHandler(
    QueryHandler[GetTaskInstancesQuery, TaskInstanceResponse]
):
    def __init__(self, task_instance_repository: TaskInstanceRepository) -> None:
        super().__init__()
        self.task_instance_repository = task_instance_repository

    async def handle(self, query: GetTaskInstancesQuery) -> list[TaskInstanceResponse]:
        task_instances = await self.task_instance_repository.get_all_by_user_per_day(
            user_id=query.user_id, day=query.day
        )

        return TypeAdapter(list[TaskInstanceResponse]).validate_python(
            TaskInstanceResponse(
                public_id=task_instance.public_id,
                title=task_instance.title,
                description=task_instance.description,
                occurrence_date=task_instance.occurrence_date,
                scheduled_at=task_instance.scheduled_at,
                status=task_instance.status.value,
            )
            for task_instance in task_instances
        )
