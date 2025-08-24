# FBS License Manager Integration Guide

## Overview

The **FBS License Manager** (`fbs_license_manager`) provides license management, feature control, and upgrade prompts for commercial FBS deployments.

## Installation

```python
# settings.py
INSTALLED_APPS = [
    'fbs_license_manager',
]

FBS_LICENSE_MANAGER = {
    'ENABLE_LICENSING': True,
    'LICENSE_TYPE': 'professional',
    'FEATURE_LIMITS': {
        'msme_businesses': 10,
        'workflows': 50,
        'reports': 1000,
        'users': 25
    }
}
```

## Core Usage

### Initialize License Manager

```python
from fbs_license_manager.services import LicenseManager, FeatureFlags

# Initialize with solution and license key
license_manager = LicenseManager('your_solution_name', 'your_license_key')

# Initialize feature flags
feature_flags = FeatureFlags('your_solution_name', license_manager)
```

### Check Feature Availability

```python
# Check if feature is available
if license_manager.has_feature('msme'):
    print("MSME features are available")

# Get feature limit
msme_limit = license_manager.get_feature_limit('msme_businesses')
print(f"MSME businesses limit: {msme_limit}")

# Check feature usage
usage_info = license_manager.check_feature_usage('msme_businesses', current_usage=5)
if usage_info['available']:
    print(f"Can create {usage_info['remaining']} more MSME businesses")
else:
    print("MSME business limit reached")
```

### Get License Information

```python
# Get comprehensive license info
license_info = license_manager.get_license_info()
print(f"License type: {license_info['type']}")
print(f"Status: {license_info['status']}")
print(f"Features: {license_info['features']}")
print(f"Limits: {license_info['limits']}")

# Get license status
status = license_manager.get_license_status()
print(f"Current status: {status}")

# Check if license is expired
if license_manager.is_expired():
    print("License has expired")
```

## Feature Management

### Feature Flags

```python
# Check if feature is enabled
if feature_flags.is_enabled('msme'):
    print("MSME features are enabled")

# Get feature matrix
feature_matrix = feature_flags.get_feature_matrix()
for feature, info in feature_matrix.items():
    print(f"{feature}: {'Enabled' if info['enabled'] else 'Disabled'}")

# Check feature access
access_info = feature_flags.check_feature_access('msme_businesses', current_usage=5)
if access_info['access']:
    print(f"Access granted. Remaining: {access_info['remaining']}")
else:
    print("Access denied. Limit reached.")
```

### Feature Usage Tracking

```python
from fbs_license_manager.models import FeatureUsage

# Track feature usage
FeatureUsage.objects.create(
    solution_name='your_solution_name',
    feature_name='msme_businesses',
    usage_count=1
)

# Increment usage
FeatureUsage.increment_usage('your_solution_name', 'msme_businesses')

# Get usage statistics
usage_stats = license_manager.get_feature_usage_stats('msme_businesses')
print(f"Total usage: {usage_stats['total_usage']}")
print(f"Current period: {usage_stats['current_period_usage']}")
```

## License Types and Limits

### Available License Types

- **Trial**: Limited features, time-limited
- **Basic**: Core features, moderate limits
- **Professional**: Advanced features, higher limits
- **Enterprise**: All features, unlimited

### Feature Limits Structure

```python
# Example limits configuration
limits = {
    'msme_businesses': 10,
    'workflows': 50,
    'reports': 1000,
    'users': 25,
    'storage_gb': 100,
    'api_calls_per_month': 10000
}

# Nested limits (for complex features)
complex_limits = {
    'msme': {
        'businesses': 10,
        'users_per_business': 5,
        'storage_per_business': '10GB'
    },
    'workflows': {
        'total': 50,
        'active': 25,
        'templates': 20
    }
}
```

## Upgrade Management

### Upgrade Prompts

```python
from fbs_license_manager.services import UpgradePrompts

# Initialize upgrade prompts
upgrade_prompts = UpgradePrompts(license_manager)

# Get upgrade prompt for specific feature
prompt = upgrade_prompts.get_upgrade_prompt('msme_businesses')
if prompt['upgrade_required']:
    print(f"Upgrade needed: {prompt['message']}")
    print(f"Recommended plan: {prompt['recommended_plan']}")

# Get comprehensive upgrade analysis
analysis = upgrade_prompts.get_comprehensive_upgrade_analysis()
print(f"Current plan: {analysis['current_plan']}")
print(f"Recommended upgrades: {analysis['recommended_upgrades']}")
```

### Upgrade Options

```python
# Get available upgrade options
upgrade_options = license_manager.get_upgrade_options()
for option in upgrade_options:
    print(f"Upgrade to {option['type']}: {option['price']}")
    print(f"Features: {option['features']}")
```

## Integration with FBS App

### FBS Interface Integration

```python
from fbs_app.interfaces import FBSInterface

# Initialize FBS with licensing
fbs = FBSInterface('your_solution_name', license_key='your_license_key')

# Check feature access through FBS
access_info = fbs.check_feature_access('msme_businesses')
if access_info['access']:
    # Use MSME features
    setup_result = fbs.msme.setup_business('retail', config_data)
else:
    # Handle limit reached
    upgrade_prompt = fbs.get_upgrade_prompt('msme_businesses')
    print(f"Upgrade needed: {upgrade_prompt['message']}")
```

### Feature Availability Check

