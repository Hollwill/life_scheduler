import dataclasses

from application.common.base import CommandHandler
from application.common.unit_of_work import UnitOfWork
from application.task_instance.exceptions import TaskInstanceNotFoundException


@dataclasses.dataclass
class CompleteTaskInstanceCommand:
    task_instance_public_id: str


class CompleteTaskInstanceHandler(CommandHandler[CompleteTaskInstanceCommand, None]):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle(self, command: CompleteTaskInstanceCommand) -> None:
        async with self.uow:
            task_instance = await self.uow.task_instances.get_by_public_id(
                command.task_instance_public_id
            )
            if not task_instance:
                raise TaskInstanceNotFoundException(
                    {"task_instance_public_id": command.task_instance_public_id}
                )

            task_instance.complete()

            await self.uow.task_instances.save(task_instance)
