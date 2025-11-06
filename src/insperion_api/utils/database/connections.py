from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from insperion_api.config.database import DatabaseConfig
from insperion_api.settings.config import settings

db_cfg = DatabaseConfig()


class AsyncDatabaseSession:
    pool_size = settings.db_pool_size
    max_overflow = settings.db_max_overflow

    engine = create_async_engine(
        DatabaseConfig().build_db_url(async_driver=True),
        pool_size=pool_size,
        max_overflow=max_overflow,
    )
    SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def __call__(self):
        return self.engine


get_async_engine = AsyncDatabaseSession()
