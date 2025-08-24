# 🔐 FBS Licensing System

The FBS Licensing System provides flexible, feature-based access control with support for both embedded and external licensing services.

## 🏗️ Architecture Overview

### **Hybrid Approach**
- **Embedded Engine**: Local license validation (default)
- **External Service**: Hosted license service (optional)
- **Intelligent Fallback**: Automatic fallback to embedded if external fails
- **Seamless Migration**: Easy transition between licensing modes

### **Core Components**
1. **EmbeddedLicenseEngine**: Local license management
2. **ExternalLicenseService**: External service integration
3. **HybridLicenseManager**: Combined approach with fallback
4. **FeatureFlags**: Feature availability management
5. **UpgradePrompts**: Upgrade guidance and pricing

## 🚀 Quick Start

### **Basic Usage**

```python
from fbs_app.interfaces import FBSInterface

# Initialize with solution context
fbs = FBSInterface('my_solution', 'license_key')

# Check license info
license_info = fbs.get_license_info()
print(f"License: {license_info['license_type']}")

# Check feature access
if fbs.check_feature_access('bi')['access']:
    # Use BI features
    dashboards = fbs.bi.get_dashboards()
else:
    # Show upgrade prompt
    upgrade_info = fbs.get_upgrade_prompt('bi')
```

### **Odoo Integration**

```python
# License data is automatically stored in Odoo database
# Each solution has isolated license data

# Check if Odoo storage is available
if license_info['odoo_available']:
    print("License stored in Odoo database")
    print(f"Storage type: {license_info['storage_type']}")

# Feature usage is automatically tracked in Odoo
# No manual tracking required
```

### **Feature Checking**

```python
# Check if feature is enabled
if fbs.feature_flags.is_enabled('msme'):
    # MSME features available
    pass

# Check feature access with usage
access = fbs.check_feature_access('msme_businesses', current_usage=5)
if access['access']:
    print(f"Remaining: {access['remaining']}")
else:
    print("Upgrade required")
```

## 📋 License Tiers

### **1. Trial (30 days)**
- **Features**: Core, Basic MSME, Basic Odoo
- **Limits**: 1 business, 100 records, 2 workflows
- **Price**: Free
- **Upgrade**: Available to Basic, Professional, Enterprise

### **2. Basic ($29/month or $290/year)**
- **Features**: Core, MSME, Basic Odoo, Basic Workflows
- **Limits**: 5 businesses, 1000 records, 10 workflows
- **Price**: $29/month or $290/year
- **Upgrade**: Available to Professional, Enterprise

### **3. Professional ($99/month or $990/year)**
- **Features**: Core, MSME, Odoo, Workflows, BI, Compliance
- **Limits**: 25 businesses, 10000 records, 100 workflows
- **Price**: $99/month or $990/year
- **Upgrade**: Available to Enterprise

### **4. Enterprise ($299/month or $2990/year)**
- **Features**: All features + Accounting, Advanced Analytics
- **Limits**: Unlimited
- **Price**: $299/month or $2990/year
- **Upgrade**: Maximum tier

## ⚙️ Configuration

### **Environment Variables**

```bash
# License Type
export FBS_LICENSE_TYPE="professional"

# Feature Overrides
export FBS_ENABLE_BI_FEATURES="true"
export FBS_ENABLE_MSME_FEATURES="true"

# License Service Configuration
export FBS_PREFER_EXTERNAL_LICENSE="false"
export FBS_FALLBACK_TO_EMBEDDED="true"
export FBS_FORCE_EMBEDDED_LICENSE="false"
```

### **Odoo Database Storage**

The licensing system automatically stores license data in the Odoo database for each solution:

```python
# License data is stored in fbs.solution.license model
# Feature usage is tracked in fbs.feature.usage model
# License management operations use fbs.license.manager model

# Each solution has isolated license data
# Data persists across restarts and deployments
# Automatic cache synchronization with Odoo
```

### **Storage Strategy**

1. **Priority 1**: Odoo Database (persistent)
2. **Priority 2**: Django Cache (performance)
3. **Priority 3**: Environment Variables (configuration)
4. **Priority 4**: License Files (fallback)
5. **Priority 5**: Generated Defaults (trial)

### **Django Settings**

```python
# settings.py
FBS_APP = {
    'DEFAULT_LICENSE': 'professional',
    'TRIAL_DAYS': 30,
    'ENABLE_BI_FEATURES': True,
    'ENABLE_MSME_FEATURES': True,
    'PREFER_EXTERNAL_LICENSE': False,
    'FALLBACK_TO_EMBEDDED': True,
    'FORCE_EMBEDDED_LICENSE': False,
}
```

### **License File**

Create `.fbs_license` in your project root:

```json
{
    "type": "professional",
    "features": ["core", "msme", "odoo", "workflows", "bi", "compliance"],
    "limits": {
        "msme_businesses": 25,
        "odoo_records": 10000,
        "workflows": 100,
        "reports": 500,
        "users": 25
    }
}
```

## 🔧 External License Service

### **Configuration**

```python
# settings.py
FBS_LICENSE_API_URL = 'https://license.fayvad.com/api/v1'
FBS_LICENSE_API_KEY = 'your_api_key_here'
FBS_LICENSE_TIMEOUT = 5
FBS_LICENSE_RETRY_ATTEMPTS = 3
FBS_LICENSE_RETRY_DELAY = 1
```

### **API Endpoints**

The external service should provide these endpoints:

- `POST /validate` - Validate license key
- `GET /info` - Get license information
- `POST /feature_access` - Check feature access
- `POST /report_usage` - Report feature usage
- `GET /upgrade_options` - Get upgrade options
- `GET /health` - Service health check

### **Response Format**

```json
{
    "valid": true,
    "license_type": "professional",
    "expiry_date": "2025-12-31T23:59:59",
    "features": ["core", "msme", "odoo", "workflows", "bi"],
    "limits": {
        "msme_businesses": 25,
        "odoo_records": 10000,
        "workflows": 100
    }
}
```

## 🎯 Feature Management

### **Feature Dependencies**

```python
# Features have dependencies
dependencies = {
    'msme': ['core'],
    'bi': ['core', 'msme'],
    'workflows': ['core'],
    'compliance': ['core', 'workflows'],
    'accounting': ['core', 'msme'],
    'advanced_analytics': ['core', 'bi', 'msme']
}
```

### **Feature Matrix**

```python
# Get complete feature availability
matrix = fbs.get_feature_matrix()

for feature, config in matrix.items():
    print(f"{feature}: {'✅' if config['enabled'] else '❌'}")
    if config['dependencies']:
        print(f"  Dependencies: {', '.join(config['dependencies'])}")
```

### **Usage Tracking**

```python
# Check current usage
usage = fbs.feature_flags.get_feature_usage_summary('msme_businesses', {
    'count': 5
})

if usage['unlimited']:
    print("Unlimited usage")
else:
    for limit_type, info in usage['usage'].items():
        print(f"{limit_type}: {info['current']}/{info['limit']} ({info['percentage']}%)")
```

## 🚀 Upgrade Management

### **Upgrade Prompts**

```python
# Get upgrade prompt for a feature
upgrade = fbs.get_upgrade_prompt('bi')

if upgrade['upgrade_available']:
    print(f"Upgrade to {upgrade['next_tier'].upper()}")
    print(f"Price: ${upgrade['pricing']['monthly']}/month")
    print(f"Features: {', '.join(upgrade['next_features'])}")
```

### **Upgrade Analysis**

```python
# Get comprehensive upgrade analysis
analysis = fbs.get_upgrade_analysis()

if analysis['upgrade_available']:
    for option in analysis['upgrade_options']:
        print(f"Tier: {option['tier']}")
        print(f"New Features: {len(option['new_features'])}")
        print(f"Price: ${option['pricing']['monthly']}/month")
```

### **Upgrade Process**

```python
# Get upgrade process information
process = fbs.upgrade_prompts.get_upgrade_process_info()

print(f"Estimated Time: {process['estimated_time']}")
print(f"Data Migration: {'Yes' if process['data_migration'] else 'No'}")
print(f"Training Included: {'Yes' if process['training_included'] else 'No'}")

# Get contact information
contact = fbs.upgrade_prompts.get_upgrade_contact_info()
print(f"Sales: {contact['sales_email']}")
print(f"Support: {contact['support_email']}")
```

## 🔄 Migration Between Modes

### **Embedded to External**

```python
# Initialize hybrid manager
from fbs_app.licensing import HybridLicenseManager

manager = HybridLicenseManager('solution_name', 'license_key')

# Test external service
test_result = manager.test_external_service()
if test_result['status'] == 'tested':
    # Migrate to external
    result = manager.migrate_to_external()
    if result['success']:
        print("Successfully migrated to external licensing")
```

### **External to Embedded**

```python
# Force switch to embedded
manager.switch_to_embedded()

# Or migrate completely
result = manager.migrate_to_embedded()
if result['success']:
    print("Successfully migrated to embedded licensing")
```

## 🧪 Testing

### **Run License Tests**

