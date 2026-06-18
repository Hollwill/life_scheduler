from dishka import make_async_container

from composition.providers import (
    ApplicationProvider,
    DatabaseProvider,
    InfrastructureProvider,
    SettingsProvider,
)

container = make_async_container(
    SettingsProvider(),
    DatabaseProvider(),
    InfrastructureProvider(),
    ApplicationProvider(),
)
