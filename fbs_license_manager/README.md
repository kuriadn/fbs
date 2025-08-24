# 🔐 FBS License Manager

A standalone, embeddable licensing solution for Django applications that provides enterprise-grade feature management, usage tracking, and upgrade prompts.

## ✨ Features

- **🔑 License Management**: Support for trial, basic, professional, and enterprise tiers
- **🔐 Security**: Cryptography-based license key encryption
- **🚦 Feature Flags**: Runtime feature availability management
- **📊 Usage Tracking**: Monitor feature usage and enforce limits
- **🔄 Upgrade Prompts**: Intelligent upgrade recommendations
- **💾 Persistent Storage**: Database-backed license storage with caching
- **🔌 FBS Integration**: Seamless integration with FBS app for Odoo capabilities
- **📱 Multi-Tenant**: Isolated licensing per solution/client

## 🚀 Quick Start

### Installation

```bash
# Install the package
pip install fbs-license-manager

# Or install from source
git clone https://github.com/fbs/fbs-license-manager.git
cd fbs-license-manager
pip install -e .
```

### Django Setup

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'fbs_license_manager',
]

# Optional: Configure license settings
FBS_LICENSE_TYPE = 'professional'  # trial, basic, professional, enterprise
FBS_TRIAL_DAYS = 30
FBS_ENABLE_MSME_FEATURES = True
FBS_ENABLE_BI_FEATURES = True
```

### Basic Usage

```python
from fbs_license_manager import LicenseManager, FeatureFlags

# Initialize license manager
license_manager = LicenseManager('my_solution', 'license_key_123')

# Check license info
license_info = license_manager.get_license_info()
print(f"License: {license_info['license_type']}")

# Check feature access
feature_flags = FeatureFlags('my_solution', license_manager)
if feature_flags.is_enabled('msme'):
    print("MSME features available")
    
# Check usage limits
access = feature_flags.check_feature_access('msme', current_usage=5)
if access['access']:
    print(f"Remaining: {access['remaining']}")
else:
    print("Upgrade required")
```

## 🏗️ Architecture

### Core Components

1. **LicenseManager**: Main interface for license operations
2. **FeatureFlags**: Feature availability and usage management
3. **UpgradePrompts**: Upgrade recommendations and pricing
4. **SolutionLicense**: Database model for license storage
5. **FeatureUsage**: Database model for usage tracking

### Storage Strategy

1. **Database**: Persistent license storage
2. **Cache**: Performance optimization
3. **Environment**: Configuration overrides
4. **Generated**: Default trial licenses

## 📋 License Tiers

### Trial (30 days)
- Core features
- Basic MSME functionality
- Basic Odoo integration
- **Limits**: 1 business, 100 records, 2 workflows

### Basic ($29/month)
- All trial features
- Full MSME functionality
- Basic workflows
- **Limits**: 5 businesses, 1000 records, 10 workflows

### Professional ($99/month)
- All basic features
- Business Intelligence
- Compliance management
- **Limits**: 25 businesses, 10000 records, 100 workflows

### Enterprise ($299/month)
- All professional features
- Advanced analytics
- Accounting features
- **Limits**: Unlimited

## 🔧 Configuration

### Environment Variables

```bash
# License Type
export FBS_LICENSE_TYPE="professional"

# Feature Overrides
export FBS_ENABLE_MSME_FEATURES="true"
export FBS_ENABLE_BI_FEATURES="true"
export FBS_ENABLE_WORKFLOW_FEATURES="true"
export FBS_ENABLE_COMPLIANCE_FEATURES="true"

# Limits
export FBS_MSME_BUSINESSES_LIMIT="25"
export FBS_WORKFLOWS_LIMIT="100"
export FBS_REPORTS_LIMIT="10000"
export FBS_USERS_LIMIT="25"

# Trial Configuration
export FBS_TRIAL_DAYS="30"
```

### Django Settings

```python
# settings.py
FBS_LICENSE_MANAGER = {
    'default_license_type': 'trial',
    'trial_days': 30,
    'enable_features': {
        'msme': True,
        'bi': True,
        'workflows': True,
        'compliance': True,
    },
    'limits': {
        'msme_businesses': 25,
        'workflows': 100,
        'reports': 10000,
        'users': 25,
    }
}
```

## 📊 Usage Tracking

### Automatic Tracking

```python
# Usage is automatically tracked when checking access
access = feature_flags.check_feature_access('msme', current_usage=5)

# Or manually increment usage
from fbs_license_manager.models import FeatureUsage
FeatureUsage.increment_usage('my_solution', 'msme', count=1)
```

### Usage Reports

```python
# Get usage summary
usage_summary = feature_flags.get_feature_usage_summary()
print(f"MSME usage: {usage_summary.get('msme', 0)}")

# Get upgrade recommendations
recommendations = feature_flags.get_upgrade_recommendations()
for rec in recommendations:
    print(f"{rec['feature']}: {rec['percentage']:.1f}% used")
