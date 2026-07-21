import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import Scope
from testcontainers.postgres import PostgresContainer

from composition.container import container


@pytest.fixture(scope="function")
def monkeypatch_settings_envs(
    monkeypatch: pytest.MonkeyPatch, postgres_container: PostgresContainer
):
    for key, value in {
        "DATABASE_URL": postgres_container.get_connection_url(driver="asyncpg"),
        "TELEGRAM_BOT_TOKEN": "123456:ABCdefGhIJKlmNoPQRsTUVwxyZ",
        "PROXY_URL": "http://test.test:1234",
        "LLM_MODEL": "test",
        "LLM_API_KEY": "test",
        "LLM_BASE_URL": "test",
    }.items():
        monkeypatch.setenv(
            key,
            value,
        )


@pytest.mark.usefixtures("monkeypatch_settings_envs")
async def test_composition_builds_dependencies():
    async with container(scope=Scope.REQUEST) as request:
        for key in container.registry.factories:
            await request.get(key.type_hint, component=key.component)
        for key in request.registry.factories:
            await request.get(key.type_hint, component=key.component)


@pytest.mark.usefixtures("monkeypatch_settings_envs")
async def test_scheduler_building_correctly(
    postgres_container: PostgresContainer,
):
    async with container(scope=Scope.REQUEST) as request:
        scheduler = await request.get(AsyncIOScheduler)
        for job in scheduler.get_jobs():
            await request.get(job.func.handler_type)
