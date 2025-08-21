"""
FBS App Configuration Template

This file shows the required configuration for the FBS app.
Copy these settings to your Django project's settings.py or environment variables.
"""

# FBS App Configuration
FBS_APP = {
    # Odoo Connection Settings (REQUIRED)
    'ODOO_BASE_URL': 'http://localhost:8069',  # Odoo server URL
    'ODOO_TIMEOUT': 30,  # Connection timeout in seconds
    'ODOO_MAX_RETRIES': 3,  # Maximum retry attempts
    
    # Odoo Database Credentials (REQUIRED - NO HARDCODED DEFAULTS)
    'DATABASE_USER': 'odoo',  # Odoo database username
    'DATABASE_PASSWORD': 'your_secure_password_here',  # Odoo database password
    
    # Database Configuration (REQUIRED)
    'default_database_config': {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': 'your_postgres_password_here',  # PostgreSQL password
    },
    
    # Solution Configuration
    'default_solutions': ['fbs_rental_db', 'fbs_retail_db', 'fbs_manufacturing_db'],
    
    # Cache Configuration
    'CACHE_TIMEOUT': 300,  # Cache timeout in seconds
    'CACHE_PREFIX': 'fbs_',
    
    # Logging Configuration
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    
    # Security Configuration
    'SECURE_HANDSHAKE': True,  # Enable secure handshake authentication
    'TOKEN_EXPIRY_HOURS': 24,  # Token expiry time in hours
    
    # Feature Flags
    'ENABLE_ODOO_DISCOVERY': True,  # Enable Odoo model discovery
    'ENABLE_WORKFLOW_ENGINE': True,  # Enable workflow engine
    'ENABLE_BI_ANALYTICS': True,  # Enable business intelligence
    'ENABLE_COMPLIANCE_TRACKING': True,  # Enable compliance tracking
}

# Environment Variables (Alternative to FBS_APP dict)
# Set these in your .env file or system environment:
#
# ODOO_BASE_URL=http://localhost:8069
# ODOO_DATABASE_USER=odoo
# ODOO_DATABASE_PASSWORD=your_secure_password
# POSTGRES_PASSWORD=your_postgres_password
# FBS_ENVIRONMENT=production
# FBS_LOG_LEVEL=INFO

# Database Configuration for Multi-Database Setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fbs_system_db',
        'USER': 'postgres',
        'PASSWORD': 'your_postgres_password_here',  # Set via environment variable
        'HOST': 'localhost',
        'PORT': '5432',
    },
    # Solution-specific databases will be created dynamically
    # 'djo_rental_db': {...},
    # 'fbs_rental_db': {...},
}

# Middleware Configuration
MIDDLEWARE = [
    # ... other middleware ...
    'fbs_app.middleware.database_routing.DatabaseRoutingMiddleware',
    'fbs_app.middleware.request_logging.RequestLoggingMiddleware',
]

# Database Routers
DATABASE_ROUTERS = ['fbs_app.routers.FBSDatabaseRouter']

# Installed Apps
INSTALLED_APPS = [
    # ... other apps ...
    'fbs_app.apps.FBSAppConfig',
]

# URL Configuration
# Include FBS URLs in your main urls.py:
# path('fbs/', include('fbs_app.urls')),
