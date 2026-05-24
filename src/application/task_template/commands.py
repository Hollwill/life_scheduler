import dataclasses
import datetime
import uuid

from application.common.commands import CommandHandler
from application.task_template.exceptions import (
    TaskTemplateNotFoundException,
    UserNotFoundException,
)
from domain.task_template.aggregate import TaskTemplate
from domain.task_template.entities import Trigger
from domain.task_template.repository import TaskTemplateRepository
from domain.user.repository import UserRepository


@dataclasses.dataclass
class CreateTaskTemplateCommand:
    user_id: uuid.UUID
    title: str
    description: str
    trigger: Trigger
    now: datetime.datetime


class CreateTaskTemplateHandler(CommandHandler[CreateTaskTemplateCommand, uuid.UUID]):
    def __init__(
        self,
        task_template_repository: TaskTemplateRepository,
        user_repository: UserRepository,
    ):
        self.task_template_repository = task_template_repository
        self.user_repository = user_repository

    async def handle(self, command: CreateTaskTemplateCommand) -> uuid.UUID:
        user = await self.user_repository.get_by_id(command.user_id)
        if user is None:
            raise UserNotFoundException({"user_id": command.user_id})

        task_template = TaskTemplate.create(
            user_id=user.id,
            title=command.title,
            description=command.description,
            trigger=command.trigger,
            now=command.now,
        )
        await self.task_template_repository.save(task_template)
        return task_template.id


@dataclasses.dataclass
class UpdateTaskTemplateCommand:
    task_template_id: uuid.UUID
    title: str
    description: str
    trigger: Trigger
    now: datetime.datetime


class UpdateTaskTemplateHandler(CommandHandler[UpdateTaskTemplateCommand, None]):
    def __init__(
        self,
        task_template_repository: TaskTemplateRepository,
    ):
        self.task_template_repository = task_template_repository

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
            trigger=command.trigger,
            now=command.now,
        )

        await self.task_template_repository.save(task_template)
