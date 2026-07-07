from dishka import make_async_container

from composition.providers import (
    ApplicationProvider,
    DatabaseProvider,
    InfrastructureProvider,
    SchedulerProvider,
    SettingsProvider,
)

container = make_async_container(
    SettingsProvider(),
    DatabaseProvider(),
    InfrastructureProvider(),
    SchedulerProvider(),
    ApplicationProvider(),
)
