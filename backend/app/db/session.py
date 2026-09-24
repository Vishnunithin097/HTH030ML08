from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.config import settings

# Base Declarative Model
Base = declarative_base()

# Primary Production Engine using psycopg2
sync_engine = create_engine(
    settings.SYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

async_engine = sync_engine
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)
AsyncSessionLocal = SessionLocal

def get_async_db() -> Generator[Session, None, None]:
    """Dependency for providing database session to FastAPI route handlers."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_sync_db() -> Generator[Session, None, None]:
    """Context/Generator for providing sync database session to CLI scripts."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
