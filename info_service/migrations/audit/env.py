"""Alembic migration environment for Info Service — audit.db (log tables)."""

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import MetaData, engine_from_config, pool

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from sqlmodel import SQLModel  # noqa: E402

import info_service.models  # noqa: E402, F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

_AUDIT_TABLES = frozenset(
    {
        "audit_logs",
        "dead_letter_queue",
        "operation_logs",
    }
)

target_metadata = MetaData()
for table in SQLModel.metadata.sorted_tables:
    if table.name in _AUDIT_TABLES:
        table.tometadata(target_metadata)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
