from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from insperion_api.utils.common.logger import logger


@asynccontextmanager
async def session_context(engine: AsyncEngine, client_name: str | None = None):
    if not client_name:
        logger.error("Client name not found in request headers or path params")

    session = AsyncSession(engine)
    schema_translate_map = {
        "agency": client_name,
    }
    await session.connection(
        execution_options={
            "schema_translate_map": schema_translate_map,
        }
    )
    session.info["schema_name"] = client_name
    try:
        yield session
    except Exception as ex:
        await session.rollback()
        logger.error(f"An error occurred during a transaction: {ex}")
        raise

    finally:
        await session.close()
