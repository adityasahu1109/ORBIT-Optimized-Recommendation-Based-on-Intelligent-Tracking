"""
SQLAlchemy engine, session factory, and database initialization.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from server.config import DB_URL

# Create the engine (single connection for SQLite)
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

# Session factory — use this to create new sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base for ORM models
Base = declarative_base()


def init_db():
    """Create all tables defined in ORM models."""
    from server.db.models import Interaction  # noqa: F401 — ensure model is registered
    print(f"Initializing database at {DB_URL}...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database ready.")


def get_db():
    """FastAPI dependency that yields a database session and auto-closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
