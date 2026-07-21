import typing

from dishka import AsyncContainer, Scope

T = typing.TypeVar("T")


def create_job(
    container: AsyncContainer,
    handler_type: type[T],
    command_factory: typing.Callable[[], object] | None = None,
):
    async def wrapper():
        async with container(scope=Scope.REQUEST) as request:
            handler = await request.get(handler_type)

            handler_args = [command_factory()] if command_factory else []

            await handler.handle(*handler_args)

    wrapper.handler_type = handler_type  # type: ignore[attr-defined]

    return wrapper
