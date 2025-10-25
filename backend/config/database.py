"""
Database configuration and connection management.
Inspired by open-notebook's repository pattern, adapted for PostgreSQL with pgvector.
"""
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

load_dotenv()

# Database configuration from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://investment_user:investment_pass@localhost:5432/investment_ai")
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "5"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))

# Base class for declarative models
Base = declarative_base()

# Global engine and session factory
engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create database engine."""
    global engine
    if engine is None:
        engine = create_async_engine(
            DATABASE_URL,
            echo=DATABASE_ECHO,
            pool_size=DATABASE_POOL_SIZE,
            max_overflow=DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,  # Verify connections before using
        )
        logger.info(f"Created database engine: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'configured'}")
    return engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create session factory."""
    global async_session_factory
    if async_session_factory is None:
        engine = get_engine()
        async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        logger.info("Created async session factory")
    return async_session_factory


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.
    
    Usage:
        async with get_db_session() as session:
            result = await session.execute(query)
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database: create tables and extensions."""
    from backend.models import Base as ModelsBase  # Import all models
    
    engine = get_engine()
    
    async with engine.begin() as conn:
        # Enable pgvector extension
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        logger.info("Enabled pgvector extension")
        
        # Create all tables
        await conn.run_sync(ModelsBase.metadata.create_all)
        logger.info("Created database tables")


async def close_db():
    """Close database connections."""
    global engine, async_session_factory
    
    if engine:
        await engine.dispose()
        logger.info("Closed database engine")
        engine = None
        async_session_factory = None


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage in routes:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()
    """
    async with get_db_session() as session:
        yield session


# Utility function for testing connection
async def test_connection() -> bool:
    """Test database connection."""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
