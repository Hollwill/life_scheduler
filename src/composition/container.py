from dishka import make_async_container

from composition.providers import (
    ApplicationProvider,
    DatabaseProvider,
    RepositoryProvider,
    SettingsProvider,
)

container = make_async_container(
    SettingsProvider(),
    DatabaseProvider(),
    RepositoryProvider(),
    ApplicationProvider(),
)
