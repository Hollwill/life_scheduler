import datetime
from collections.abc import AsyncIterable

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer, Provider, Scope, provide
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from application.common.events import DispatchOutboxMessagesHandler, EventDispatcher
from application.common.notifiers import TelegramNotifier
from application.common.repositories import OutboxRepository
from application.common.unit_of_work import UnitOfWork
from application.llm.assistant_service import AssistantService
from application.llm.chat_client import ChatClient
from application.llm.dispatcher import ToolDispatcher
from application.llm.prompt_builder import PromptBuilder
from application.llm.repositories import ConversationHistoryRepository
from application.task_instance.commands import (
    CompleteTaskInstanceHandler,
    CreateTaskInstanceHandler,
    GenerateDailyAgendaCommand,
    GenerateDailyAgendaHandler,
    GenerateTaskRemindersCommand,
    GenerateTaskRemindersHandler,
    MissOverdueTaskInstancesCommand,
    MissOverdueTaskInstancesHandler,
)
from application.task_instance.event_handlers import (
    SendTelegramDailyAgendaHandler,
    SendTelegramReminderHandler,
)
from application.task_instance.events import (
    DailyAgendaRequested,
    ReminderNotificationRequested,
)
from application.task_instance.queries import GetTaskInstancesHandler
from application.task_instance.tools import (
    CompleteTaskInstanceTool,
    CreateTaskInstanceTool,
)
from application.task_template.commands import (
    CreateTaskTemplateHandler,
    DeactivateTaskTemplateHandler,
    GenerateTasksForDayCommand,
    GenerateTasksForDayHandler,
    UpdateTaskTemplateHandler,
)
from application.task_template.queries import GetTaskTemplatesHandler
from application.task_template.tools import (
    CreateTaskTemplateTool,
    DeactivateTaskTemplateTool,
    GetTaskTemplatesTool,
    UpdateTaskTemplateTool,
)
from application.user.commands import GetOrCreateUserHandler, SetUserTimezoneHandler
from application.user.tools import SetUserTimezoneTool
from composition.utils import create_job
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
from infrastructure.llm.openai_chat_client import OpenAIChatClient
from infrastructure.memory.database import MemoryDatabase
from infrastructure.memory.repositories.memory_conversation_history_repository import (
    MemoryConversationHistoryRepository,
)
from infrastructure.notifiers import AiogramTelegramNotifier
from settings import Settings


class ApplicationHandlersProvider(Provider):
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
    def create_task_instance_handler(
        self,
        uow: UnitOfWork,
    ) -> CreateTaskInstanceHandler:
        return CreateTaskInstanceHandler(uow=uow)

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
    def update_task_template_handler(
        self,
        uow: UnitOfWork,
    ) -> UpdateTaskTemplateHandler:
        return UpdateTaskTemplateHandler(uow=uow)

    @provide(scope=Scope.REQUEST)
    def get_miss_overdue_task_instances_handler(
        self,
        uow: UnitOfWork,
    ) -> MissOverdueTaskInstancesHandler:
        return MissOverdueTaskInstancesHandler(uow=uow)

    @provide(scope=Scope.REQUEST)
    def get_generate_task_reminders_handler(
        self,
        uow: UnitOfWork,
    ) -> GenerateTaskRemindersHandler:
        return GenerateTaskRemindersHandler(uow=uow)

    @provide(scope=Scope.REQUEST)
    def get_generate_daily_agenda_handler(
        self,
        uow: UnitOfWork,
    ) -> GenerateDailyAgendaHandler:
        return GenerateDailyAgendaHandler(uow=uow)

    @provide(scope=Scope.REQUEST)
    def get_generate_tasks_for_day_handler(
        self, uow: UnitOfWork
    ) -> GenerateTasksForDayHandler:
        return GenerateTasksForDayHandler(
            uow=uow,
        )

    @provide(scope=Scope.REQUEST)
    def get_set_user_timezone_handler(self, uow: UnitOfWork) -> SetUserTimezoneHandler:
        return SetUserTimezoneHandler(
            uow=uow,
        )


class ApplicationToolsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_tool_dispatcher(
        self,
        create_task_template_tool: CreateTaskTemplateTool,
        create_task_instance_tool: CreateTaskInstanceTool,
        update_task_template_tool: UpdateTaskTemplateTool,
        deactivate_task_template_tool: DeactivateTaskTemplateTool,
        get_task_templates_tool: GetTaskTemplatesTool,
        set_user_timezone_tool: SetUserTimezoneTool,
        complete_task_instance_tool: CompleteTaskInstanceTool,
    ) -> ToolDispatcher:

        return ToolDispatcher(
            tools={
                tool.name: tool
                for tool in [
                    create_task_template_tool,
                    create_task_instance_tool,
                    complete_task_instance_tool,
                    update_task_template_tool,
                    deactivate_task_template_tool,
                    get_task_templates_tool,
                    set_user_timezone_tool,
                ]
            }
        )

    @provide(scope=Scope.REQUEST)
    def get_create_task_template_tool(
        self, create_task_template_handler: CreateTaskTemplateHandler
    ) -> CreateTaskTemplateTool:
        return CreateTaskTemplateTool(handler=create_task_template_handler)

    @provide(scope=Scope.REQUEST)
    def get_create_task_instance_tool(
        self, create_task_instance_handler: CreateTaskInstanceHandler
    ) -> CreateTaskInstanceTool:
        return CreateTaskInstanceTool(handler=create_task_instance_handler)

    @provide(scope=Scope.REQUEST)
    def get_update_task_template_tool(
        self, update_task_template_handler: UpdateTaskTemplateHandler
    ) -> UpdateTaskTemplateTool:
        return UpdateTaskTemplateTool(handler=update_task_template_handler)

    @provide(scope=Scope.REQUEST)
    def provide_get_task_templates_tool(
        self, get_task_templates_handler: GetTaskTemplatesHandler
    ) -> GetTaskTemplatesTool:
        return GetTaskTemplatesTool(handler=get_task_templates_handler)

    @provide(scope=Scope.REQUEST)
    def provide_deactivate_task_template_tool(
        self, deactivate_task_template_handler: DeactivateTaskTemplateHandler
    ) -> DeactivateTaskTemplateTool:
        return DeactivateTaskTemplateTool(handler=deactivate_task_template_handler)

    @provide(scope=Scope.REQUEST)
    def provide_set_user_timezone_tool(
        self, set_user_timezone_handler: SetUserTimezoneHandler
    ) -> SetUserTimezoneTool:
        return SetUserTimezoneTool(handler=set_user_timezone_handler)

    @provide(scope=Scope.REQUEST)
    def provide_complete_task_instance_tool(
        self, complete_task_instance_handler: CompleteTaskInstanceHandler
    ) -> CompleteTaskInstanceTool:
        return CompleteTaskInstanceTool(handler=complete_task_instance_handler)


class ApplicationAssistantProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_chat_client(self, settings: Settings) -> ChatClient:
        assert settings.llm_model

        return OpenAIChatClient(
            client=AsyncOpenAI(
                base_url=settings.llm_base_url, api_key=settings.llm_api_key
            ),
            model=settings.llm_model,
        )

    @provide(scope=Scope.REQUEST)
    def get_prompt_builder(self) -> PromptBuilder:
        return PromptBuilder()

    @provide(scope=Scope.REQUEST)
    def get_assistant_service(
        self,
        user_repository: UserRepository,
        conversation_repository: ConversationHistoryRepository,
        chat_client: ChatClient,
        tool_dispatcher: ToolDispatcher,
        prompt_builder: PromptBuilder,
    ) -> AssistantService:

        return AssistantService(
            user_repository=user_repository,
            history_repository=conversation_repository,
            chat_client=chat_client,
            tool_dispatcher=tool_dispatcher,
            prompt_builder=prompt_builder,
        )


class ApplicationOutboxProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_outbox_messages_handler(
        self,
        outbox_repository: OutboxRepository,
        uow: UnitOfWork,
        dispatcher: EventDispatcher,
    ) -> DispatchOutboxMessagesHandler:
        return DispatchOutboxMessagesHandler(
            outbox_repository=outbox_repository,
            uow=uow,
            dispatcher=dispatcher,
            event_registry={
                event_cls.event_type: event_cls
                for event_cls in [
                    ReminderNotificationRequested,
                    DailyAgendaRequested,
                ]
            },
        )

    @provide(scope=Scope.REQUEST)
    def get_event_dispatcher(
        self, uow: UnitOfWork, telegram_notifier: TelegramNotifier
    ) -> EventDispatcher:
        return EventDispatcher(
            handlers={
                ReminderNotificationRequested: [
                    SendTelegramReminderHandler(
                        uow=uow, telegram_notifier=telegram_notifier
                    ),
                ],
                DailyAgendaRequested: [
                    SendTelegramDailyAgendaHandler(
                        uow=uow, telegram_notifier=telegram_notifier
                    )
                ],
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

    @provide(scope=Scope.APP)
    async def memory_db(
        self,
    ) -> MemoryDatabase:
        return MemoryDatabase()

    @provide(scope=Scope.REQUEST)
    async def conversation_repository(
        self,
        memory_db: MemoryDatabase,
    ) -> ConversationHistoryRepository:
        return MemoryConversationHistoryRepository(db=memory_db)

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
    def outbox_repository(
        self,
        session: AsyncSession,
    ) -> OutboxRepository:

        return SqlAlchemyOutboxRepository(
            session=session,
        )


class InfrastructureProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def bot(self, settings: Settings) -> Bot:
        assert settings.telegram_bot_token

        if settings.proxy_url:
            session = AiohttpSession(proxy=settings.proxy_url)
        else:
            session = AiohttpSession()

        return Bot(
            token=settings.telegram_bot_token,
            session=session,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    @provide(scope=Scope.REQUEST)
    def telegram_notifier(self, bot: Bot) -> TelegramNotifier:
        return AiogramTelegramNotifier(
            bot=bot,
        )


class SchedulerProvider(Provider):
    @provide(scope=Scope.APP)
    def get_scheduler(
        self,
        container: AsyncContainer,
    ) -> AsyncIOScheduler:
        scheduler = AsyncIOScheduler()

        scheduler.add_job(
            create_job(
                container,
                GenerateTaskRemindersHandler,
                lambda: GenerateTaskRemindersCommand(
                    now=datetime.datetime.now(tz=datetime.UTC),
                ),
            ),
            "interval",
            minutes=1,
            name="generate_task_reminders",
        )

        scheduler.add_job(
            create_job(
                container,
                GenerateDailyAgendaHandler,
                lambda: GenerateDailyAgendaCommand(day=datetime.date.today()),
            ),
            "cron",
            hour=2,
            minute=0,
            name="generate_daily_agenda",
        )

        scheduler.add_job(
            create_job(
                container,
                GenerateTasksForDayHandler,
                lambda: GenerateTasksForDayCommand(
                    day=datetime.date.today(),
                    now=datetime.datetime.now(tz=datetime.UTC),
                ),
            ),
            "interval",
            minutes=1,
            name="generate_tasks_for_day",
        )

        scheduler.add_job(
            create_job(
                container,
                MissOverdueTaskInstancesHandler,
                lambda: MissOverdueTaskInstancesCommand(
                    now=datetime.datetime.now(tz=datetime.UTC),
                ),
            ),
            "interval",
            hours=1,
            name="miss_overdue_task_instances",
        )

        scheduler.add_job(
            create_job(
                container,
                DispatchOutboxMessagesHandler,
            ),
            "interval",
            seconds=10,
            name="dispatch_outbox_messages",
        )

        return scheduler


class SettingsProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> Settings:
        return Settings()
