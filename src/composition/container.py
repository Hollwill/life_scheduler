from dishka import make_async_container

from composition.providers import (
    ApplicationAssistantProvider,
    ApplicationHandlersProvider,
    ApplicationOutboxProvider,
    ApplicationToolsProvider,
    DatabaseProvider,
    InfrastructureProvider,
    SchedulerProvider,
    SettingsProvider,
)

container = make_async_container(
    ApplicationHandlersProvider(),
    ApplicationAssistantProvider(),
    ApplicationToolsProvider(),
    ApplicationOutboxProvider(),
    DatabaseProvider(),
    InfrastructureProvider(),
    SchedulerProvider(),
    SettingsProvider(),
)
