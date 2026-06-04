from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from application.task_instance.queries import GetTaskInstancesHandler
from application.task_template.commands import (
    CreateTaskTemplateHandler,
    DeactivateTaskTemplateHandler,
)
from application.task_template.queries import GetTaskTemplatesHandler
from application.user.commands import GetOrCreateUserHandler
from domain.task_instance.repository import TaskInstanceRepository
from domain.task_instance.service import TaskGenerationService
from domain.task_template.repository import TaskTemplateRepository
from domain.user.repository import (
    UserRepository,
)
from infrastructure.database.repositories.task_instance import (
    SqlAlchemyTaskInstanceRepository,
)
from infrastructure.database.repositories.task_template import (
    SqlAlchemyTaskTemplateRepository,
)
from infrastructure.database.repositories.user import (
    SqlAlchemyUserRepository,
)
from settings import Settings


class DomainProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def task_generation_service_provider(
        self,
    ) -> TaskGenerationService:
        return TaskGenerationService()


class ApplicationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_or_create_user_handler(
        self,
        user_repository: UserRepository,
    ) -> GetOrCreateUserHandler:

        return GetOrCreateUserHandler(
            user_repository=user_repository,
        )

    @provide(scope=Scope.REQUEST)
    def get_task_templates_handler(
        self,
        task_template_repository: TaskTemplateRepository,
    ) -> GetTaskTemplatesHandler:
        return GetTaskTemplatesHandler(
            task_template_repository=task_template_repository
        )

    @provide(scope=Scope.REQUEST)
    def get_task_instances_handler(
        self,
        task_instance_repository: TaskInstanceRepository,
    ) -> GetTaskInstancesHandler:

        return GetTaskInstancesHandler(
            task_instance_repository=task_instance_repository,
        )

    @provide(scope=Scope.REQUEST)
    def deactivate_task_template_handler(
        self,
        task_template_repository: TaskTemplateRepository,
    ) -> DeactivateTaskTemplateHandler:

        return DeactivateTaskTemplateHandler(
            task_template_repository=task_template_repository,
        )

    @provide(scope=Scope.REQUEST)
    def create_task_template_handler(
        self,
        task_template_repository: TaskTemplateRepository,
        user_repository: UserRepository,
    ) -> CreateTaskTemplateHandler:
        return CreateTaskTemplateHandler(
            task_template_repository=task_template_repository,
            user_repository=user_repository,
        )


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def engine_provider(
        self,
        settings: Settings,
    ) -> AsyncEngine:
        return create_async_engine(str(settings.database_url), echo=False)

    @provide(scope=Scope.APP)
    def session_factory_provider(
        self,
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def session(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:

        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_repository(
        self,
        session: AsyncSession,
    ) -> UserRepository:

        return SqlAlchemyUserRepository(
            session=session,
        )

    @provide(scope=Scope.REQUEST)
    def task_template_repository(
        self,
        session: AsyncSession,
    ) -> TaskTemplateRepository:

        return SqlAlchemyTaskTemplateRepository(
            session=session,
        )

    @provide(scope=Scope.REQUEST)
    def task_instance_repository(
        self,
        session: AsyncSession,
    ) -> TaskInstanceRepository:

        return SqlAlchemyTaskInstanceRepository(
            session=session,
        )


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings()
