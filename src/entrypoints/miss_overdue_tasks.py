import asyncio
import datetime
import logging

from dishka import Scope
from sqlalchemy.ext.asyncio import AsyncEngine

from application.task_instance.commands import (
    MissOverdueTaskInstancesCommand,
    MissOverdueTaskInstancesHandler,
)
from composition.container import container
from infrastructure.database.init_db import init_db
from infrastructure.logging import setup_logging

logger = logging.getLogger(__name__)


async def main():
    setup_logging()
    async with container(scope=Scope.REQUEST) as request_container:
        now = datetime.datetime.now(tz=datetime.UTC)
        logger.info("Generating tasks for datetime %s", now.isoformat())

        handler = await request_container.get(MissOverdueTaskInstancesHandler)

        engine = await container.get(AsyncEngine)

        await init_db(engine)

        await handler.handle(MissOverdueTaskInstancesCommand(now=now))


if __name__ == "__main__":
    asyncio.run(main())
