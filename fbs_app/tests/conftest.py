"""
Comprehensive Test Configuration for FBS App

This module provides:
- Test fixtures for all components
- Mock configurations
- Test data factories
- Database setup utilities
- Performance testing utilities
"""

import pytest
import factory
from django.test import TestCase
from django.contrib.auth.models import User
from django.db import connections
from django.test.utils import override_settings
from unittest.mock import Mock, patch, MagicMock
import logging

# Configure logging for tests - use WARNING level for faster tests
logging.basicConfig(level=logging.WARNING)

# Test markers
pytestmark = [
    pytest.mark.django_db,
    pytest.mark.fast,
]

# Global test configuration
@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """Setup test database with proper configuration"""
    with django_db_blocker.unblock():
        # Create test database
        pass

@pytest.fixture(scope="function")
def db_access_without_rollback_and_enable_signal_firing(django_db_setup, django_db_blocker):
    """Enable database access and signal firing for tests"""
    django_db_blocker.unblock()
    yield
    django_db_blocker.restore()

# User fixtures
@pytest.fixture
def test_user():
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def admin_user():
    """Create an admin user"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )

# Database fixtures
@pytest.fixture
def clean_db():
    """Ensure clean database state"""
    for connection in connections.all():
        connection.close()
    yield

# Mock fixtures
@pytest.fixture
def mock_odoo_client():
    """Mock Odoo client for testing"""
    mock_client = Mock()
    mock_client.list_records.return_value = {
        'success': True,
        'data': [],
        'total_count': 0
    }
    mock_client.create_record.return_value = {
        'success': True,
        'data': {'id': 1}
    }
    mock_client.update_record.return_value = {
        'success': True,
        'data': {'id': 1}
    }
    mock_client.delete_record.return_value = {
        'success': True
    }
    return mock_client

@pytest.fixture
def mock_redis():
    """Mock Redis for testing"""
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    return mock_redis

# Test data factories
class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users"""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True

@pytest.fixture
def user_factory():
    """Provide user factory"""
    return UserFactory

# Performance testing fixtures
@pytest.fixture
def benchmark(request):
    """Benchmark fixture for performance testing"""
    return request.getfixturevalue('benchmark')

# Security testing fixtures
@pytest.fixture
def security_headers():
    """Security headers for testing"""
    return {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
    }

# Time mocking fixtures
@pytest.fixture
def frozen_time():
    """Freeze time for testing"""
    from freezegun import freeze_time
    with freeze_time("2024-01-01 12:00:00"):
        yield

# HTTP mocking fixtures
@pytest.fixture
def mock_http():
    """Mock HTTP responses"""
    import responses
    with responses.RequestsMock() as rsps:
        yield rsps

# Test utilities
class FBSAppTestCase(TestCase):
    """Base test case for FBS App tests"""
    
    def setUp(self):
        """Setup test case"""
        super().setUp()
        self.maxDiff = None  # Show full diffs in tests
        
        # Set a reasonable timeout for tests to prevent hanging
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Test timed out")
        
        # Set 30 second timeout for each test
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(30)
    
    def tearDown(self):
        """Cleanup test case"""
        import signal
        signal.alarm(0)  # Cancel the alarm
        super().tearDown()
    
    def assertSuccessResponse(self, response, expected_data=None):
        """Assert successful response"""
        self.assertEqual(response.status_code, 200)
        if expected_data:
            self.assertEqual(response.data, expected_data)
    
    def assertErrorResponse(self, response, status_code=400):
        """Assert error response"""
        self.assertEqual(response.status_code, status_code)
        self.assertIn('error', response.data)
    
    def create_solution_context(self, solution_name='test_solution'):
        """Create solution context for testing"""
        from fbs_app.models import OdooDatabase
        return OdooDatabase.objects.create(
            name=f'fbs_{solution_name}_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )

# Performance testing utilities
@pytest.fixture
def performance_test():
    """Performance test fixture"""
    def _performance_test(func, *args, **kwargs):
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        assert execution_time < 1.0, f"Performance test failed: {execution_time:.3f}s"
        return result
    return _performance_test

# Security testing utilities
@pytest.fixture
def security_test():
    """Security test fixture"""
    def _security_test(func, *args, **kwargs):
        # Add security checks here
        result = func(*args, **kwargs)
        return result
    return _security_test
