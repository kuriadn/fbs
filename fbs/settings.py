import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-your-secret-key-here'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'fayvad_core',
    'fayvad_core.discovery',
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
]

ROOT_URLCONF = 'fayvad_core.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'fayvad_core.wsgi.application'

# Database - Django's own tables (FBS system tables)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fbs_system_db',  # Separate database for FBS system tables
        'USER': 'fayvad',
        'PASSWORD': 'MeMiMo@0207',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ['v1'],
}

# JWT settings
JWT_SECRET_KEY = SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# CORS settings for frontend integration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-database',
    'x-api-version',
]

# Odoo Configuration
ODOO_CONFIG = {
    'BASE_URL': 'http://localhost:8069',
    'MASTER_PASSWORD': 'admin',
    'DATABASE': 'fayvad',
    'USERNAME': 'dn.kuria@gmail.com',
    'PASSWORD': 'MeMiMo@0207',
    'TIMEOUT': 30,
    'MAX_RETRIES': 3,
    'RETRY_DELAY': 1,
    'CONNECTION_POOL_SIZE': 10,
    'MAX_POOL_SIZE': 20,
    'POOL_TIMEOUT': 30,
    'VERIFY_SSL': False,
    'CERT_PATH': None
}

# Legacy settings for backward compatibility
ODOO_BASE_URL = ODOO_CONFIG['BASE_URL']
ODOO_MASTER_PASSWORD = ODOO_CONFIG['MASTER_PASSWORD']
ODOO_DATABASE = ODOO_CONFIG['DATABASE']
ODOO_USER = ODOO_CONFIG['USERNAME']
ODOO_PASSWORD = ODOO_CONFIG['PASSWORD']

# FBS Configuration for Dynamic Solution Database Creation
FBS_CONFIG = {
    'table_prefix': 'fbs_',           # Prefix for FBS system tables
    'business_prefix': '',             # Business table prefix (set per solution)
    'auto_create_tables': True,        # Auto-create tables on startup
    'enable_migrations': True,         # Enable schema migrations
    'database_naming_pattern': 'fbs_{solution_name}_db',  # Database naming pattern
    'default_database_config': {
        'host': 'localhost',
        'port': '5432',
        'user': 'fayvad',
        'password': 'MeMiMo@0207'
    },
    'odoo_integration': {
        'use_solution_db_as_odoo': True,  # Use the same database for Odoo and FBS
        'auto_populate_odoo_modules': True,  # Auto-populate with relevant Odoo modules
        'default_odoo_user': 'admin',
        'default_odoo_password': 'admin'
    }
}

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
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
} 