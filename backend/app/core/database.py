"""
Database configuration and session management for the Clinical Workstation.

Architectural Notes:
We use asynchronous SQLAlchemy 2.0 patterns rather than synchronous ORM to:
1. Maximize Concurrency: Asynchronous operations allow the server to handle other requests while waiting for database I/O, which is crucial for a scalable FastAPI application.
2. Prevent Blocking: Synchronous database calls in FastAPI can block the event loop if not carefully managed in thread pools, leading to performance degradation.
3. Align with Ecosystem: FastAPI is natively asynchronous. Using async database drivers (like aiosqlite) provides a consistent and idiomatic approach to building non-blocking endpoints.
"""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from .config import settings

# Create the async engine
# Note: check_same_thread=False is required for SQLite to allow multiple threads 
# to interact with the database, which is common in ASGI apps despite the async loop.
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Declarative base class for models
class Base(DeclarativeBase):
    pass

async def init_db() -> None:
    """Initialize the database by creating all tables."""
    from sqlalchemy import select
    from app.models.app_settings import AppSettings
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AppSettings).limit(1))
        existing = result.scalar_one_or_none()
        if not existing:
            # Fresh DB — seed all defaults
            for setting in AppSettings.default_settings():
                session.add(AppSettings(**setting))
        else:
            # Existing DB — upsert any missing keys
            existing_keys_result = await session.execute(select(AppSettings.key))
            existing_keys = {row[0] for row in existing_keys_result.all()}
            for setting in AppSettings.default_settings():
                if setting["key"] not in existing_keys:
                    session.add(AppSettings(**setting))
        await session.commit()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to yield a database session, commit on success, rollback on error,
    and ensure it is closed after the request.
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
