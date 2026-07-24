import dataclasses
import datetime
import typing
import uuid
from zoneinfo import ZoneInfo

from application.common.base import CommandHandler
from application.common.unit_of_work import UnitOfWork
from application.task_instance.events import (
    DailyAgendaRequested,
    ReminderNotificationRequested,
)
from application.task_instance.exceptions import TaskInstanceNotFoundException
from domain.common.aggregate_root import EMPTY, _Empty
from domain.task_instance.aggregate import TaskInstance
from domain.user.value_objects import TimeZone


@dataclasses.dataclass
class CreateTaskInstanceCommand:
    user_id: uuid.UUID
    title: str
    description: str | None
    occurrence_date: datetime.date
    scheduled_at: datetime.datetime | None
    now: datetime.datetime


class CreateTaskInstanceHandler(CommandHandler[CreateTaskInstanceCommand, None]):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle(self, command: CreateTaskInstanceCommand) -> None:
        async with self.uow:
            user = await self.uow.users.get_by_id(command.user_id)

            scheduled_at = self._calculate_scheduled_at(
                command.occurrence_date,
                command.scheduled_at,
                user.timezone,
            )
            task_instance = TaskInstance.create(
                task_template_id=None,
                user_id=command.user_id,
                title=command.title,
                description=command.description,
                occurrence_date=(
                    scheduled_at.date() if scheduled_at else command.occurrence_date
                ),  # TODO некрасивый костыль, надо поправить
                scheduled_at=scheduled_at,
                now=command.now,
            )
            await self.uow.task_instances.save(task_instance)

    # TODO Убрать дублирование преобразования
    @staticmethod
    def _calculate_scheduled_at(
        occurrence_date: datetime.date,
        scheduled_at: datetime.datetime | None,
        timezone: TimeZone,
    ) -> datetime.datetime | None:
        if not scheduled_at:
            return None

        local_datetime = datetime.datetime.combine(
            date=occurrence_date,
            time=scheduled_at.time(),
            tzinfo=ZoneInfo(timezone.value),
        )
        utc_reminder_time = local_datetime.astimezone(datetime.UTC)
        return utc_reminder_time


@dataclasses.dataclass
class UpdateTaskInstanceCommand:
    task_instance_public_id: str
    title: str | _Empty = EMPTY
    description: str | None | _Empty = EMPTY
    occurrence_date: datetime.date | _Empty = EMPTY
    scheduled_at: datetime.datetime | None | _Empty = EMPTY
    now: datetime.datetime | _Empty = EMPTY


class UpdateTaskInstanceHandler(
    CommandHandler[UpdateTaskInstanceCommand, dict[str, typing.Any]]
):
    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self.uow = uow

    async def handle(
        self,
        command: UpdateTaskInstanceCommand,
    ) -> dict[str, typing.Any]:
        async with self.uow:
            task_instance = await self.uow.task_instances.get_by_public_id(
                command.task_instance_public_id
            )

            if task_instance is None:
                raise TaskInstanceNotFoundException(
                    {
                        "task_instance_public_id": command.task_instance_public_id,
                    }
                )

            task_instance.edit(
                title=command.title,
                description=command.description,
                occurrence_date=command.occurrence_date,
                scheduled_at=command.scheduled_at,
            )

            await self.uow.task_instances.save(task_instance)

        return {
            "status": "success",
            "task_instance_public_id": task_instance.public_id,
        }


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
    now: datetime.datetime


class GenerateTaskRemindersHandler(CommandHandler[GenerateTaskRemindersCommand, None]):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle(self, command: GenerateTaskRemindersCommand) -> None:
        async with self.uow:
            for task_instance in await self.uow.task_instances.get_all_for_remind(
                now=command.now
            ):
                # produces reminder event
                task_instance.mark_reminded(now=command.now)
                await self.uow.task_instances.save(task_instance)
                await self.uow.outbox.save_from_event(
                    ReminderNotificationRequested(str(task_instance.id))
                )


@dataclasses.dataclass
class MissOverdueTaskInstancesCommand:
    now: datetime.datetime


class MissOverdueTaskInstancesHandler(
    CommandHandler[MissOverdueTaskInstancesCommand, None]
):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle(self, command: MissOverdueTaskInstancesCommand) -> None:
        async with self.uow:
            overdue_tasks = await self.uow.task_instances.get_all_overdue(
                now=command.now
            )

            for task in overdue_tasks:
                task.miss()
                await self.uow.task_instances.save(task)


@dataclasses.dataclass
class GenerateDailyAgendaCommand:
    day: datetime.date


class GenerateDailyAgendaHandler(CommandHandler[GenerateDailyAgendaCommand, None]):
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def handle(self, command: GenerateDailyAgendaCommand) -> None:
        async with self.uow:
            users = await self.uow.users.get_all()
            for user in users:
                await self.uow.outbox.save_from_event(
                    DailyAgendaRequested(
                        user_id=str(user.id), day=command.day.isoformat()
                    )
                )
