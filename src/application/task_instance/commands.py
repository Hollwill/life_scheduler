import dataclasses

from application.common.base import CommandHandler
from application.task_instance.exceptions import TaskInstanceNotFoundException
from domain.task_instance.repository import TaskInstanceRepository


@dataclasses.dataclass
class CompleteTaskInstanceCommand:
    task_instance_public_id: str


class CompleteTaskInstanceHandler(CommandHandler[CompleteTaskInstanceCommand, None]):
    def __init__(self, task_instance_repository: TaskInstanceRepository) -> None:
        self.task_instance_repository = task_instance_repository

    async def handle(self, command: CompleteTaskInstanceCommand) -> None:
        task_instance = await self.task_instance_repository.get_by_public_id(
            command.task_instance_public_id
        )
        if not task_instance:
            raise TaskInstanceNotFoundException(
                {"task_instance_public_id": command.task_instance_public_id}
            )

        task_instance.complete()

        await self.task_instance_repository.save(task_instance)
