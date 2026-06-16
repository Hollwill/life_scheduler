import asyncio
import logging
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka.integrations.aiogram import setup_dishka
from sqlalchemy.ext.asyncio import AsyncEngine

from composition.container import container
from infrastructure.database.init_db import init_db
from infrastructure.logging import setup_logging
from presentation.telegram.bot import dp
from settings import Settings


async def main() -> None:
    setup_logging()

    settings = await container.get(Settings)

    if not settings.telegram_bot_token:
        raise ValueError("Telegram bot token is not set")

    engine = await container.get(AsyncEngine)

    await init_db(engine)  # TODO: Унести инициализацию БД в миграции через alembic

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    setup_dishka(
        container=container,
        router=dp,
    )

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
