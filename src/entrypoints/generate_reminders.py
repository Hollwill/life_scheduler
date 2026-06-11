import asyncio
import datetime

from dishka import Scope
from sqlalchemy.ext.asyncio import AsyncEngine

from application.common.unit_of_work import UnitOfWork
from application.task_instance.commands import (
    GenerateTaskRemindersCommand,
    GenerateTaskRemindersHandler,
)
from composition.container import container
from infrastructure.database.init_db import init_db


async def main():
    async with container(scope=Scope.REQUEST) as request_container:
        now = datetime.datetime.now(tz=datetime.UTC)

        handler = GenerateTaskRemindersHandler(
            uow=await request_container.get(UnitOfWork),
            now=now,
        )

        engine = await container.get(AsyncEngine)

        await init_db(engine)

        await handler.handle(GenerateTaskRemindersCommand())


if __name__ == "__main__":
    asyncio.run(main())
