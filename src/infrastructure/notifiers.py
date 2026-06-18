import logging
from collections import defaultdict

from aiogram import Bot

from application.common.notifiers import TelegramNotifier

logger = logging.getLogger(__name__)


class AiogramTelegramNotifier(TelegramNotifier):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_message(self, telegram_id: int, text: str) -> None:
        await self.bot.send_message(chat_id=telegram_id, text=text)
        logger.info(
            "Message '%s' sent to user in telegram by id %s ", text, telegram_id
        )


class FakeTelegramNotifier(TelegramNotifier):
    def __init__(self):
        self.sent_messages: dict[int, list[str]] = defaultdict(list)

    async def send_message(self, telegram_id: int, text: str) -> None:
        self.sent_messages[telegram_id].append(text)
