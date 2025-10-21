from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from insperion_api.config.database import DatabaseConfig

engine = create_engine(
    DatabaseConfig().build_db_url(async_driver=False),
)


def get_schemas():
    session = Session(engine)
    try:
        result = session.execute(text("SELECT name from config.agencies;"))

    # HACK: Excepts the 'table not found' error when this function is called
    # before the first migration executes. The first migration creates the
    # agencies table allowing this function to run successfully for subsequent
    # migrations.
    # A more elegant solution would be to conditionally skip calling this
    # function when the first migration is detected during `alembic upgrade head`
    except Exception:
        return []
    schemas = [row[0] for row in result]
    session.close()

    return schemas
