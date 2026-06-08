import asyncio
import datetime

from dishka import Scope

from application.common.unit_of_work import UnitOfWork
from application.task_template.commands import (
    GenerateTasksForDayCommand,
    GenerateTasksForDayHandler,
)
from composition.container import container
from domain.task_instance.service import TaskGenerationService


async def main():
    async with container(scope=Scope.REQUEST) as request_container:
        now = datetime.datetime.now()

        handler = GenerateTasksForDayHandler(
            uow=await request_container.get(UnitOfWork),
            task_generation_service=await request_container.get(TaskGenerationService),
            now=now,
        )

        await handler.handle(GenerateTasksForDayCommand(day=now.date()))


if __name__ == "__main__":
    asyncio.run(main())
