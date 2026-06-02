import dataclasses
import datetime
import uuid

from application.common.base import CommandHandler
from application.task_template.exceptions import (
    TaskTemplateNotFoundException,
    UserNotFoundException,
)
from application.task_template.schemas import TriggerPayload
from application.task_template.trigger_mapper import TriggerMapper
from domain.task_instance.repository import TaskInstanceRepository
from domain.task_instance.service import TaskGenerationService
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.repository import TaskTemplateRepository
from domain.user.aggregate import User
from domain.user.repository import UserRepository


@dataclasses.dataclass
class CreateTaskTemplateCommand:
    user_id: uuid.UUID
    title: str
    description: str | None
    trigger_payload: TriggerPayload
    now: datetime.datetime


class CreateTaskTemplateHandler(CommandHandler[CreateTaskTemplateCommand, uuid.UUID]):
    def __init__(
        self,
        task_template_repository: TaskTemplateRepository,
        user_repository: UserRepository,
    ) -> None:
        self.task_template_repository: TaskTemplateRepository = task_template_repository
        self.user_repository: UserRepository = user_repository

    async def handle(self, command: CreateTaskTemplateCommand) -> uuid.UUID:
        user: User | None = await self.user_repository.get_by_id(command.user_id)
        if user is None:
            raise UserNotFoundException({"user_id": command.user_id})

        task_template = TaskTemplate.create(
            user_id=user.id,
            title=command.title,
            description=command.description,
            trigger=TriggerMapper.to_domain(command.trigger_payload),
            now=command.now,
        )
        await self.task_template_repository.save(task_template)
        return task_template.id


@dataclasses.dataclass
class UpdateTaskTemplateCommand:
    task_template_id: uuid.UUID
    title: str
    description: str | None
    trigger_payload: TriggerPayload
    now: datetime.datetime


class UpdateTaskTemplateHandler(CommandHandler[UpdateTaskTemplateCommand, None]):
    def __init__(
        self,
        task_template_repository: TaskTemplateRepository,
    ) -> None:
        self.task_template_repository: TaskTemplateRepository = task_template_repository

    async def handle(self, command: UpdateTaskTemplateCommand) -> None:
        task_template = await self.task_template_repository.get_by_id(
            command.task_template_id
        )
        if task_template is None:
            raise TaskTemplateNotFoundException(
                {"task_template_id": command.task_template_id}
            )

        task_template.edit(
            title=command.title,
            description=command.description,
            trigger=TriggerMapper.to_domain(command.trigger_payload),
            now=command.now,
        )

        await self.task_template_repository.save(task_template)


@dataclasses.dataclass
class GenerateTasksForDayCommand:
    day: datetime.date


class GenerateTasksForDayHandler(CommandHandler[GenerateTasksForDayCommand, None]):
    def __init__(
        self,
        task_template_repository: TaskTemplateRepository,
        task_instance_repository: TaskInstanceRepository,
        task_generation_service: TaskGenerationService,
        now: datetime.datetime,
    ) -> None:
        self.task_template_repository = task_template_repository
        self.task_instance_repository = task_instance_repository
        self.task_generation_service = task_generation_service
        self.now = now

    async def handle(self, command: GenerateTasksForDayCommand) -> None:

        task_templates = await self.task_template_repository.get_all_active()

        today_task_instances = await self.task_instance_repository.get_all_by_day(
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

            await self.task_instance_repository.save(task_instance)
