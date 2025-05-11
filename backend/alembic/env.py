import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base from your session.py and all your models
# This is crucial for Alembic's autogenerate feature
from app.db.session import Base # Adjusted path
from app.models.audit_model import Audit # Ensure this model is imported

# Set target_metadata to your Base.metadata
# For autogenerate support, Alembic needs to know about your models.
# When you create your first model (e.g., Audit), you'll uncomment the import above
# and ensure it's correctly imported here.
target_metadata = Base.metadata


def get_url():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        # This will happen if .env is not loaded or DATABASE_URL is not set
        # For local dev, ensure .env exists in backend/ and contains DATABASE_URL
        # For Heroku, DATABASE_URL is set by Heroku itself.
        print("DATABASE_URL not found. Attempting to load from alembic.ini as fallback for local init.")
        # Fallback to alembic.ini for initial setup if needed, though env var is preferred
        db_url = config.get_main_option("sqlalchemy.url")
        if not db_url or db_url == "driver://user:pass@localhost/dbname":
             raise ValueError("DATABASE_URL not set and alembic.ini sqlalchemy.url is not configured correctly.")

    if db_url and db_url.startswith("postgres://"): # Heroku uses postgres://
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    return db_url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_url()
    render_as_batch = url.startswith("sqlite") # Check if SQLite
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=render_as_batch # Enable batch mode for SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Construct the sqlalchemy.url from the DATABASE_URL environment variable
    # This ensures Alembic uses the same database URL as the application
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Enable batch mode for SQLite in online mode
    render_as_batch = connectable.dialect.name == "sqlite"

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            render_as_batch=render_as_batch # Enable batch mode for SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
