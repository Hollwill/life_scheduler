import asyncio

from dishka import Scope
from sqlalchemy.ext.asyncio import AsyncEngine

from application.common.events import DispatchOutboxMessagesHandler
from composition.container import container
from infrastructure.database.init_db import init_db
from infrastructure.logging import setup_logging


async def main():
    setup_logging()
    async with container(scope=Scope.REQUEST) as request_container:
        engine = await container.get(AsyncEngine)

        await init_db(engine)

        handler = await request_container.get(DispatchOutboxMessagesHandler)

        await handler.handle()


if __name__ == "__main__":
    asyncio.run(main())
