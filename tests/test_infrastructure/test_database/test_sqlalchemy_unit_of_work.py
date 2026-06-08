import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.task_instance.aggregate import TaskInstance
from infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork
from tests.factories.task_instance import TaskInstanceFactory


async def test_uow_cannot_use_one_object_twice(
    session_factory: async_sessionmaker[AsyncSession],
):
    sqlalchemy_uow = SqlAlchemyUnitOfWork(session_factory)

    async with sqlalchemy_uow:
        pass

    with pytest.raises(RuntimeError):
        async with sqlalchemy_uow:
            pass


@pytest.mark.parametrize("task_instance", (TaskInstanceFactory.build(),))
async def test_uow_commit_persists_task_instance(
    session_factory: async_sessionmaker[AsyncSession], task_instance: TaskInstance
):
    task_instance_title = task_instance.title

    async with SqlAlchemyUnitOfWork(session_factory) as sqlalchemy_uow:
        await sqlalchemy_uow.task_instances.save(task_instance)
        await sqlalchemy_uow.commit()

    async with SqlAlchemyUnitOfWork(session_factory) as sqlalchemy_uow:
        loaded = await sqlalchemy_uow.task_instances.get_by_id(task_instance.id)

    assert loaded is not None
    assert loaded.title == task_instance_title


@pytest.mark.parametrize("task_instance", (TaskInstanceFactory.build(),))
async def test_uow_explicit_commit_by_default(
    session_factory: async_sessionmaker[AsyncSession], task_instance: TaskInstance
):
    task_id = task_instance.id
    task_instance_title = task_instance.title

    async with SqlAlchemyUnitOfWork(session_factory) as sqlalchemy_uow:
        await sqlalchemy_uow.task_instances.save(task_instance)
        # implicit commit

    async with SqlAlchemyUnitOfWork(session_factory) as sqlalchemy_uow:
        loaded = await sqlalchemy_uow.task_instances.get_by_id(task_id)

    assert loaded is not None
    assert loaded.title == task_instance_title


@pytest.mark.parametrize("task_instance", (TaskInstanceFactory.build(),))
async def test_uow_rollback_does_not_persist(
    session_factory: async_sessionmaker[AsyncSession], task_instance: TaskInstance
):
    task_id = task_instance.id

    try:
        async with SqlAlchemyUnitOfWork(session_factory) as sqlalchemy_uow:
            await sqlalchemy_uow.task_instances.save(task_instance)

            raise RuntimeError("error for transaction rollback")
    except RuntimeError:
        pass

    async with SqlAlchemyUnitOfWork(session_factory) as sqlalchemy_uow:
        loaded = await sqlalchemy_uow.task_instances.get_by_id(task_id)

    assert loaded is None


@pytest.mark.parametrize("task_instance", (TaskInstanceFactory.build(),))
async def test_uow_explicit_rollback_does_not_persist(
    session_factory: async_sessionmaker[AsyncSession], task_instance: TaskInstance
):
    task_id = task_instance.id

    async with SqlAlchemyUnitOfWork(session_factory) as sqlalchemy_uow:
        await sqlalchemy_uow.task_instances.save(task_instance)
        await sqlalchemy_uow.rollback()

    async with SqlAlchemyUnitOfWork(session_factory) as sqlalchemy_uow:
        loaded = await sqlalchemy_uow.task_instances.get_by_id(task_id)

    assert loaded is None
