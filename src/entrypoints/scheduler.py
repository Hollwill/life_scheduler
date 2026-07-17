import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from composition.container import container
from infrastructure.logging import setup_logging

logger = logging.getLogger(__name__)


async def main():
    setup_logging()

    scheduler = await container.get(AsyncIOScheduler)

    scheduler.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
