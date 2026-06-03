import asyncio
import datetime

from dishka import Scope

from application.task_template.commands import (
    GenerateTasksForDayCommand,
    GenerateTasksForDayHandler,
)
from composition.container import container
from domain.task_instance.repository import TaskInstanceRepository
from domain.task_instance.service import TaskGenerationService
from domain.task_template.repository import TaskTemplateRepository


async def main():
    async with container(scope=Scope.REQUEST) as request_container:
        now = datetime.datetime.now()

        handler = GenerateTasksForDayHandler(
            task_template_repository=await request_container.get(
                TaskTemplateRepository
            ),
            task_instance_repository=await request_container.get(
                TaskInstanceRepository
            ),
            task_generation_service=await request_container.get(TaskGenerationService),
            now=now,
        )

        await handler.handle(GenerateTasksForDayCommand(day=now.date()))


if __name__ == "__main__":
    asyncio.run(main())
