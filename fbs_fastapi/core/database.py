"""
FBS FastAPI Database Layer

SQLAlchemy async database connectivity and session management.
Supports multi-database routing for solution isolation.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from typing import Dict, AsyncGenerator, Optional, Any
import logging
from contextlib import asynccontextmanager

from .config import config

logger = logging.getLogger(__name__)

# SQLAlchemy Base for all models
class Base(DeclarativeBase):
    """Modern SQLAlchemy DeclarativeBase for all FBS models"""
    pass

# Database engines cache
_engines: Dict[str, Any] = {}
_session_factories: Dict[str, async_sessionmaker[AsyncSession]] = {}

def get_database_url(database_name: Optional[str] = None) -> str:
    """
    Get database URL for specific database or default.

    Args:
        database_name: Optional database name (e.g., 'fbs_solution_db')

    Returns:
        Database URL string
    """
    if database_name:
        # For solution-specific databases, modify the base URL
        base_url = config.database_url
        # Replace the database name in the URL
        if 'fbs_system_db' in base_url:
            return base_url.replace('fbs_system_db', database_name)
        else:
            # Fallback: append to path
            return base_url + f'_{database_name}'

    return config.database_url

def get_engine(database_name: Optional[str] = None):
    """
    Get or create async engine for specific database.

    Args:
        database_name: Optional database name

    Returns:
        SQLAlchemy async engine
    """
    db_key = database_name or 'default'

    if db_key not in _engines:
        database_url = get_database_url(database_name)

        _engines[db_key] = create_async_engine(
            database_url,
            echo=config.database_echo,
            poolclass=NullPool,  # Disable connection pooling for async
        )

        logger.info(f"Created database engine for: {db_key}")

    return _engines[db_key]

def get_session_factory(database_name: Optional[str] = None) -> async_sessionmaker[AsyncSession]:
    """
    Get or create session factory for specific database.

    Args:
        database_name: Optional database name

    Returns:
        SQLAlchemy async session factory
    """
    db_key = database_name or 'default'

    if db_key not in _session_factories:
        engine = get_engine(database_name)
        _session_factories[db_key] = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    return _session_factories[db_key]

@asynccontextmanager
async def get_db_session(database_name: Optional[str] = None) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database sessions.

    Args:
        database_name: Optional database name

    Yields:
        AsyncSession: Database session
    """
    session_factory = get_session_factory(database_name)
    session = session_factory()

    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()

async def create_tables():
    """Create all database tables"""
    try:
        # Create tables for default database
        engine = get_engine()
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            # Import models to ensure they're registered with SQLAlchemy
            from ..models import models, dms_models, license_models
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

async def drop_tables():
    """Drop all database tables (for testing/cleanup)"""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise

async def check_database_health() -> Dict[str, Any]:
    """
    Check database connectivity and health.

    Returns:
        Dict with health status information
    """
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            # Simple query to test connectivity
            result = await conn.execute("SELECT 1")
            row = result.fetchone()

        return {
            'status': 'healthy',
            'database': config.database_url.split('/')[-1],
            'message': 'Database connection successful'
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            'status': 'unhealthy',
            'database': config.database_url.split('/')[-1],
            'error': str(e),
            'message': 'Database connection failed'
        }

# Export for easy importing
__all__ = [
    'Base',
    'get_engine',
    'get_session_factory',
    'get_db_session',
    'create_tables',
    'drop_tables',
    'check_database_health'
]
