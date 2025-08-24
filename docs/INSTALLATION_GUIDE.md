# FBS Comprehensive Installation Guide

**FBS (Fayvad Business Suite)** - Complete Django App Ecosystem for MSME Business Management

## Overview

This guide explains how to install and configure the complete FBS ecosystem in your existing Django project. The FBS ecosystem consists of three integrated apps:

### **FBS App (Core Business Suite)**
- **Business Intelligence & Analytics**
- **Workflow Management**
- **Compliance Management**
- **Basic Accounting**
- **MSME Business Tools**
- **Odoo ERP Integration**

### **FBS DMS (Document Management System)**
- **Document Storage & Management**
- **Workflow Approvals**
- **File Attachments**
- **Search & Filtering**
- **Odoo Synchronization**

### **FBS License Manager**
- **Feature Control & Licensing**
- **Usage Tracking & Limits**
- **Upgrade Prompts**
- **Commercial Deployment Support**

## Prerequisites

- Python 3.10 or higher
- Django 4.2+ or 5.0+
- PostgreSQL database
- Redis (optional, for caching)
- Odoo 17 CE (for ERP integration)

## Installation Methods

### Method 1: Install from Source (Recommended)

```bash
# Clone the complete FBS repository
git clone https://github.com/kuriadn/fbs.git
cd fbs

# Install all three apps in development mode
pip install -e .
```

### Method 2: Manual Installation

```bash
# Copy all three app directories to your Django project
cp -r fbs_app/ /path/to/your/django/project/
cp -r fbs_dms/ /path/to/your/django/project/
cp -r fbs_license_manager/ /path/to/your/django/project/

# Or add to your project's apps directory
mkdir -p /path/to/your/django/project/apps/
cp -r fbs_app/ /path/to/your/django/project/apps/
cp -r fbs_dms/ /path/to/your/django/project/apps/
cp -r fbs_license_manager/ /path/to/your/django/project/apps/
```

### Method 3: Individual App Installation

```bash
# Install individual apps if needed
pip install -e fbs_app/
pip install -e fbs_dms/
pip install -e fbs_license_manager/
```

## Django Project Configuration

### 1. Add to INSTALLED_APPS

In your Django project's `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    
    # FBS Ecosystem
    'fbs_app.apps.FBSAppConfig',           # Core business suite
    'fbs_dms.apps.FBSDMSConfig',           # Document management
    'fbs_license_manager.apps.FBSLicenseManagerConfig',  # License management
]
```

### 2. Add FBS Middleware

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # FBS Middleware (add before authentication)
    'fbs_app.middleware.DatabaseRoutingMiddleware',
    'fbs_app.middleware.RequestLoggingMiddleware',
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### 3. Configure REST Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'fbs_app.authentication.HandshakeAuthentication',
        'fbs_app.authentication.OdooTokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'fbs_app.authentication.HandshakePermission',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### 4. Add FBS URLs

In your project's `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # Your existing URLs
    path('admin/', admin.site.urls),
    
    # FBS App URLs
    path('fbs/', include('fbs_app.urls')),
    
    # Or customize the prefix
    path('business/', include('fbs_app.urls')),  # Custom prefix
]
```

### 5. Environment Configuration

Copy the environment template and customize it:

```bash
cp env.example .env
```

Edit `.env` with your specific configuration:

```bash
# Core Django settings
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# FBS App specific settings
FBS_ENABLE_MSME_FEATURES=True
FBS_ENABLE_ACCOUNTING_FEATURES=True
ODOO_BASE_URL=http://localhost:8069
```

### 6. FBS App Configuration

The FBS app configuration is automatically loaded from environment variables. All settings are consolidated in the main `settings.py` file.

Key configuration sections include:

```python
# FBS App Core Configuration
FBS_APP = {
    # Database configuration
    'DATABASE_ENGINE': 'django.db.backends.postgresql',
    'DATABASE_HOST': 'localhost',
    'DATABASE_PORT': '5432',
    'DATABASE_USER': 'your_database_user',
    'DATABASE_PASSWORD': 'your_database_password',
    
    # Odoo integration
    'ODOO_BASE_URL': 'http://localhost:8069',
    'ODOO_TIMEOUT': 30,
    'ODOO_MAX_RETRIES': 3,
    
    # Features
    'ENABLE_MSME_FEATURES': True,
    'ENABLE_BI_FEATURES': True,
    'ENABLE_WORKFLOW_FEATURES': True,
    'ENABLE_COMPLIANCE_FEATURES': True,
    'ENABLE_ACCOUNTING_FEATURES': True,
}

