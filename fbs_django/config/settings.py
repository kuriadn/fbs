"""
Django settings for FBS (Fayvad Business Suite) v4.0.0

Complete Django implementation of FBS with multi-tenant architecture,
TailwindCSS templates, and PWA capabilities.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# SECURITY SETTINGS
# ============================================================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-fbs-development-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',')

# ============================================================================
# APPLICATION DEFINITION
# ============================================================================

INSTALLED_APPS = [
    # Django core
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'django_filters',
    'channels',  # For WebSocket support
    'django_celery_beat',  # Background tasks
    'tailwindcss',  # UI framework

    # FBS Apps
    'apps.core',
    'apps.dms',
    'apps.licensing',
    'apps.module_gen',
    'apps.odoo_integration',
    'apps.discovery',
    'apps.virtual_fields',
    'apps.msme',
    'apps.bi',
    'apps.workflows',
    'apps.compliance',
    'apps.accounting',
    'apps.auth_handshake',
    'apps.onboarding',
    'apps.notifications',
    'apps.signals',
]

# ============================================================================
# MIDDLEWARE
# ============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # FBS Custom Middleware
    'apps.core.middleware.DatabaseRouterMiddleware',
    'apps.core.middleware.RequestLoggingMiddleware',
]

# ============================================================================
# URL CONFIGURATION
# ============================================================================

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ============================================================================
# TEMPLATES (Disabled for headless FBS)
# ============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# FBS Database Credential Matrix:
# - fbs_system_db: fayvad/MeMiMo@0207 (Django system database)
# - fbs_{solution}_db: fayvad/MeMiMo@0207 & admin/MeMiMo@0207 & odoo/four@One2 (Odoo databases)
# - djo_{solution}_db: fayvad/MeMiMo@0207 & liz.gichane/MeMiMo@0207 (Django solution databases)

# Multi-tenant database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'fbs_system_db'),
        'USER': os.getenv('DB_USER', 'fayvad'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'MeMiMo@0207'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Dynamic database routing for solutions
DATABASE_ROUTERS = ['apps.core.database_router.FBSDatabaseRouter']

# ============================================================================
# ODOO INTEGRATION SETTINGS
# ============================================================================

ODOO_CONFIG = {
    'BASE_URL': os.getenv('ODOO_URL', 'http://localhost:8069'),
    'DB': os.getenv('ODOO_DB', 'odoo'),
    'USERNAME': os.getenv('ODOO_USER', 'fayvad'),
    'PASSWORD': os.getenv('ODOO_PASSWORD', 'MeMiMo@0207'),
    'TIMEOUT': int(os.getenv('ODOO_TIMEOUT', '30')),
    'MAX_RETRIES': int(os.getenv('ODOO_MAX_RETRIES', '3')),
}

# ============================================================================
# FBS-SPECIFIC SETTINGS
# ============================================================================

FBS_CONFIG = {
    'MODULE_TEMPLATES_DIR': BASE_DIR / 'apps/module_gen/templates',
    'UPLOAD_DIR': BASE_DIR / 'uploads',
    'LICENSE_ENCRYPTION_KEY': os.getenv('LICENSE_KEY', 'fbs-license-key'),
    'REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_TIMEOUT': int(os.getenv('CACHE_TIMEOUT', '300')),
    'MAX_UPLOAD_SIZE': int(os.getenv('MAX_UPLOAD_SIZE', '10485760')),  # 10MB
}

# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

AUTH_USER_MODEL = 'core.FBSUser'

# REST Framework configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.core.authentication.FBSTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'apps.core.permissions.FBSLicensePermission',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# ============================================================================
# TAILWINDCSS CONFIGURATION (Disabled for headless FBS)
# ============================================================================

# TAILWINDCSS = {
#     'SOURCE_DIRS': [
#         BASE_DIR / 'templates',
#         BASE_DIR / 'apps' / '**' / 'templates',
#     ],
# }

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = os.getenv('TIME_ZONE', 'UTC')

# ============================================================================
# CACHING CONFIGURATION
# ============================================================================

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    }
}

# ============================================================================
# STATIC & MEDIA FILES
# ============================================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

# ============================================================================
# PASSWORD VALIDATION
# ============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================================================
# DEFAULT AUTO FIELD
# ============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# PWA CONFIGURATION (Disabled for headless FBS)
# ============================================================================

# PWA_CONFIG = {
#     'NAME': 'FBS Business Suite',
#     'SHORT_NAME': 'FBS',
#     'DESCRIPTION': 'Enterprise Business Management Suite',
#     'START_URL': '/',
#     'DISPLAY': 'standalone',
#     'BACKGROUND_COLOR': '#ffffff',
#     'THEME_COLOR': '#1f2937',
#     'ICONS': [
#         {
#             'src': '/static/icons/icon-192.png',
#             'sizes': '192x192',
#             'type': 'image/png'
#         },
#         {
#             'src': '/static/icons/icon-512.png',
#             'sizes': '512x512',
#             'type': 'image/png'
#         }
#     ]
# }
