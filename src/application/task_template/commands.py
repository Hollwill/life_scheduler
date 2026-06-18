import dataclasses
import datetime
import logging
import uuid
from itertools import groupby
from zoneinfo import ZoneInfo

from application.common.base import CommandHandler
from application.common.unit_of_work import UnitOfWork
from application.task_template.exceptions import (
    TaskTemplateNotFoundException,
    UserNotFoundException,
)
from application.task_template.schemas import TriggerPayload
from application.task_template.trigger_mapper import TriggerMapper
from domain.task_instance.aggregate import TaskInstance
from domain.task_template.aggregate import TaskTemplate
from domain.user.aggregate import User
from domain.user.value_objects import TimeZone

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class CreateTaskTemplateCommand:
    user_id: uuid.UUID
    title: str
    description: str | None
    trigger_payload: TriggerPayload
    now: datetime.datetime


class CreateTaskTemplateHandler(CommandHandler[CreateTaskTemplateCommand, str]):
    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self.uow: UnitOfWork = uow

    async def handle(self, command: CreateTaskTemplateCommand) -> str:
        async with self.uow:
            user: User | None = await self.uow.users.get_by_id(command.user_id)
            if user is None:
                raise UserNotFoundException({"user_id": command.user_id})

            task_template = TaskTemplate.create(
                user_id=user.id,
                title=command.title,
                description=command.description,
                trigger=TriggerMapper.to_domain(command.trigger_payload),
                now=command.now,
            )
            await self.uow.task_templates.save(task_template)
        return task_template.public_id


@dataclasses.dataclass
class UpdateTaskTemplateCommand:
    task_template_public_id: str
    title: str
    description: str | None
    trigger_payload: TriggerPayload
    now: datetime.datetime


class UpdateTaskTemplateHandler(CommandHandler[UpdateTaskTemplateCommand, None]):
    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self.uow: UnitOfWork = uow

    async def handle(self, command: UpdateTaskTemplateCommand) -> None:
        async with self.uow:
            task_template = await self.uow.task_templates.get_by_public_id(
                command.task_template_public_id
            )
            if task_template is None:
                raise TaskTemplateNotFoundException(
                    {"task_template_id": command.task_template_public_id}
                )

            task_template.edit(
                title=command.title,
                description=command.description,
                trigger=TriggerMapper.to_domain(command.trigger_payload),
                now=command.now,
            )

            await self.uow.task_templates.save(task_template)


@dataclasses.dataclass
class DeactivateTaskTemplateCommand:
    task_template_public_id: str
    now: datetime.datetime


class DeactivateTaskTemplateHandler(
    CommandHandler[DeactivateTaskTemplateCommand, None]
):
    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self.uow: UnitOfWork = uow

    async def handle(self, command: DeactivateTaskTemplateCommand) -> None:
        async with self.uow:
            task_template = await self.uow.task_templates.get_by_public_id(
                command.task_template_public_id
            )
            if task_template is None:
                raise TaskTemplateNotFoundException(
                    {"task_template_id": command.task_template_public_id}
                )

            task_template.deactivate(
                now=command.now,
            )

            await self.uow.task_templates.save(task_template)


@dataclasses.dataclass
class GenerateTasksForDayCommand:
    day: datetime.date


class GenerateTasksForDayHandler(CommandHandler[GenerateTasksForDayCommand, None]):
    def __init__(
        self,
        uow: UnitOfWork,
        now: datetime.datetime,
    ) -> None:
        self.uow = uow
        self.now = now

    async def handle(self, command: GenerateTasksForDayCommand) -> None:
        async with self.uow:
            task_templates = await self.uow.task_templates.get_all_active()

            task_templates = sorted(task_templates, key=lambda x: x.user_id)

            today_task_instances = await self.uow.task_instances.get_all_by_day(
                command.day
            )

            exists_template_ids_for_day = {
                task_instance.task_template_id for task_instance in today_task_instances
            }

            for user_id, user_task_templates in groupby(
                task_templates, key=lambda x: x.user_id
            ):
                user = await self.uow.users.get_by_id(user_id)
                assert user is not None

                for task_template in user_task_templates:
                    if task_template.id in exists_template_ids_for_day:
                        logger.info(
                            "Task not generated cause task for template %s already exists",
                            task_template.id,
                        )
                        continue
                    if not task_template.occurs_on(command.day):
                        logger.info(
                            "Task not generated cause template %s not occurs on %s",
                            task_template.id,
                            self.now.isoformat(),
                        )
                        continue

                    scheduled_at = self._calculate_scheduled_at(
                        command.day,
                        task_template.trigger.get_reminder_time(),
                        user.timezone,
                    )

                    task_instance = TaskInstance.create(
                        task_template_id=task_template.id,
                        user_id=task_template.user_id,
                        title=task_template.title,
                        description=task_template.description,
                        occurrence_date=command.day,
                        scheduled_at=scheduled_at,
                        now=self.now,
                    )

                    await self.uow.task_instances.save(task_instance)
                    logger.info(
                        "Generated task instance %s for task template %s on date %s, scheduled at %s",
                        task_instance.id,
                        task_template.id,
                        scheduled_at.isoformat() if scheduled_at else None,
                    )

    @staticmethod
    def _calculate_scheduled_at(
        day: datetime.date, reminder_time: datetime.time | None, timezone: TimeZone
    ) -> datetime.datetime | None:
        if not reminder_time:
            return None

        local_datetime = datetime.datetime.combine(
            date=day,
            time=reminder_time,
            tzinfo=ZoneInfo(timezone.value),
        )
        utc_reminder_time = local_datetime.astimezone(datetime.UTC)
        return utc_reminder_time
