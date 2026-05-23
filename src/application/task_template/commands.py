import dataclasses
import datetime
import uuid

from application.common.commands import CommandHandler
from application.task_template.exceptions import UserNotFoundException
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
            now=datetime.datetime.now(),
        )
        await self.task_template_repository.add(task_template)
        return task_template.id
