import dataclasses
import datetime

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


@dataclasses.dataclass
class GenerateTaskRemindersCommand:
    pass


class GenerateTaskRemindersHandler(CommandHandler[GenerateTaskRemindersCommand, None]):
    def __init__(self, uow: UnitOfWork, now: datetime.datetime) -> None:
        self.uow = uow
        self.now = now

    async def handle(self, command: GenerateTaskRemindersCommand) -> None:
        async with self.uow:
            for task_instance in await self.uow.task_instances.get_all_for_remind(
                now=self.now
            ):
                # produces reminder event
                task_instance.mark_reminded(now=self.now)
                await self.uow.task_instances.save(task_instance)


@dataclasses.dataclass
class MissOverdueTaskInstancesCommand:
    now: datetime.datetime


class MissOverdueTaskInstancesHandler(
    CommandHandler[MissOverdueTaskInstancesCommand, None]
):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle(self, command: MissOverdueTaskInstancesCommand) -> None:
        overdue_tasks = await self.uow.task_instances.get_all_overdue(now=command.now)

        for task in overdue_tasks:
            task.miss()
            await self.uow.task_instances.save(task)
