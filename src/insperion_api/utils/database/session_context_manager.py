from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from insperion_api.utils.common.logger import logger


@asynccontextmanager
async def session_context(engine: AsyncEngine):
    session = AsyncSession(engine)
    try:
        yield session
    except Exception as ex:
        await session.rollback()
        logger.error(f"An error occurred during a transaction: {ex}")
        raise

    finally:
        await session.close()
