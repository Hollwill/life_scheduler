import datetime
import uuid

import pytest

from application.user.exceptions import UserNotFoundException
from application.user.queries import GetUserNowHandler, GetUserNowQuery
from domain.user.value_objects import TimeZone
from infrastructure.memory.repositories import MemoryUserRepository
from tests.factories.user import UserFactory


@pytest.mark.parametrize(
    ("timezone", "now", "expected_response"),
    (
        (
            TimeZone("Asia/Tokyo"),
            datetime.datetime.fromisoformat("2021-01-09T23:00:00+00:00"),
            "2021-01-10T08:00:00+09:00",
        ),
        (
            TimeZone("Europe/Berlin"),
            datetime.datetime.fromisoformat("2021-01-10T07:00:00+00:00"),
            "2021-01-10T08:00:00+01:00",
        ),
        (
            TimeZone("Europe/Moscow"),
            datetime.datetime.fromisoformat("2021-01-10T05:00:00+00:00"),
            "2021-01-10T08:00:00+03:00",
        ),
    ),
)
async def test_get_user_now_converts_now_to_user_timezone(
    memory_user_repository: MemoryUserRepository,
    timezone: TimeZone,
    now: datetime.datetime,
    expected_response: str,
):
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

    user = UserFactory.build(
        id=user_id,
        timezone=timezone,
    )

    await memory_user_repository.save(user)

    response = await GetUserNowHandler(
        user_repository=memory_user_repository,
    ).handle(
        GetUserNowQuery(
            user_id=user_id,
            now=now,
        )
    )

    assert response == expected_response


async def test_get_user_now_raises_user_not_found(
    memory_user_repository: MemoryUserRepository,
):
    user_id = uuid.UUID("00000000-0000-0000-0000-000000000000")

    with pytest.raises(UserNotFoundException):
        await GetUserNowHandler(
            user_repository=memory_user_repository,
        ).handle(
            GetUserNowQuery(
                user_id=user_id,
                now=datetime.datetime.fromisoformat("2021-01-10T05:00:00+00:00"),
            )
        )
