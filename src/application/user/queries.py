import dataclasses
import datetime
import uuid

from application.common.base import QueryHandler
from application.user.exceptions import UserNotFoundException
from domain.user.repository import UserRepository


@dataclasses.dataclass
class GetUserNowQuery:
    user_id: uuid.UUID
    now: datetime.datetime


class GetUserNowHandler(QueryHandler[GetUserNowQuery, str]):
    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__()
        self.user_repository = user_repository

    async def handle(self, query: GetUserNowQuery) -> str:
        user = await self.user_repository.get_by_id(user_id=query.user_id)

        if not user:
            raise UserNotFoundException({"user_id": query.user_id})

        return query.now.astimezone(tz=user.timezone.to_zoneinfo()).isoformat()