```

## 🔄 Upgrade Management

### Upgrade Prompts

```python
from fbs_license_manager import UpgradePrompts

upgrade_prompts = UpgradePrompts(license_manager)

# Get upgrade prompt for a feature
prompt = upgrade_prompts.get_upgrade_prompt('bi')
if prompt['upgrade_required']:
    print(f"Upgrade to {prompt['recommended_tier']} for {prompt['price']}")

# Get comprehensive analysis
analysis = upgrade_prompts.get_comprehensive_upgrade_analysis()
print(f"Current tier: {analysis['current_tier']}")
print(f"Upgrade available: {analysis['upgrade_available']}")
```

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=fbs_license_manager
```

### Test Configuration

```python
# test_settings.py
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'fbs_license_manager',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

## 📚 API Reference

### LicenseManager

```python
class LicenseManager:
    def __init__(self, solution_name: str, license_key: str = None)
    def get_license_info() -> Dict[str, Any]
    def has_feature(feature_name: str) -> bool
    def get_feature_limit(feature_name: str) -> int
    def check_feature_usage(feature_name: str, current_usage: int) -> Dict[str, Any]
    def get_upgrade_options() -> List[Dict[str, Any]]
    def refresh_license()
```

### FeatureFlags

```python
class FeatureFlags:
    def __init__(self, solution_name: str, license_manager)
    def is_enabled(feature_name: str) -> bool
    def check_feature_access(feature_name: str, **kwargs) -> Dict[str, Any]
    def get_feature_limits() -> Dict[str, int]
    def get_feature_usage_summary() -> Dict[str, int]
    def get_upgrade_recommendations() -> List[Dict[str, Any]]
    def get_feature_matrix() -> Dict[str, Dict[str, Any]]
```

### UpgradePrompts

```python
class UpgradePrompts:
    def __init__(self, license_manager)
    def get_upgrade_prompt(feature_name: str) -> Dict[str, Any]
    def get_comprehensive_upgrade_analysis() -> Dict[str, Any]
    def get_upgrade_contact_info() -> Dict[str, str]
    def get_upgrade_process_info() -> Dict[str, Any]
```

## 🔌 Integration Examples

### With FBS Core

```python
from fbs_app.interfaces import FBSInterface

# FBS will automatically use license manager if available
fbs = FBSInterface('my_solution', 'license_key_123')

# Check licensing status
license_info = fbs.get_license_info()
print(f"Storage type: {license_info['storage_type']}")
print(f"Odoo available: {license_info['odoo_available']}")

# Feature access with licensing
access = fbs.check_feature_access('msme')
if access['access']:
    # Use MSME features
    businesses = fbs.msme.get_businesses()
else:
    # Show upgrade prompt
    upgrade = fbs.get_upgrade_prompt('msme')
```

### Standalone Usage

```python
from fbs_license_manager import LicenseManager, FeatureFlags

# Use without FBS core
license_manager = LicenseManager('standalone_app')
feature_flags = FeatureFlags('standalone_app', license_manager)

# Check features
if feature_flags.is_enabled('premium_feature'):
    # Use premium feature
    pass
```

## 🔐 Security Features

### License Key Encryption

The license manager automatically encrypts all license keys using cryptography:

```python
# settings.py (optional)
FBS_LICENSE_ENCRYPTION_KEY = 'your-custom-encryption-key'  # Auto-generated if not provided

# License keys are automatically encrypted/decrypted
license = SolutionLicense.objects.get(solution_name='my_solution')
encrypted_key = license.license_key  # Stored encrypted
decrypted_key = license.get_decrypted_license_key()  # Retrieved decrypted
```

### Security Benefits

- **🔒 Automatic Encryption**: License keys encrypted at rest
- **🔑 Key Derivation**: Uses PBKDF2 with Django secret key
- **🛡️ Fallback Protection**: Graceful degradation if encryption fails
- **📊 Audit Trail**: All license operations logged

## 🚀 Deployment

### Production Settings

```python
# settings.py
FBS_LICENSE_MANAGER = {
    'default_license_type': 'enterprise',
    'cache_ttl': 3600,  # 1 hour
    'database_backup': True,
    'monitoring': True,
}

# Odoo Integration (optional)
FBS_ODOO_CONFIG = {
    'enabled': True,
    'url': 'https://your-odoo-instance.com',
    'database': 'your_database',
    'username': 'your_username',
    'api_key': 'your_api_key'
}
```

### Docker

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN pip install -e .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://fbs.com/docs/license-manager](https://fbs.com/docs/license-manager)
- **Issues**: [GitHub Issues](https://github.com/fbs/fbs-license-manager/issues)
- **Email**: support@fbs.com
- **Discord**: [FBS Community](https://discord.gg/fbs)

## 🔮 Roadmap

- [ ] External license service integration
- [ ] Advanced analytics and reporting
- [ ] Multi-currency pricing
- [ ] Subscription management
- [ ] API rate limiting
- [ ] Advanced feature dependencies
- [ ] License migration tools
- [ ] Performance optimization