```bash
# Run all licensing tests
python manage.py test fbs_app.tests.test_licensing

# Run specific test class
python manage.py test fbs_app.tests.test_licensing.EmbeddedLicenseEngineTest

# Run with coverage
coverage run --source='fbs_app.licensing' manage.py test fbs_app.tests.test_licensing
coverage report
```

### **Management Commands**

```bash
# Display license information
python manage.py license_info --solution my_solution --detailed

# JSON output
python manage.py license_info --solution my_solution --format json

# With license key
python manage.py license_info --solution my_solution --license-key FBS-XXXX-XXXX-XXXX-XXXX
```

## 📊 Monitoring and Analytics

### **License Health**

```python
# Check license service health
health = fbs.license_manager.get_service_health()

print(f"Current Source: {health['current_source']}")
print(f"Embedded Status: {health['embedded']['status']}")
print(f"External Status: {health['external']['status']}")
```

### **Feature Usage Analytics**

```python
# Track feature usage
usage_data = {
    'count': 1,
    'storage': 1024,  # bytes
    'users': 1,
    'time': 300  # seconds
}

# Report usage (if using external service)
result = fbs.license_manager.report_usage('msme_businesses', usage_data)
if result['success']:
    print(f"Usage reported: {result['usage_id']}")
```

## 🔒 Security Considerations

### **License Key Security**
- Store license keys securely (environment variables, secure files)
- Never commit license keys to version control
- Use HTTPS for external license service communication
- Implement rate limiting for license validation

### **Feature Access Control**
- Always check feature access before enabling functionality
- Implement usage tracking and limits
- Log license validation attempts
- Monitor for license bypass attempts

### **Data Privacy**
- Minimize data sent to external license services
- Implement data retention policies
- Ensure compliance with data protection regulations
- Provide data export/deletion capabilities

## 🚨 Troubleshooting

### **Common Issues**

1. **License Not Loading**
   - Check environment variables
   - Verify license file format
   - Check file permissions

2. **Features Not Available**
   - Verify license type supports feature
   - Check feature dependencies
   - Review environment overrides

3. **External Service Failures**
   - Check network connectivity
   - Verify API credentials
   - Check service health
   - Review fallback configuration

### **Debug Mode**

```python
# Enable debug logging
import logging
logging.getLogger('fbs_app.licensing').setLevel(logging.DEBUG)

# Check license source
print(f"License Source: {fbs.license_manager.get_license_source()}")

# Check service configuration
print(f"Service Info: {fbs.license_manager.get_service_info()}")
```

## 📚 API Reference

### **LicenseManager Methods**

- `get_license_info()` - Get comprehensive license information
- `has_feature(feature_name)` - Check if feature is available
- `get_feature_limit(feature_name, limit_type)` - Get feature limits
- `check_feature_usage(feature_name, current_usage)` - Check usage limits
- `validate_license()` - Validate current license
- `get_upgrade_options()` - Get available upgrades

### **FeatureFlags Methods**

- `is_enabled(feature_name)` - Check if feature is enabled
- `get_enabled_features()` - Get all enabled features
- `get_feature_config(feature_name)` - Get feature configuration
- `check_feature_access(feature_name, **kwargs)` - Check feature access
- `get_feature_matrix()` - Get complete feature matrix

### **UpgradePrompts Methods**

- `get_upgrade_prompt(feature_name)` - Get upgrade prompt
- `get_feature_upgrade_prompt(feature_name)` - Get feature-specific upgrade
- `get_comprehensive_upgrade_analysis()` - Get complete upgrade analysis
- `get_upgrade_contact_info()` - Get contact information
- `get_upgrade_process_info()` - Get process information

## 🔮 Future Enhancements

### **Planned Features**
- **Usage Analytics Dashboard**: Visual usage tracking
- **Automated Upgrades**: Self-service license upgrades
- **License Pooling**: Shared licenses across solutions
- **Advanced Compliance**: Regulatory compliance tracking
- **Machine Learning**: Predictive upgrade recommendations

### **Integration Opportunities**
- **Payment Gateways**: Stripe, PayPal integration
- **CRM Systems**: Salesforce, HubSpot integration
- **Analytics Platforms**: Google Analytics, Mixpanel
- **Support Systems**: Zendesk, Intercom integration

## 📞 Support

For licensing support and questions:

- **Email**: support@fayvad.com
- **Documentation**: https://fayvad.com/docs/licensing
- **Community**: https://community.fayvad.com
- **Sales**: sales@fayvad.com

---

**FBS Licensing System** - Empowering your business with flexible, feature-rich access control.
