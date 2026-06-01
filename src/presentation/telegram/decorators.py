from functools import wraps
from typing import Callable

from aiogram.utils.formatting import Bold, Text

from presentation.telegram.exceptions import ParseError


def parse_error_handle(*examples_list: str):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            message = args[0]

            try:
                return await func(*args, **kwargs)

            except ParseError as err:
                await message.answer(
                    **Text(
                        Bold("Invalid command format: "),
                        str(err),
                        "\n\n",
                        Bold("Examples:"),
                        "\n\n",
                        "\n\n".join(examples_list),
                    ).as_kwargs()
                )

        return wrapper

    return decorator
