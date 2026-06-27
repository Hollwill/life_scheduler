from collections.abc import AsyncIterable

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from application.common.events import DispatchOutboxMessagesHandler, EventDispatcher
from application.common.notifiers import TelegramNotifier
from application.common.repositories import OutboxRepository
from application.common.tools.dispatcher import ToolDispatcher
from application.common.unit_of_work import UnitOfWork
from application.task_instance.commands import (
    CompleteTaskInstanceHandler,
    MissOverdueTaskInstancesHandler,
)
from application.task_instance.event_handlers import SendTelegramReminderHandler
from application.task_instance.queries import GetTaskInstancesHandler
from application.task_template.commands import (
    CreateTaskTemplateHandler,
    DeactivateTaskTemplateHandler,
)
from application.task_template.queries import GetTaskTemplatesHandler
from application.task_template.tools import CreateTaskTemplateTool
from application.user.commands import GetOrCreateUserHandler
from domain.task_instance.events import TaskReminderRequested
from domain.task_instance.repository import TaskInstanceRepository
from domain.task_template.repository import TaskTemplateRepository
from domain.user.repository import (
    UserRepository,
)
from infrastructure.database.repositories.outbox import SqlAlchemyOutboxRepository
from infrastructure.database.repositories.task_instance import (
    SqlAlchemyTaskInstanceRepository,
)
from infrastructure.database.repositories.task_template import (
    SqlAlchemyTaskTemplateRepository,
)
from infrastructure.database.repositories.user import (
    SqlAlchemyUserRepository,
)
from infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from infrastructure.notifiers import AiogramTelegramNotifier
from settings import Settings


class ApplicationProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_or_create_user_handler(
        self,
        uow: UnitOfWork,
    ) -> GetOrCreateUserHandler:

        return GetOrCreateUserHandler(
            uow=uow,
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
        user_repository: UserRepository,
    ) -> GetTaskInstancesHandler:

        return GetTaskInstancesHandler(
            task_instance_repository=task_instance_repository,
            user_repository=user_repository,
        )

    @provide(scope=Scope.REQUEST)
    def complete_task_instance_handler(
        self,
        uow: UnitOfWork,
    ) -> CompleteTaskInstanceHandler:

        return CompleteTaskInstanceHandler(uow=uow)

    @provide(scope=Scope.REQUEST)
    def deactivate_task_template_handler(
        self, uow: UnitOfWork
    ) -> DeactivateTaskTemplateHandler:

        return DeactivateTaskTemplateHandler(uow=uow)

    @provide(scope=Scope.REQUEST)
    def create_task_template_handler(
        self,
        uow: UnitOfWork,
    ) -> CreateTaskTemplateHandler:
        return CreateTaskTemplateHandler(uow=uow)

    @provide(scope=Scope.REQUEST)
    def get_event_dispatcher(
        self, uow: UnitOfWork, telegram_notifier: TelegramNotifier
    ) -> EventDispatcher:
        return EventDispatcher(
            handlers={
                TaskReminderRequested: [
                    SendTelegramReminderHandler(
                        uow=uow, telegram_notifier=telegram_notifier
                    ),
                ]
            }
        )

    @provide(scope=Scope.REQUEST)
    def get_outbox_messages_handler(
        self,
        outbox_repository: OutboxRepository,
        uow: UnitOfWork,
        dispatcher: EventDispatcher,
    ) -> DispatchOutboxMessagesHandler:
        return DispatchOutboxMessagesHandler(
            outbox_repository=outbox_repository, uow=uow, dispatcher=dispatcher
        )

    @provide(scope=Scope.REQUEST)
    def get_miss_overdue_task_instances_handler(
        self,
        uow: UnitOfWork,
    ) -> MissOverdueTaskInstancesHandler:
        return MissOverdueTaskInstancesHandler(uow=uow)

    @provide(scope=Scope.REQUEST)
    def get_create_task_template_tool(
        self, create_task_template_handler: CreateTaskTemplateHandler
    ) -> CreateTaskTemplateTool:
        return CreateTaskTemplateTool(handler=create_task_template_handler)

    @provide(scope=Scope.REQUEST)
    def get_tool_dispatcher(
        self,
        create_task_template_tool: CreateTaskTemplateTool,
    ) -> ToolDispatcher:

        return ToolDispatcher(
            tools={
                create_task_template_tool.name: create_task_template_tool,
            }
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
    def unit_of_work(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> UnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory)

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


class InfrastructureProvider(Provider):
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

    @provide(scope=Scope.REQUEST)
    def bot(self, settings: Settings) -> Bot:
        assert settings.telegram_bot_token

        return Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    @provide(scope=Scope.REQUEST)
    def telegram_notifier(self, bot: Bot) -> TelegramNotifier:
        return AiogramTelegramNotifier(
            bot=bot,
        )

    @provide(scope=Scope.REQUEST)
    def outbox_repository(
        self,
        session: AsyncSession,
    ) -> OutboxRepository:

        return SqlAlchemyOutboxRepository(
            session=session,
        )


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings()
