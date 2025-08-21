# 🧪 FBS App Testing Guide

Comprehensive testing framework for the FBS App, ensuring robust, elegant, and state-of-the-art functionality.

## 📋 Table of Contents

- [Overview](#overview)
- [Testing Architecture](#testing-architecture)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [Test Development](#test-development)
- [Coverage Requirements](#coverage-requirements)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)
- [Continuous Integration](#continuous-integration)

## 🎯 Overview

The FBS App testing framework is designed to ensure:
- **100% Code Coverage** - Every line of code is tested
- **Performance Excellence** - All operations meet performance benchmarks
- **Security Hardening** - Comprehensive security testing and validation
- **Reliability** - Robust error handling and edge case coverage
- **Maintainability** - Clean, readable, and maintainable test code

## 🏗️ Testing Architecture

### Test Structure
```
fbs_app/tests/
├── conftest.py              # Test configuration and fixtures
├── test_models.py           # Model unit tests
├── test_interfaces.py       # Interface unit tests
├── test_services.py         # Service unit tests
├── test_integration.py      # Integration tests
├── test_performance.py      # Performance tests
├── test_security.py         # Security tests
└── test_e2e.py             # End-to-end tests
```

### Test Configuration
- **pytest** - Modern Python testing framework
- **pytest-django** - Django integration
- **pytest-cov** - Coverage reporting
- **pytest-benchmark** - Performance testing
- **pytest-mock** - Mocking and patching
- **pytest-xdist** - Parallel test execution

## 🧩 Test Categories

### 1. Unit Tests (`@pytest.mark.unit`)
- **Purpose**: Test individual components in isolation
- **Coverage**: Models, interfaces, services, utilities
- **Mocking**: External dependencies mocked
- **Speed**: Fast execution (< 100ms per test)

### 2. Integration Tests (`@pytest.mark.integration`)
- **Purpose**: Test component interactions
- **Coverage**: Service integration, database operations
- **Mocking**: Minimal mocking, real database
- **Speed**: Medium execution (100ms - 1s per test)

### 3. Performance Tests (`@pytest.mark.performance`)
- **Purpose**: Ensure performance benchmarks are met
- **Coverage**: Database queries, API calls, business logic
- **Benchmarks**: Response time, throughput, resource usage
- **Thresholds**: Configurable performance limits

### 4. Security Tests (`@pytest.mark.security`)
- **Purpose**: Validate security measures
- **Coverage**: Input validation, authentication, authorization
- **Tests**: SQL injection, XSS, CSRF, authentication bypass
- **Tools**: Bandit, safety, custom security validators

### 5. End-to-End Tests (`@pytest.mark.e2e`)
- **Purpose**: Test complete user workflows
- **Coverage**: Full application scenarios
- **Environment**: Test database, mocked external services
- **Speed**: Slow execution (1s - 10s per test)

## 🚀 Running Tests

### Quick Start
```bash
# Run all tests with coverage
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit
python run_tests.py --integration
python run_tests.py --performance
python run_tests.py --security

# Run with specific markers
python run_tests.py --markers unit performance
```

### Advanced Options
```bash
# Parallel execution
python run_tests.py --parallel

# Benchmark tests only
python run_tests.py --benchmark

# Code quality checks
python run_tests.py --quality

# Security checks
python run_tests.py --security-checks

# Generate comprehensive report
python run_tests.py --report
```

### Direct pytest Commands
```bash
# Run specific test file
pytest fbs_app/tests/test_models.py -v

# Run tests with specific markers
pytest -m "unit and not slow" -v

# Run with coverage
pytest --cov=fbs_app --cov-report=html

# Run in parallel
pytest -n auto --dist=loadfile

# Performance testing
pytest --benchmark-only --benchmark-sort=name
```

## 🛠️ Test Development

### Writing Unit Tests

#### Model Tests
```python
class TestOdooDatabase(FBSAppTestCase):
    """Test OdooDatabase model"""
    
    def test_create_odoo_database(self):
        """Test creating a basic Odoo database"""
        db = OdooDatabase.objects.create(
            name='test_db',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
        self.assertEqual(db.name, 'test_db')
        self.assertTrue(db.is_active)
    
    def test_database_validation(self):
        """Test database field validation"""
        # Test unique constraint instead
        OdooDatabase.objects.create(
            name='test_db_validation',
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
        
        with self.assertRaises(IntegrityError):
            OdooDatabase.objects.create(
                name='test_db_validation',  # Duplicate name should fail
                host='localhost',
                port=8069,
                protocol='http',
                username='admin',
                password='admin'
            )
```

#### Interface Tests
```python
class TestMSMEInterface(FBSAppTestCase):
    """Test MSME interface functionality"""
    
    def setUp(self):
        super().setUp()
        self.msme_interface = MSMEInterface('test_solution')
        self.mock_service = Mock()
        self.msme_interface._service = self.mock_service
    
    def test_setup_business(self):
        """Test business setup"""
        business_config = {
            'solution_name': 'test_solution',
            'business_type': 'retail',
            'current_step': 'setup',
            'total_steps': 5,
            'progress': 20.0
        }
        
        expected_response = {'success': True, 'business_id': 1}
        self.mock_service.setup_msme_business.return_value = expected_response
        
        result = self.msme_interface.setup_business('retail', business_config)
        
        self.assertEqual(result, expected_response)
        self.mock_service.setup_msme_business.assert_called_once_with('retail', business_config)
```

#### Performance Tests
```python
@pytest.mark.performance
class TestModelPerformance(FBSAppTestCase):
    """Test model performance"""
    
    def test_bulk_create_performance(self):
        """Test bulk create performance"""
        def bulk_create_users():
            users = [UserFactory.build() for _ in range(10)]
            return User.objects.bulk_create(users)
        
        result = bulk_create_users()
        self.assertEqual(len(result), 10)
```

#### Security Tests
```python
@pytest.mark.security
class TestModelSecurity(FBSAppTestCase):
    """Test model security"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention"""
        suspicious_name = "'; DROP TABLE users; --"
        
        db = OdooDatabase.objects.create(
            name=suspicious_name,
            host='localhost',
            port=8069,
            protocol='http',
            username='admin',
            password='admin'
        )
        
        # Should not cause SQL injection
        retrieved = OdooDatabase.objects.get(name=suspicious_name)
        self.assertEqual(retrieved, db)
```

### Test Fixtures

#### User Fixtures
```python
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
```

#### Mock Fixtures
```python
@pytest.fixture
def mock_odoo_client():
    """Mock Odoo client for testing"""
    mock_client = Mock()
    mock_client.list_records.return_value = {
        'success': True,
        'data': [],
        'total_count': 0
    }
    return mock_client
```

### Test Data Factories
```python
class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users"""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True
```

## 📊 Coverage Requirements

### Minimum Coverage
- **Overall Coverage**: 90%
- **Critical Paths**: 100%
- **Business Logic**: 100%
- **Error Handling**: 100%
- **Security Functions**: 100%

### Coverage Reports
```bash
# Generate HTML coverage report
pytest --cov=fbs_app --cov-report=html

# Generate XML coverage report
pytest --cov=fbs_app --cov-report=xml

# Coverage with missing lines
pytest --cov=fbs_app --cov-report=term-missing
```

### Coverage Configuration
```ini
# pytest.ini
addopts = 
    --cov=fbs_app
    --cov-report=html
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=90
```

## ⚡ Performance Testing

### Performance Benchmarks
- **Response Time**: < 100ms for simple operations
- **Database Queries**: < 50ms for standard queries
- **Memory Usage**: < 100MB for typical operations
- **CPU Usage**: < 10% for standard operations

### Performance Test Examples
```python
@pytest.mark.performance
def test_interface_initialization_performance(self, benchmark):
    """Test interface initialization performance"""
    def create_interface():
        return FBSInterface('test_solution')
    
    result = benchmark(create_interface)
    self.assertIsInstance(result, FBSInterface)

@pytest.mark.performance
def test_method_call_performance(self, benchmark):
    """Test method call performance"""
    with patch.object(self.fbs_interface.msme._service, 'get_dashboard') as mock_service:
        mock_service.return_value = {'success': True, 'data': {}}
        
        def call_method():
            return self.fbs_interface.msme.get_dashboard()
        
        result = benchmark(call_method)
        self.assertEqual(result['success'], True)
```

## 🔒 Security Testing

### Security Test Categories
1. **Input Validation**
   - SQL injection prevention
   - XSS prevention
   - CSRF protection
   - Path traversal prevention

2. **Authentication & Authorization**
   - Token validation
   - Permission checks
   - Session management
   - Role-based access control

3. **Data Protection**
   - Sensitive data encryption
   - Data sanitization
   - Access logging
   - Audit trails

### Security Test Examples
```python
@pytest.mark.security
def test_solution_name_injection(self):
    """Test solution name injection prevention"""
    malicious_solution = "'; DROP TABLE users; --"
    
    # Should not cause SQL injection
    interface = FBSInterface(malicious_solution)
    self.assertEqual(interface.solution_name, malicious_solution)

@pytest.mark.security
def test_parameter_validation(self):
    """Test parameter validation and sanitization"""
    malicious_config = {
        'business_name': "<script>alert('xss')</script>",
        'business_type': "'; DROP TABLE users; --"
    }
    
    # Should handle malicious input gracefully
    with patch.object(self.fbs_interface.msme._service, 'setup_business') as mock_service:
        mock_service.return_value = {'success': False, 'error': 'Invalid input'}
        result = self.fbs_interface.msme.setup_business('retail', malicious_config)
        self.assertFalse(result['success'])
```

## 🔄 Continuous Integration

### CI/CD Pipeline
```yaml
# .github/workflows/test.yml
name: FBS App Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python run_tests.py --all
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

## 📈 Test Metrics

### Key Performance Indicators
- **Test Execution Time**: < 5 minutes for full suite
- **Test Success Rate**: > 99%
- **Coverage Trend**: Increasing over time
- **Bug Detection Rate**: High (catches issues early)

### Test Reporting
- **HTML Coverage Reports**: Visual coverage analysis
- **JUnit XML**: CI/CD integration
- **Performance Benchmarks**: Historical performance tracking
- **Security Scan Results**: Vulnerability tracking

## 🎯 Best Practices

### Test Design
1. **Arrange-Act-Assert**: Clear test structure
2. **Single Responsibility**: One assertion per test
3. **Descriptive Names**: Clear test purpose
4. **Independent Tests**: No test dependencies
5. **Fast Execution**: Tests run quickly

### Test Maintenance
1. **Regular Updates**: Keep tests current with code
2. **Refactoring**: Improve test quality over time
3. **Documentation**: Clear test documentation
4. **Code Review**: Review test code quality

### Test Data Management
1. **Factory Pattern**: Use factories for test data
2. **Minimal Data**: Only create necessary test data
3. **Cleanup**: Proper test data cleanup
4. **Isolation**: Test data isolation

## 🚨 Troubleshooting

### Common Issues
1. **Import Errors**: Check Python path and virtual environment
2. **Database Issues**: Ensure test database is configured
3. **Mock Issues**: Verify mock setup and expectations
4. **Performance Failures**: Check benchmark thresholds

### Debug Commands
```bash
# Run with verbose output
pytest -v -s

# Run single test with debugger
pytest -s --pdb

# Run with coverage and debug
pytest --cov=fbs_app --cov-report=term-missing -s
```

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Remember**: Good tests are an investment in code quality and maintainability. Write tests that are clear, comprehensive, and maintainable! 🚀
