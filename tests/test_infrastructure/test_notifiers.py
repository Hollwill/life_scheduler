from unittest import mock

from infrastructure.notifiers import AiogramTelegramNotifier


async def test_aiogram_telegram_notifier():
    bot = mock.AsyncMock()

    notifier = AiogramTelegramNotifier(bot)

    await notifier.send_message(12345, "test")

    bot.send_message.assert_awaited_with(chat_id=12345, text="test")
