from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from insperion_api.config.database import DatabaseConfig
from insperion_api.settings.config import get_env

db_cfg = DatabaseConfig()


class AsyncDatabaseSession:
    pool_size = get_env("DB_POOL_SIZE", 10)
    max_overflow = get_env("DB_MAX_OVERFLOW", 10)

    engine = create_async_engine(
        DatabaseConfig().build_db_url(async_driver=True),
        pool_size=pool_size,
        max_overflow=max_overflow,
    )
    SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def __call__(self):
        return self.engine


get_async_engine = AsyncDatabaseSession()
