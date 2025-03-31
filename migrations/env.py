from logging.config import fileConfig
import os
import re

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from alembic.script import ScriptDirectory

# Import app model bases
from utils.database import Base, get_database_url

# Import model classes to register them with the Base
import apps.user.models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set the database URL from environment variable
config.set_main_option('sqlalchemy.url', get_database_url())

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def process_revision_directives(context, revision, directives):
    """
    Override the revision ID to use sequential numbers (0001, 0002, etc.).
    """
    # Extract Migration script
    if not directives:
        return
        
    migration_script = directives[0]
    
    # Get the version directory
    versions_dir = os.path.join(os.path.dirname(__file__), 'versions')
    if not os.path.exists(versions_dir):
        os.makedirs(versions_dir)
    
    # List files in versions directory
    files = os.listdir(versions_dir)
    
    # Extract existing revision numbers from filenames
    # Looking for patterns like 0001_*, 0002_*, etc.
    numbers = []
    pattern = r'^(\d{4})_.*\.py$'
    for filename in files:
        match = re.match(pattern, filename)
        if match:
            numbers.append(int(match.group(1)))
    
    # Determine the next number
    if numbers:
        next_rev_id = max(numbers) + 1
    else:
        next_rev_id = 1
    
    # Set the revision ID with leading zeros
    migration_script.rev_id = f"{next_rev_id:04d}"


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
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
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
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
