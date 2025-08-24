"""
Comprehensive Pytest configuration for FBS Project tests.

This file configures pytest-django to support testing across all apps:
- fbs_app (core functionality)
- fbs_license_manager (licensing system)
- fbs_dms (document management)
- Integration testing between apps
- Cherry-picking scenarios
- Isolation architecture testing
"""

import pytest
import os
import tempfile
from pathlib import Path
from django.conf import settings
from django.test import override_settings

# Test database configuration
@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Override database setup to use SQLite for tests with multi-database support."""
    with django_db_blocker.unblock():
        # Configure test databases
        test_databases = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            },
            'licensing': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            },
            # Solution-specific test databases
            'djo_test_solution_db': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            },
            'fbs_test_solution_db': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        }
        
        # Override settings
        settings.DATABASES = test_databases
        yield

@pytest.fixture(scope='session')
def django_db_setup_teardown(django_db_setup):
    """Ensure proper database teardown after tests."""
    yield
    # Cleanup will be handled by pytest-django

# Test data fixtures
@pytest.fixture
def test_user(db):
    """Create a test user for authentication."""
    from django.contrib.auth.models import User
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    return user

@pytest.fixture
def test_company(db):
    """Create a test company for multi-tenant testing."""
    return {
        'id': 'test_company_001',
        'name': 'Test Company Inc.',
        'domain': 'testcompany.com'
    }

@pytest.fixture
def test_solution_config(db):
    """Create test solution configuration for isolation testing."""
    return {
        'name': 'test_solution',
        'django_db': 'djo_test_solution_db',
        'fbs_db': 'fbs_test_solution_db',
        'company_id': 'test_company_001'
    }

@pytest.fixture
def test_license_data(db):
    """Create test license data for licensing tests."""
    return {
        'solution_name': 'test_solution',
        'license_type': 'professional',
        'license_key': 'TEST-LICENSE-KEY-12345',
        'features': ['feature1', 'feature2', 'feature3'],
        'limits': {'feature1': {'count': 100}, 'feature2': {'count': 50}},
        'status': 'active',
        'source': 'test'
    }

@pytest.fixture
def test_document_data(db):
    """Create test document data for DMS tests."""
    return {
        'name': 'Test Document',
        'title': 'Test Document Title',
        'description': 'This is a test document for testing purposes',
        'confidentiality_level': 'internal',
        'metadata': {'test_key': 'test_value'}
    }

@pytest.fixture
def test_file_data(db):
    """Create test file data for file attachment tests."""
    return {
        'original_filename': 'test_document.pdf',
        'mime_type': 'application/pdf',
        'file_size': 1024 * 1024,  # 1MB
        'content': b'Test file content for testing purposes'
    }

# App-specific fixtures
@pytest.fixture
def fbs_app_interface(db, test_solution_config):
    """Create FBS app interface for testing."""
    try:
        from fbs_app.interfaces import FBSInterface
        return FBSInterface(test_solution_config['name'])
    except ImportError:
        pytest.skip("fbs_app not available")

@pytest.fixture
def license_manager(db, test_solution_config):
    """Create license manager for testing."""
    try:
        from fbs_license_manager.services import LicenseManager
        return LicenseManager(
            solution_name=test_solution_config['name'],
            license_key=test_license_data()['license_key']
        )
    except ImportError:
        pytest.skip("fbs_license_manager not available")

@pytest.fixture
def document_service(db, test_company):
    """Create document service for testing."""
    try:
        from fbs_dms.services.document_service import DocumentService
        return DocumentService(company_id=test_company['id'])
    except ImportError:
        pytest.skip("fbs_dms not available")

# Database routing fixtures
@pytest.fixture
def test_database_router():
    """Create test database router for isolation testing."""
    try:
        from fbs_app.routers import FBSDatabaseRouter
        return FBSDatabaseRouter()
    except ImportError:
        pytest.skip("fbs_app not available")

# Cherry-picking test fixtures
@pytest.fixture
def fbs_only_config(db):
    """Configuration for FBS app only (no licensing, no DMS)."""
    return {
        'apps': ['fbs_app'],
        'databases': ['default'],
        'features': ['core', 'msme', 'workflows', 'bi', 'compliance', 'accounting']
    }

@pytest.fixture
def fbs_with_licensing_config(db):
    """Configuration for FBS app + licensing (no DMS)."""
    return {
        'apps': ['fbs_app', 'fbs_license_manager'],
        'databases': ['default', 'licensing'],
        'features': ['core', 'msme', 'workflows', 'bi', 'compliance', 'accounting', 'licensing']
    }

@pytest.fixture
def fbs_with_dms_config(db):
    """Configuration for FBS app + DMS (no licensing)."""
    return {
        'apps': ['fbs_app', 'fbs_dms'],
        'databases': ['default', 'djo_test_solution_db'],
        'features': ['core', 'msme', 'workflows', 'bi', 'compliance', 'accounting', 'dms']
    }

@pytest.fixture
def full_stack_config(db):
    """Configuration for all apps together."""
    return {
        'apps': ['fbs_app', 'fbs_license_manager', 'fbs_dms'],
        'databases': ['default', 'licensing', 'djo_test_solution_db', 'fbs_test_solution_db'],
        'features': ['core', 'msme', 'workflows', 'bi', 'compliance', 'accounting', 'licensing', 'dms']
    }

# Performance testing fixtures
@pytest.fixture
def large_dataset(db):
    """Create large dataset for performance testing."""
    try:
        from fbs_app.models import RequestLog
        from django.contrib.auth.models import User
        
        # Create test users
        users = []
        for i in range(100):
            user = User.objects.create_user(
                username=f'perf_user_{i}',
                email=f'perf_user_{i}@example.com',
                password='testpass123'
            )
            users.append(user)
        
        # Create test logs
        logs = []
        for i in range(1000):
            log = RequestLog.objects.create(
                user=users[i % 100],
                method='GET',
                endpoint=f'/api/test/{i}',
                response_status=200,
                response_time=0.1,
                ip_address='127.0.0.1'
            )
            logs.append(log)
        
        return {'users': users, 'logs': logs}
    except ImportError:
        pytest.skip("fbs_app not available")

# Security testing fixtures
@pytest.fixture
def malicious_input_data():
    """Create malicious input data for security testing."""
    return {
        'sql_injection': "'; DROP TABLE users; --",
        'xss_payload': '<script>alert("XSS")</script>',
        'path_traversal': '../../../etc/passwd',
        'command_injection': '$(rm -rf /)',
        'overflow': 'A' * 10000
    }

# Cleanup fixtures
@pytest.fixture(autouse=True)
def cleanup_test_data(db):
    """Automatically cleanup test data after each test."""
    yield
    # Django will handle cleanup automatically with test database

# Markers for test organization
pytest_plugins = [
    "pytest_django",
]

# Custom markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests between components"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end workflow tests"
    )
    config.addinivalue_line(
        "markers", "cherry_picking: Tests for app cherry-picking scenarios"
    )
    config.addinivalue_line(
        "markers", "isolation: Tests for database isolation architecture"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and load testing"
    )
    config.addinivalue_line(
        "markers", "security: Security and vulnerability testing"
    )
    config.addinivalue_line(
        "markers", "fbs_app: Tests specific to FBS core app"
    )
    config.addinivalue_line(
        "markers", "license_manager: Tests specific to license manager"
    )
    config.addinivalue_line(
        "markers", "dms: Tests specific to document management system"
    )
