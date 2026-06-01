import datetime
import uuid

from aiogram import Dispatcher, html
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka, inject

from application.task_template.commands import (
    CreateTaskTemplateHandler,
)
from presentation.telegram.decorators import parse_error_handle
from presentation.telegram.middlewares import (
    CommonErrorMiddleware,
    CurrentUserMiddleware,
)
from presentation.telegram.parsers import (
    parse_create_daily,
    parse_create_monthly,
    parse_create_one_time,
    parse_create_weekly,
    parse_create_yearly,
)

dp = Dispatcher()

dp.message.middleware(CurrentUserMiddleware())
dp.message.middleware(CommonErrorMiddleware())

# TODO: Написать еще middleware для перехвата исключений и ответа "что-то пошло не так".
# TODO: В идеале еще добавлять что-то вроде x-request-id чтобы по логам легче искать было.


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
@parse_error_handle(
    "/create_daily title",
    "/create_daily 09:00 title",
    "/create_daily 09:00 title | description",
    "/create_daily title | description",
)
@inject
async def create_daily(
    message: Message,
    command: CommandObject,
    user_id: uuid.UUID,
    create_task_template_handler: FromDishka[CreateTaskTemplateHandler],
):
    application_command = parse_create_daily(
        user_id=user_id,
        command_raw=command.args,
        now=datetime.datetime.now(tz=datetime.UTC),
    )

    await create_task_template_handler.handle(
        command=application_command,
    )

    await message.answer(f'Daily task "{application_command.title}" created.')


@dp.message(Command("create_one_time"))
@parse_error_handle(
    "/create_one_time 2021-01-10 title",
    "/create_one_time 09:00 2021-01-10 title",
    "/create_one_time 09:00 2021-01-10 title | description",
    "/create_one_time 2021-01-10 title | description",
)
@inject
async def create_one_time(
    message: Message,
    command: CommandObject,
    user_id: uuid.UUID,
    create_task_template_handler: FromDishka[CreateTaskTemplateHandler],
):

    application_command = parse_create_one_time(
        user_id=user_id,
        command_raw=command.args,
        now=datetime.datetime.now(tz=datetime.UTC),
    )

    await create_task_template_handler.handle(
        command=application_command,
    )

    await message.answer(f'One time task "{application_command.title}" created.')


@dp.message(Command("create_weekly"))
@parse_error_handle(
    "/create_weekly mon,tue title",
    "/create_weekly 09:00 mon,tue title",
    "/create_weekly 09:00 mon,tue title | description",
    "/create_weekly mon,tue title | description",
)
@inject
async def create_weekly(
    message: Message,
    command: CommandObject,
    user_id: uuid.UUID,
    create_task_template_handler: FromDishka[CreateTaskTemplateHandler],
):
    application_command = parse_create_weekly(
        user_id=user_id,
        command_raw=command.args,
        now=datetime.datetime.now(tz=datetime.UTC),
    )

    await create_task_template_handler.handle(command=application_command)

    await message.answer(f'Weekly task "{application_command.title}" created.')


@dp.message(Command("create_monthly"))
@parse_error_handle(
    "/create_monthly 15 title",
    "/create_monthly 09:00 15 title",
    "/create_monthly 09:00 15 title | description",
    "/create_monthly 15 title | description",
)
@inject
async def create_monthly(
    message: Message,
    command: CommandObject,
    user_id: uuid.UUID,
    create_task_template_handler: FromDishka[CreateTaskTemplateHandler],
):
    application_command = parse_create_monthly(
        user_id=user_id,
        command_raw=command.args,
        now=datetime.datetime.now(tz=datetime.UTC),
    )

    await create_task_template_handler.handle(command=application_command)

    await message.answer(f'Monthly task "{application_command.title}" created.')


@dp.message(Command("create_yearly"))
@parse_error_handle(
    "/create_yearly jan 15 title",
    "/create_yearly 09:00 jan 15 title",
    "/create_yearly 09:00 jan 15 title | description",
    "/create_yearly jan 15 title | description",
)
@inject
async def create_yearly(
    message: Message,
    command: CommandObject,
    user_id: uuid.UUID,
    create_task_template_handler: FromDishka[CreateTaskTemplateHandler],
):
    application_command = parse_create_yearly(
        user_id=user_id,
        command_raw=command.args,
        now=datetime.datetime.now(tz=datetime.UTC),
    )

    await create_task_template_handler.handle(command=application_command)

    await message.answer(f'Yearly task "{application_command.title}" created.')


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
