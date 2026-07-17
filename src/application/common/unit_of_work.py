import abc

from application.common.repositories import OutboxRepository
from domain.common.event import Event
from domain.task_instance.repository import TaskInstanceRepository
from domain.task_template.repository import TaskTemplateRepository
from domain.user.repository import UserRepository


class UnitOfWork(abc.ABC):
    def __init__(self):
        # Репозитории инстанцируются в __aenter__
        self._task_instances: TaskInstanceRepository | None = None
        self._task_templates: TaskTemplateRepository | None = None
        self._users: UserRepository | None = None
        self._outbox: OutboxRepository | None = None

    @property
    def task_instances(self) -> TaskInstanceRepository:
        if self._task_instances is None:
            raise RuntimeError("Task instances repository is not initialized")
        return self._task_instances

    @property
    def task_templates(self) -> TaskTemplateRepository:
        if self._task_templates is None:
            raise RuntimeError("Task templates repository is not initialized")
        return self._task_templates

    @property
    def users(self) -> UserRepository:
        if self._users is None:
            raise RuntimeError("Users repository is not initialized")
        return self._users

    @property
    def outbox(self) -> OutboxRepository:
        if self._outbox is None:
            raise RuntimeError("Outbox repository is not initialized")
        return self._outbox

    @abc.abstractmethod
    async def commit(self) -> None: ...

    @abc.abstractmethod
    async def rollback(self) -> None: ...

    @abc.abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError

    @abc.abstractmethod
    def _collect_events(self) -> list[Event]:
        raise NotImplementedError
