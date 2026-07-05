import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_dishka import setup_dishka
from sqlalchemy.ext.asyncio import AsyncEngine

from composition.container import container
from infrastructure.database.init_db import init_db
from infrastructure.logging import setup_logging

logger = logging.getLogger(__name__)


async def main():
    setup_logging()

    engine = await container.get(AsyncEngine)

    await init_db(engine)

    scheduler = await container.get(AsyncIOScheduler)

    setup_dishka(container=container, scheduler=scheduler)


if __name__ == "__main__":
    asyncio.run(main())
