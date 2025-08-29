"""
Comprehensive Django Settings for FBS Project

This provides all Django configuration needed to run fbs_app, consolidated from
both the main project and the FBS app configuration.
"""

import os
from pathlib import Path
import sys

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-in-production')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'fbs_app',  # Our embeddable FBS app
    'fbs_license_manager',  # Standalone license management
    'fbs_dms',  # Document management system
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # FBS App middleware
    'fbs_app.middleware.DatabaseRoutingMiddleware',
    'fbs_app.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'fbs_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'fbs_app.context_processors.fbs_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'fbs_project.wsgi.application'

# Database - Multi-database setup
DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('DB_NAME', 'fbs_system_db'),
        'USER': os.environ.get('DB_USER', 'odoo'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'four@One2'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
    # Solution-specific databases (djo_{solution}_db, fbs_{solution}_db)
    # are created by the solution implementation and added to settings
    # by the solution, not by FBS apps
}

# Database Routers
DATABASE_ROUTERS = [
    'fbs_app.routers.FBSDatabaseRouter',
]

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# FBS App static files
FBS_STATIC_URL = 'fbs/static/'
FBS_STATIC_ROOT = os.path.join(BASE_DIR, 'fbs_static')

# FBS App media files
FBS_MEDIA_URL = 'fbs/media/'
FBS_MEDIA_ROOT = os.path.join(BASE_DIR, 'fbs_media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'fbs_app': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# FBS APP CONFIGURATION
# =============================================================================

# FBS App Core Configuration
FBS_APP = {
    # Database configuration
    'DATABASE_ENGINE': os.environ.get('FBS_DB_ENGINE', 'django.db.backends.postgresql'),
    'DATABASE_HOST': os.environ.get('FBS_DB_HOST', 'localhost'),
    'DATABASE_PORT': os.environ.get('FBS_DB_PORT', '5432'),
    'DATABASE_USER': os.environ.get('FBS_DB_USER', 'odoo'),
    'DATABASE_PASSWORD': os.environ.get('FBS_DB_PASSWORD', 'four@One2'),
    
    # Odoo integration
    'ODOO_BASE_URL': os.environ.get('ODOO_BASE_URL', 'http://localhost:8069'),
    'ODOO_TIMEOUT': int(os.environ.get('ODOO_TIMEOUT', '30')),
    'ODOO_MAX_RETRIES': int(os.environ.get('ODOO_MAX_RETRIES', '3')),
    
    # Authentication
    'HANDSHAKE_EXPIRY_HOURS': int(os.environ.get('FBS_HANDSHAKE_EXPIRY_HOURS', '24')),
    'REQUEST_RATE_LIMIT': int(os.environ.get('FBS_REQUEST_RATE_LIMIT', '1000')),  # requests per hour
    'REQUEST_BURST_LIMIT': int(os.environ.get('FBS_REQUEST_BURST_LIMIT', '100')),   # requests per minute
    
    # Features
    'ENABLE_MSME_FEATURES': os.environ.get('FBS_ENABLE_MSME_FEATURES', 'True').lower() == 'true',
    'ENABLE_BI_FEATURES': os.environ.get('FBS_ENABLE_BI_FEATURES', 'True').lower() == 'true',
    'ENABLE_WORKFLOW_FEATURES': os.environ.get('FBS_ENABLE_WORKFLOW_FEATURES', 'True').lower() == 'true',
    'ENABLE_COMPLIANCE_FEATURES': os.environ.get('FBS_ENABLE_COMPLIANCE_FEATURES', 'True').lower() == 'true',
    'ENABLE_ACCOUNTING_FEATURES': os.environ.get('FBS_ENABLE_ACCOUNTING_FEATURES', 'True').lower() == 'true',
    
    # Logging
    'LOG_LEVEL': os.environ.get('FBS_LOG_LEVEL', 'INFO'),
    'LOG_REQUESTS': os.environ.get('FBS_LOG_REQUESTS', 'True').lower() == 'true',
    'LOG_RESPONSES': os.environ.get('FBS_LOG_RESPONSES', 'False').lower() == 'true',
    
    # Caching
    'CACHE_ENABLED': os.environ.get('FBS_CACHE_ENABLED', 'True').lower() == 'true',
    'CACHE_TIMEOUT': int(os.environ.get('FBS_CACHE_TIMEOUT', '300')),  # 5 minutes
    'REDIS_URL': os.environ.get('FBS_REDIS_URL', 'redis://localhost:6379/0'),
    
    # Security
    'ALLOW_CORS': os.environ.get('FBS_ALLOW_CORS', 'True').lower() == 'true',
    'CORS_ORIGINS': os.environ.get('FBS_CORS_ORIGINS', '*').split(','),  # Override in production
    'CSRF_TRUSTED_ORIGINS': os.environ.get('FBS_CSRF_TRUSTED_ORIGINS', '').split(',') if os.environ.get('FBS_CSRF_TRUSTED_ORIGINS') else [],
    
    # Business Logic
    'DEFAULT_MSME_TEMPLATE': os.environ.get('FBS_DEFAULT_MSME_TEMPLATE', 'standard'),
    'AUTO_INSTALL_MODULES': os.environ.get('FBS_AUTO_INSTALL_MODULES', 'True').lower() == 'true',
    'ENABLE_AUTO_DISCOVERY': os.environ.get('FBS_ENABLE_AUTO_DISCOVERY', 'True').lower() == 'true',
}

# FBS Authentication Configuration
FBS_AUTHENTICATION = {
    'ENABLE_HANDSHAKE_AUTH': os.environ.get('FBS_ENABLE_HANDSHAKE_AUTH', 'True').lower() == 'true',
    'ENABLE_TOKEN_AUTH': os.environ.get('FBS_ENABLE_TOKEN_AUTH', 'True').lower() == 'true',
    'HANDSHAKE_EXPIRY_HOURS': int(os.environ.get('FBS_HANDSHAKE_EXPIRY_HOURS', '24')),
}

# FBS URL Configuration
FBS_URL_PREFIX = os.environ.get('FBS_URL_PREFIX', 'fbs/')

# FBS Templates
FBS_TEMPLATE_DIRS = []

# =============================================================================
# ENVIRONMENT-SPECIFIC OVERRIDES
# =============================================================================

if DEBUG:
    # Development-specific settings
    FBS_APP['LOG_LEVEL'] = 'DEBUG'
    FBS_APP['LOG_REQUESTS'] = True
    FBS_APP['LOG_RESPONSES'] = True
    
    # Development CORS settings
    CORS_ALLOW_ALL_ORIGINS = True
    
    # Development logging
    LOGGING['loggers']['fbs_app']['level'] = 'DEBUG'
    
    # Development database (SQLite for faster development)
    if os.environ.get('FBS_USE_SQLITE', 'False').lower() == 'true':
        DATABASES['default'] = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
else:
    # Production-specific settings
    FBS_APP['LOG_LEVEL'] = 'WARNING'
    FBS_APP['LOG_REQUESTS'] = False
    FBS_APP['LOG_RESPONSES'] = False
    
    # Production security
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    
    # Production CORS (restrict to specific origins)
    CORS_ALLOWED_ORIGINS = os.environ.get('FBS_CORS_ALLOWED_ORIGINS', '').split(',')
    if not CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS = [
            "https://yourdomain.com",
            "https://www.yourdomain.com",
        ]

# =============================================================================
# TESTING CONFIGURATION
# =============================================================================

if 'test' in sys.argv or 'pytest' in sys.argv:
    # Test-specific settings
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
    
    # Disable logging during tests
    LOGGING['loggers']['fbs_app']['level'] = 'ERROR'
    
    # Test-specific FBS settings
    FBS_APP['CACHE_ENABLED'] = False
    FBS_APP['LOG_REQUESTS'] = False
    FBS_APP['LOG_RESPONSES'] = False
