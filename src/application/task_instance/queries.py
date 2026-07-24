import dataclasses
import datetime
import uuid
from zoneinfo import ZoneInfo

from application.common.base import QueryHandler
from application.task_instance.schemas import TaskInstanceResponse
from domain.task_instance.repository import TaskInstanceRepository
from domain.user.repository import UserRepository


@dataclasses.dataclass
class GetTaskInstancesQuery:
    user_id: uuid.UUID
    day: datetime.date | None
    now: datetime.datetime


class GetTaskInstancesHandler(
    QueryHandler[GetTaskInstancesQuery, TaskInstanceResponse]
):
    def __init__(
        self,
        task_instance_repository: TaskInstanceRepository,
        user_repository: UserRepository,
    ) -> None:
        super().__init__()
        self.task_instance_repository = task_instance_repository
        self.user_repository = user_repository

    async def handle(self, query: GetTaskInstancesQuery) -> list[TaskInstanceResponse]:
        task_instances = await self.task_instance_repository.get_all_by_user(
            user_id=query.user_id, from_date=query.now.date(), to_date=query.day
        )
        user = await self.user_repository.get_by_id(query.user_id)

        task_instances_result = []
        for task_instance in task_instances:
            scheduled_at = None

            if task_instance.scheduled_at:
                scheduled_at = task_instance.scheduled_at.astimezone(
                    tz=ZoneInfo(user.timezone.value),
                )

            task_instances_result.append(
                TaskInstanceResponse(
                    public_id=task_instance.public_id,
                    title=task_instance.title,
                    description=task_instance.description,
                    occurrence_date=task_instance.occurrence_date,
                    scheduled_at=scheduled_at,
                    status=task_instance.status.value,
                )
            )

        return task_instances_result
