import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# ---------------------------------------------------------------------------
# Database configuration
# ---------------------------------------------------------------------------
#
# Defaults to local SQLite for development.
# For production, configure a PostgreSQL URL via the DATABASE_URL
# environment variable, for example:
#   postgresql+psycopg2://user:password@host:5432/dbname?sslmode=require
# ---------------------------------------------------------------------------

DEFAULT_SQLITE_URL = "sqlite:///./fhat.db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

engine_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    # SQLite dev/CI
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # For PostgreSQL or other engines, rely on DATABASE_URL parameters
    # such as sslmode=require for encrypted connections.
    # Additional SSL options can be wired here if needed.
    pass

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