```python
# Check if licensing is available
if fbs._licensing_available:
    # Check specific features
    if fbs.feature_flags.is_enabled('msme'):
        print("MSME features available")
    
    if fbs.feature_flags.is_enabled('bi'):
        print("Business Intelligence features available")
    
    if fbs.feature_flags.is_enabled('workflows'):
        print("Workflow features available")
else:
    print("No licensing system - all features available")
```

## Environment-Based Configuration

### Environment Variables

```bash
# License configuration
FBS_LICENSE_TYPE=professional
FBS_ENABLE_MSME_FEATURES=true
FBS_ENABLE_BI_FEATURES=true
FBS_ENABLE_WORKFLOW_FEATURES=true
FBS_ENABLE_COMPLIANCE_FEATURES=true

# Feature limits
FBS_MSME_BUSINESSES_LIMIT=10
FBS_WORKFLOWS_LIMIT=50
FBS_REPORTS_LIMIT=1000
FBS_USERS_LIMIT=25
```

### Settings Configuration

```python
# settings.py
FBS_LICENSE_MANAGER = {
    'ENABLE_LICENSING': os.environ.get('FBS_ENABLE_LICENSING', 'True').lower() == 'true',
    'LICENSE_TYPE': os.environ.get('FBS_LICENSE_TYPE', 'trial'),
    'FEATURE_LIMITS': {
        'msme_businesses': int(os.environ.get('FBS_MSME_BUSINESSES_LIMIT', 5)),
        'workflows': int(os.environ.get('FBS_WORKFLOWS_LIMIT', 10)),
        'reports': int(os.environ.get('FBS_REPORTS_LIMIT', 100)),
        'users': int(os.environ.get('FBS_USERS_LIMIT', 5))
    }
}
```

## Database Configuration

### Multi-Database Setup

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fbs_system_db',
        'USER': 'odoo',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    },
    'licensing': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lic_system_db',
        'USER': 'odoo',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Database routers
DATABASE_ROUTERS = [
    'fbs_app.routers.FBSDatabaseRouter',
]
```

## Security Features

### License Encryption

```python
# License keys are automatically encrypted
license_manager = LicenseManager('solution_name', 'your_license_key')

# The key is encrypted before storage
# Access is controlled through the LicenseManager interface
```

### Access Control

```python
# Feature access is checked at runtime
if not license_manager.has_feature('msme'):
    raise PermissionDenied("MSME features not available in current license")

# Usage limits are enforced
if license_manager.check_feature_usage('msme_businesses', current_usage)['available']:
    # Proceed with operation
    pass
else:
    raise PermissionDenied("Feature usage limit reached")
```

## Monitoring and Analytics

### License Usage Tracking

```python
# Track feature usage
FeatureUsage.objects.create(
    solution_name='solution_name',
    feature_name='msme_businesses',
    usage_count=1
)

# Get usage analytics
analytics = license_manager.get_usage_analytics()
print(f"Total features used: {analytics['total_features']}")
print(f"Most used feature: {analytics['most_used_feature']}")
print(f"Usage trends: {analytics['usage_trends']}")
```

### Performance Monitoring

```python
# Get license manager performance metrics
metrics = license_manager.get_performance_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']}")
print(f"Database queries: {metrics['db_queries']}")
print(f"Response time: {metrics['response_time']}")
```

## Error Handling

### License Errors

```python
try:
    license_manager = LicenseManager('solution_name', 'invalid_key')
    license_info = license_manager.get_license_info()
except Exception as e:
    print(f"License error: {e}")
    # Fallback to trial mode or handle error appropriately
```

### Feature Access Errors

```python
try:
    if not license_manager.has_feature('msme'):
        raise PermissionDenied("MSME features not available")
    
    # Use MSME features
    result = use_msme_feature()
except PermissionDenied as e:
    print(f"Access denied: {e}")
    # Show upgrade prompt or handle gracefully
```

## Testing

### Running Tests

```bash
# Run license manager tests
python -m pytest fbs_license_manager/tests/

# Run specific test categories
python -m pytest fbs_license_manager/tests/test_models.py
python -m pytest fbs_license_manager/tests/test_services.py
```

### Test Configuration

```python
# test_settings.py
FBS_LICENSE_MANAGER = {
    'ENABLE_LICENSING': True,
    'LICENSE_TYPE': 'trial',
    'FEATURE_LIMITS': {
        'msme_businesses': 5,
        'workflows': 10,
        'reports': 100
    }
}
```

## Troubleshooting

### Common Issues

1. **License not found**
   ```
   License not found for solution: solution_name
   ```
   **Solution**: Check solution name and license key

2. **Feature not available**
   ```
   Feature 'msme' not available in current license
   ```
   **Solution**: Check license type and feature availability

3. **Usage limit reached**
   ```
   Feature usage limit reached for msme_businesses
   ```
   **Solution**: Upgrade license or wait for limit reset

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger('fbs_license_manager').setLevel(logging.DEBUG)

# Check license manager state
print(f"License available: {license_manager._license_data}")
print(f"Features: {license_manager._features}")
```

## Best Practices

### License Management

- Use environment variables for license configuration
- Implement proper error handling for license failures
- Cache license information to reduce database queries
- Monitor feature usage to optimize license plans

### Feature Control

- Check feature availability before operations
- Implement graceful degradation when features are unavailable
- Use feature flags for conditional functionality
- Track usage for billing and optimization

### Security

- Never expose license keys in client-side code
- Encrypt sensitive license information
- Implement proper access controls
- Audit license usage regularly
