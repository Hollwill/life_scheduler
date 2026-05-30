import datetime
from typing import Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.postgres import PostgresContainer

from infrastructure.database.base import Base
from infrastructure.database.repositories.task_instance import (
    SqlAlchemyTaskInstanceRepository,
)
from infrastructure.database.repositories.task_template import (
    SqlAlchemyTaskTemplateRepository,
)
from infrastructure.database.repositories.user import SqlAlchemyUserRepository


@pytest.fixture
def now() -> datetime.datetime:
    return datetime.datetime.now()


@pytest.fixture(scope="session", autouse=True)
def postgres_container() -> Generator[PostgresContainer, Any, None]:
    with PostgresContainer("postgres:18") as postgres:
        yield postgres


@pytest_asyncio.fixture
async def engine(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, Any]:
    engine = create_async_engine(
        postgres_container.get_connection_url(driver="asyncpg"),
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, Any]:
    async with session_factory() as session:
        yield session

        await session.rollback()


@pytest.fixture
def task_template_database_repository(
    session: AsyncSession,
) -> SqlAlchemyTaskTemplateRepository:
    return SqlAlchemyTaskTemplateRepository(session)


@pytest.fixture
def task_instance_database_repository(
    session: AsyncSession,
) -> SqlAlchemyTaskInstanceRepository:
    return SqlAlchemyTaskInstanceRepository(session)


@pytest.fixture
def user_database_repository(session: AsyncSession) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)
