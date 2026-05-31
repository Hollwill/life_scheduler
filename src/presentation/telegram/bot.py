import uuid

from aiogram import Dispatcher, html
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from application.task_template.commands import (
    CreateTaskTemplateCommand,
    CreateTaskTemplateHandler,
)
from presentation.telegram.middlewares import CurrentUserMiddleware

dp = Dispatcher()

dp.message.middleware(CurrentUserMiddleware())


@dp.message(CommandStart())
async def command_start_handler(message: Message, user_id: uuid.UUID) -> None:
    await message.answer(f"""
        Hello, {html.bold(message.from_user.full_name)}!
        Your id is {user_id}

        Commands:

        /templates
        /tasks
        /create_daily
        /create_weekly
        /create_monthly
        /create_yearly
        /create_one_time
        """)


@dp.message(Command("create_daily"))
async def create_daily(
    message: Message,
    user_id: uuid.UUID,
    create_task_template_handler: CreateTaskTemplateHandler,
):
    try:
        _, reminder_time, title = message.text.split(
            maxsplit=2,
        )
    except ValueError:
        await message.answer("Usage:\n/create_daily 09:00 Drink water")
        return

    await create_task_template_handler.handle(
        CreateTaskTemplateCommand(
            user_id=user_id,
            title=title,
            description=None,
            trigger_payload={
                "type": "DAILY",
                "reminder_time": reminder_time,
            },
        )
    )

    await message.answer(f'Daily task "{title}" created.')


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")