# FBS Authentication Configuration
FBS_AUTHENTICATION = {
    'ENABLE_HANDSHAKE_AUTH': True,
    'ENABLE_TOKEN_AUTH': True,
    'HANDSHAKE_EXPIRY_HOURS': 24,
}

# FBS URL Configuration
FBS_URL_PREFIX = 'fbs/'  # Can be overridden via environment
```

## Database Setup

### 1. Run Migrations

```bash
python manage.py makemigrations fbs_app
python manage.py migrate
```

### 2. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 3. Load Initial Data (Optional)

```bash
python manage.py loaddata fbs_app/fixtures/initial_data.json
```

## Odoo Integration Setup

### 1. Install Odoo 17 CE

Follow the [official Odoo installation guide](https://www.odoo.com/documentation/17.0/administration/install.html).

### 2. Required Odoo Modules

Ensure these modules are available in your Odoo installation:

- `base` (always required)
- `web` (UI framework)
- `mail` (messaging)
- `contacts` (partner management)
- `sale` (sales management)
- `product` (product management)
- `account` (financial management)
- `hr` (staff management)
- `project` (project management)
- `crm` (customer relationship management)

### 3. Configure Odoo Database

```bash
# Create a reference database
python3 /path/to/odoo/odoo-bin -d fayvad_reference --stop-after-init

# Install required modules
python3 /path/to/odoo/odoo-bin -d fayvad_reference -i base,web,mail,contacts,sale,product,account,hr,project,crm --stop-after-init
```

## Testing the Installation

### 1. Start Django Server

```bash
python manage.py runserver
```

### 2. Access FBS Admin

Navigate to: `http://localhost:8000/admin/`

You should see FBS models in the admin interface.

### 3. Test Service Interfaces

```bash
# Health check
curl http://localhost:8000/fbs/health/

# Service interfaces
# Use Django shell to test service interfaces
```

## Configuration Options

### Customizing URL Structure

```python
# In your settings.py
FBS_URL_PREFIX = 'business/'  # Changes /fbs/ to /business/
# FBS_API_PREFIX removed - no more API endpoints
```

### Feature Toggles

```python
FBS_APP = {
    'ENABLE_MSME_FEATURES': True,      # MSME business tools
    'ENABLE_BI_FEATURES': True,        # Business intelligence
    'ENABLE_WORKFLOW_FEATURES': True,  # Workflow management
    'ENABLE_COMPLIANCE_FEATURES': True, # Compliance tools
    'ENABLE_ACCOUNTING_FEATURES': True, # Basic accounting
}
```

### Authentication Configuration

```python
FBS_APP = {
    'HANDSHAKE_EXPIRY_HOURS': 48,     # Extend handshake validity
    'REQUEST_RATE_LIMIT': 2000,           # Increase rate limits
'REQUEST_BURST_LIMIT': 200,
}
```

## Troubleshooting

### Common Issues

1. **Import Error: No module named 'fbs_app'**
   - Ensure the app is properly installed
   - Check your Python path
   - Verify the app directory structure

2. **Database Error: JSON field not supported**
   - Use PostgreSQL database
   - Ensure Django version supports JSON fields

3. **Migration Error: Table already exists**
   - Check for conflicting migrations
   - Use `--fake-initial` if needed

4. **Odoo Connection Error**
   - Verify Odoo is running
   - Check database credentials
   - Ensure required modules are installed

### Debug Mode

Enable debug mode for troubleshooting:

```python
DEBUG = True

# Add FBS debug settings
FBS_APP = {
    'LOG_LEVEL': 'DEBUG',
    'LOG_REQUESTS': True,
    'LOG_RESPONSES': True,
}
```

## Production Deployment

### 1. Security Settings

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# FBS Security
FBS_APP = {
    'ALLOW_CORS': False,  # Disable CORS in production
    'CORS_ORIGINS': ['https://yourdomain.com'],
    'CSRF_TRUSTED_ORIGINS': ['https://yourdomain.com'],
}
```

### 2. Database Optimization

```python
# Use connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
        },
    }
}
```

### 3. Caching Configuration

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Support and Documentation

- **Documentation**: [https://fbs-app.readthedocs.io/](https://fbs-app.readthedocs.io/)
- **GitHub**: [https://github.com/fayvad/fbs-app](https://github.com/fayvad/fbs-app)
- **Issues**: [https://github.com/fayvad/fbs-app/issues](https://github.com/fayvad/fbs-app/issues)
- **Email**: info@fayvad.com

## License

This software is proprietary and confidential. Copyright © 2025 Fayvad Digital. All rights reserved.
