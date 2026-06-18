import abc


class TelegramNotifier(abc.ABC):
    @abc.abstractmethod
    async def send_message(
        self,
        telegram_id: int,
        text: str,
    ) -> None:
        pass
