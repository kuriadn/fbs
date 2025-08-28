# FBS Suite v2.0.2 - Solution Integration Guide

## 🚀 Overview

FBS Suite v2.0.2 is a complete, production-ready business management platform that provides:
- **Odoo ERP Integration** with automatic database management
- **Document Management System (DMS)** for file handling
- **License Management** for subscription and access control
- **Virtual Fields System** for extending Odoo models
- **Multi-tenant Architecture** with solution isolation

## 📦 Installation

### Quick Install
```bash
# Install from current directory (recommended for development)
pip install -e .

# Install from Git repository
pip install git+https://github.com/fayvad/fbs.git@v2.0.2

# Install from PyPI (when available)
pip install fbs-suite==2.0.2
```

### Automated Installation
Use our installation script for complete setup and verification:
```bash
python3 install_v2.0.2.py
```

## 🔧 Basic Usage

### 1. Initialize FBS for Your Solution

```python
from fbs_app.interfaces import FBSInterface

# Initialize with your solution name
fbs = FBSInterface('your_solution_name')

# This automatically sets up:
# - Django DB: djo_your_solution_name_db
# - Odoo DB: fbs_your_solution_name_db
```

### 2. Create Solution Databases

```python
# Create databases with required Odoo modules
result = fbs.odoo.create_solution_databases_with_modules(
    core_modules=['base', 'web', 'mail', 'contacts'],
    additional_modules=['sale', 'stock', 'account', 'project']
)

if result['success']:
    print(f"✅ Databases ready: {result['django_db_name']}, {result['odoo_db_name']}")
    print(f"📦 Modules installed: {', '.join(result['all_modules_installed'])}")
else:
    print(f"❌ Database creation failed: {result.get('error')}")
```

### 3. Odoo Integration

#### Basic CRUD Operations
```python
# Get records
users = fbs.odoo.get_records('res.users')
partners = fbs.odoo.get_records('res.partner', limit=10)

# Get single record
user = fbs.odoo.get_record('res.users', 1)

# Create record
new_partner = fbs.odoo.create_record('res.partner', {
    'name': 'Acme Corporation',
    'email': 'contact@acme.com',
    'phone': '+1234567890'
})

# Update record
fbs.odoo.update_record('res.partner', new_partner['id'], {
    'phone': '+1987654321'
})

# Delete record
fbs.odoo.delete_record('res.partner', new_partner['id'])
```

#### Advanced Operations
```python
# Execute custom methods
result = fbs.odoo.execute_method(
    'res.partner', 
    'search_read', 
    [], 
    domain=[('email', '!=', False)],
    fields=['name', 'email']
)

# Discover available models and fields
models = fbs.odoo.discover_models()
fields = fbs.odoo.discover_fields('res.partner')
modules = fbs.odoo.discover_modules()
```

### 4. Virtual Fields System

Extend Odoo models with custom data:

```python
# Set custom field
fbs.virtual.set_custom_field(
    'res.partner', 
    partner_id, 
    'customer_tier', 
    'premium', 
    'char'
)

# Get custom field
tier = fbs.virtual.get_custom_field('res.partner', partner_id, 'customer_tier')

# Get all custom fields for a record
custom_fields = fbs.virtual.get_custom_fields('res.partner', partner_id)

# Merge Odoo data with custom fields
full_record = fbs.virtual.merge_odoo_with_custom(
    'res.partner', 
    partner_id, 
    ['name', 'email', 'phone']
)
```

### 5. Document Management

```python
# Upload documents
doc_result = fbs.dms.upload_document(
    file_path='invoice.pdf',
    category='invoices',
    metadata={
        'partner_id': partner_id,
        'amount': 1500.00,
        'due_date': '2024-12-31'
    }
)

# Search documents
invoices = fbs.dms.search_documents(
    category='invoices',
    filters={'partner_id': partner_id}
)

# Download document
fbs.dms.download_document(doc_id, 'downloads/')
```

### 6. License Management

```python
# Create license
license_result = fbs.license.create_license(
    plan_name='premium_plan',
    user_email='user@example.com',
    features=['advanced_analytics', 'api_access'],
    expiry_date='2025-12-31'
)

# Check license validity
is_valid = fbs.license.validate_license(license_id)

# Get license details
license_info = fbs.license.get_license(license_id)
```

## 🏗️ Architecture Features

### Solution Isolation
- Each solution gets isolated databases
- Automatic database naming: `fbs_{solution_name}_db` and `djo_{solution_name}_db`
- No cross-solution data leakage

### Odoo Integration
- **Database Creation**: Automatic Odoo database initialization with `odoo-bin`
- **Module Management**: Install/uninstall Odoo modules as needed
- **Authentication**: Admin user with configurable password
- **API Compatibility**: Full Odoo v17 CE XML-RPC support

### Error Handling
- Comprehensive error messages
- Graceful handling of existing databases
- Clear success/failure indicators

## 🔐 Configuration

### Environment Variables
```bash
# Database connections
FBS_DB_HOST=localhost
FBS_DB_PORT=5432
FBS_DB_USER=odoo
FBS_DB_PASSWORD=four@One2
FBS_DJANGO_USER=fayvad
FBS_DJANGO_PASSWORD=MeMiMo@0207

# Odoo authentication
ODOO_USER=admin
ODOO_PASSWORD=MeMiMo@0207
```

### Database Users
- **`odoo` user**: Creates and manages Odoo databases
- **`fayvad` user**: Creates and manages Django databases  
- **`admin` user**: Logs into Odoo applications

## 🧪 Testing

### Run Complete Workflow Test
```bash
python3 test_complete_workflow.py
```

### Test Specific Components
```bash
# Test Odoo database creation
python3 test_odoo_database_creation.py

# Test module management
python3 test_module_management.py

# Test admin password
python3 test_admin_password.py
```

## 📚 Best Practices

### 1. Solution Naming
- Use descriptive, lowercase names: `rental_system`, `inventory_tracker`
- Avoid special characters and spaces
- Keep names under 20 characters

### 2. Module Selection
- **Core modules**: Always include `base`, `web`, `mail`
- **Business modules**: Add based on requirements (`sale`, `stock`, `account`)
- **Custom modules**: Install after core setup

### 3. Error Handling
```python
try:
    result = fbs.odoo.create_solution_databases_with_modules(
        core_modules=['base', 'web'],
        additional_modules=['sale']
    )
    
    if result['success']:
        print("✅ Setup complete")
    else:
        print(f"⚠️  Setup issues: {result.get('message')}")
        
except Exception as e:
    print(f"❌ Setup failed: {str(e)}")
```

### 4. Database Management
- Check if databases exist before creation
- Handle "already exists" scenarios gracefully
- Monitor database sizes and performance

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Already Exists
```
Error: database "fbs_solution_db" already exists
```
**Solution**: This is normal! The database is ready to use.

#### 2. Odoo Authentication Failed
```
Error: Odoo XML-RPC fault: 1 - Access Denied
```
**Solution**: Check `ODOO_USER` and `ODOO_PASSWORD` environment variables.

#### 3. Module Installation Failed
```
Error: Module 'sale' not found
```
**Solution**: Verify module names and check Odoo module availability.

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Version History

- **v2.0.0**: Initial Odoo integration and solution-aware architecture
- **v2.0.1**: Packaging and installation improvements
- **v2.0.2**: Complete working system with all features and bug fixes

## 📞 Support

For issues and questions:
- **Email**: team@fayvad.com
- **Documentation**: Check this guide and inline code comments
- **Testing**: Use provided test scripts to verify functionality

## 🎯 Next Steps

1. **Install FBS Suite**: Use `install_v2.0.2.py`
2. **Test Integration**: Run `test_complete_workflow.py`
3. **Create Your Solution**: Initialize with your solution name
4. **Set Up Databases**: Configure required Odoo modules
5. **Start Building**: Use the provided interfaces for your business logic

---

**FBS Suite v2.0.2** - Ready for production use! 🚀
