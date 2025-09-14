"""
FBS FastAPI Test Configuration

Provides fixtures and configuration for comprehensive testing of all FBS components.
"""

import asyncio
import pytest
import os
from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Set up test environment variables BEFORE importing config
os.environ['SECRET_KEY'] = 'test_secret_key_for_testing_purposes_only'
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://test_user:test_password@localhost:5432/test_fbs_db'
os.environ['REDIS_URL'] = 'redis://localhost:6379/1'
os.environ['ODOO_URL'] = 'http://localhost:8069'
os.environ['ODOO_DB'] = 'test_odoo_db'
os.environ['APP_NAME'] = 'FBS Test'
os.environ['DEBUG'] = 'true'

# Add the project root to Python path for absolute imports
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import using absolute imports
try:
    from fbs_fastapi.core.config import config
    from fbs_fastapi.core.database import Base
    from fbs_fastapi.main import app
    IMPORTS_SUCCESSFUL = True
except ImportError as e:
    print(f"Warning: Import failed: {e}")
    # Create minimal mock objects for testing
    from unittest.mock import MagicMock
    config = MagicMock()
    Base = MagicMock()
    app = MagicMock()
    IMPORTS_SUCCESSFUL = False


# Test database configuration
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@localhost:5432/test_fbs_db"

# Test solution name
TEST_SOLUTION_NAME = "test_solution"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session


@pytest.fixture
def test_app() -> FastAPI:
    """Create test FastAPI application."""
    return app


@pytest.fixture
def test_client(test_app) -> TestClient:
    """Create test client."""
    return TestClient(test_app)


@pytest.fixture
def test_solution_name() -> str:
    """Test solution name fixture."""
    return TEST_SOLUTION_NAME


@pytest.fixture
def test_user_data() -> Dict[str, Any]:
    """Test user data fixture."""
    return {
        "user_id": "test_user_123",
        "email": "test@example.com",
        "name": "Test User",
        "solution_name": TEST_SOLUTION_NAME
    }


@pytest.fixture
def test_document_data() -> Dict[str, Any]:
    """Test document data fixture."""
    return {
        "name": "TEST-DOC-001",
        "title": "Test Document",
        "document_type_id": 1,
        "category_id": 1,
        "description": "Test document description",
        "confidentiality_level": "internal"
    }


@pytest.fixture
def test_license_data() -> Dict[str, Any]:
    """Test license data fixture."""
    return {
        "license_type": "professional",
        "expiry_date": "2025-12-31T23:59:59Z",
        "source": "test"
    }


@pytest.fixture
def test_msme_data() -> Dict[str, Any]:
    """Test MSME data fixture."""
    return {
        "business_type": "retail",
        "configuration": {
            "industry": "retail",
            "size": "small",
            "location": "test_location"
        }
    }


@pytest.fixture
def test_accounting_data() -> Dict[str, Any]:
    """Test accounting data fixture."""
    return {
        "entry_type": "income",
        "amount": 1000.00,
        "description": "Test income entry",
        "category": "sales",
        "payment_method": "bank_transfer"
    }


@pytest.fixture
def test_workflow_data() -> Dict[str, Any]:
    """Test workflow data fixture."""
    return {
        "workflow_type": "approval",
        "current_step": "draft",
        "business_id": "test_business_123",
        "metadata": {"priority": "high"}
    }


@pytest.fixture
async def initialized_services(test_solution_name):
    """Initialize all FBS services for testing."""
    from ..services.service_interfaces import FBSInterface

    fbs = FBSInterface(test_solution_name, "test_license_key")
    return fbs


# Custom test markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "functional: marks tests as functional tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )

