# !/bin/python3
# isort: skip_file
from logging import getLogger
from logging.config import fileConfig
from alembic.operations import ops
from alembic import context
from sqlalchemy import MetaData, engine_from_config, pool

from insperion_api.config.database import DatabaseConfig
from insperion_api.migrations.utils import (
    get_schemas,
)

from insperion_api.core.models.config.config import Base as ConfigBase
from insperion_api.core.models.agency.agency import Base as AgencyBase

schemas = get_schemas()
config = context.config
logger = getLogger("alembic")


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


config.set_main_option("sqlalchemy.url", DatabaseConfig().build_url_as_string())


target_metadata = [AgencyBase.metadata, ConfigBase.metadata]
merged_metadata = MetaData()

for tbl in ConfigBase.metadata.sorted_tables:
    tbl.tometadata(merged_metadata)


for schema in schemas:
    for tbl in AgencyBase.metadata.sorted_tables:
        tbl.tometadata(merged_metadata, schema=schema)


def process_revision_directives(context, revision, directives):
    """
    Adds schema creation statements to the top of the generated migration
    """
    if getattr(context.config.cmd_opts, "autogenerate", False):
        script = directives[0]

        upgrade_ops_container = script.upgrade_ops

        upgrade_ops_container.ops = [
            ops.ExecuteSQLOp(f"CREATE SCHEMA IF NOT EXISTS {schema};")
            for schema in schemas
        ] + upgrade_ops_container.ops


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        target_metadata=merged_metadata,
        transaction_per_migration=True,
        process_revision_directives=process_revision_directives,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        try:
            context.configure(
                connection=connection,
                target_metadata=merged_metadata,
                transaction_per_migration=True,
                process_revision_directives=process_revision_directives,
                include_schemas=True,
            )

            with context.begin_transaction():
                context.run_migrations()
        finally:
            logger.info("Trying to close database connection... ")
            connection.close()
            logger.info(
                "Connection Status post closing connection: closed"
                if connection.closed
                else "open"
            )


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
