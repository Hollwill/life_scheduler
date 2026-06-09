from sqlalchemy.ext.asyncio import AsyncEngine

from infrastructure.database.orm import mapper_registry


async def init_db(
    engine: AsyncEngine,
):
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)
