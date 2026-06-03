import uuid
from unittest.mock import AsyncMock, Mock

import pytest
from aiogram.filters import CommandObject

from presentation.telegram.bot import (
    command_start_handler,
    create_daily,
    create_monthly,
    create_one_time,
    create_weekly,
    create_yearly,
    tasks,
    templates,
)


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
async def test_command_start_handler(user_id: uuid.UUID):
    message = AsyncMock()

    from_user = Mock()
    from_user.full_name = "John Doe"

    message.from_user = from_user

    await command_start_handler(
        message=message,
        user_id=user_id,
    )

    message.answer.assert_awaited_once()


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
async def test_templates_handler(user_id: uuid.UUID):
    message = AsyncMock()
    container = AsyncMock()

    command = CommandObject(
        prefix="/",
        command="templates",
    )

    get_task_templates_handler = AsyncMock()
    container.get.return_value = get_task_templates_handler

    await templates(
        message,
        command,
        dishka_container=container,  # noqa
    )  # noqa

    get_task_templates_handler.handle.assert_awaited_once()
    message.answer.assert_awaited_once()


@pytest.mark.parametrize(
    "user_id",
    (uuid.UUID("00000000-0000-0000-0000-000000000000"),),
)
async def test_tasks_handler(user_id: uuid.UUID):
    message = AsyncMock()
    container = AsyncMock()

    command = CommandObject(
        prefix="/",
        command="tasks",
    )

    get_task_instances_handler = AsyncMock()

    container.get.return_value = get_task_instances_handler

    await tasks(
        message,
        command,
        dishka_container=container,  # noqa
    )

    get_task_instances_handler.handle.assert_awaited_once()
    message.answer.assert_awaited_once()


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
async def test_create_daily_handler(user_id: uuid.UUID):
    message = AsyncMock()
    container = AsyncMock()

    command = CommandObject(
        prefix="/",
        command="create_daily",
        args="09:00 Drink water",
    )

    create_task_template_handler = AsyncMock()
    container.get.return_value = create_task_template_handler

    await create_daily(
        message,
        command,
        user_id=user_id,
        dishka_container=container,  # noqa
    )  # noqa

    create_task_template_handler.handle.assert_awaited_once()
    message.answer.assert_awaited_once()


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
async def test_create_one_time_handler(user_id: uuid.UUID):
    message = AsyncMock()
    container = AsyncMock()

    command = CommandObject(
        prefix="/",
        command="create_one_time",
        args="09:00 2026-01-10 Drink water",
    )

    create_task_template_handler = AsyncMock()
    container.get.return_value = create_task_template_handler

    await create_one_time(
        message,
        command,
        user_id=user_id,
        dishka_container=container,  # noqa
    )  # noqa

    create_task_template_handler.handle.assert_awaited_once()
    message.answer.assert_awaited_once()


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
async def test_create_weekly_handler(user_id: uuid.UUID):
    message = AsyncMock()
    container = AsyncMock()

    command = CommandObject(
        prefix="/",
        command="create_weekly",
        args="mon,tue Drink water",
    )

    create_task_template_handler = AsyncMock()
    container.get.return_value = create_task_template_handler

    await create_weekly(
        message,
        command,
        user_id=user_id,
        dishka_container=container,  # noqa
    )  # noqa

    create_task_template_handler.handle.assert_awaited_once()
    message.answer.assert_awaited_once()


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
async def test_create_monthly_handler(user_id: uuid.UUID):
    message = AsyncMock()
    container = AsyncMock()

    command = CommandObject(
        prefix="/",
        command="create_monthly",
        args="15 Drink water",
    )

    create_task_template_handler = AsyncMock()
    container.get.return_value = create_task_template_handler

    await create_monthly(
        message,
        command,
        user_id=user_id,
        dishka_container=container,  # noqa
    )  # noqa

    create_task_template_handler.handle.assert_awaited_once()
    message.answer.assert_awaited_once()


@pytest.mark.parametrize(
    "user_id", (uuid.UUID("00000000-0000-0000-0000-000000000000"),)
)
async def test_create_yearly_handler(user_id: uuid.UUID):
    message = AsyncMock()
    container = AsyncMock()

    command = CommandObject(
        prefix="/",
        command="create_yearly",
        args="jan 15 Drink water",
    )

    create_task_template_handler = AsyncMock()
    container.get.return_value = create_task_template_handler

    await create_yearly(
        message,
        command,
        user_id=user_id,
        dishka_container=container,  # noqa
    )  # noqa

    create_task_template_handler.handle.assert_awaited_once()
    message.answer.assert_awaited_once()
