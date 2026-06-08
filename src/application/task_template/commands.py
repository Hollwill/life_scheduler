import dataclasses
import datetime
import uuid

from application.common.base import CommandHandler
from application.common.unit_of_work import UnitOfWork
from application.task_template.exceptions import (
    TaskTemplateNotFoundException,
    UserNotFoundException,
)
from application.task_template.schemas import TriggerPayload
from application.task_template.trigger_mapper import TriggerMapper
from domain.task_instance.service import TaskGenerationService
from domain.task_template.aggregate import TaskTemplate
from domain.user.aggregate import User


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
        task_generation_service: TaskGenerationService,
        now: datetime.datetime,
    ) -> None:
        self.uow = uow
        self.task_generation_service = task_generation_service
        self.now = now

    async def handle(self, command: GenerateTasksForDayCommand) -> None:
        async with self.uow:
            task_templates = await self.uow.task_templates.get_all_active()

            today_task_instances = await self.uow.task_instances.get_all_by_day(
                command.day
            )

            exists_template_ids_for_day = {
                task_instance.task_template_id for task_instance in today_task_instances
            }

            for task_template in task_templates:
                if task_template.id in exists_template_ids_for_day:
                    continue

                task_instance = self.task_generation_service.generate_from_template(
                    task_template, day=command.day, now=self.now
                )
                if not task_instance:
                    continue

                await self.uow.task_instances.save(task_instance)
