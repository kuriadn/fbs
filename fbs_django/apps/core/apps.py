"""
FBS Core App Configuration

Central orchestration and shared functionality for FBS.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """FBS Core application configuration"""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    label = 'fbs_core'
    verbose_name = 'FBS Core'

    def ready(self):
        """Initialize the FBS Core app"""
        # Import signals to ensure they're registered
        import apps.core.signals

        # Initialize audit logging
        from apps.core.utils.audit import setup_audit_logging
        setup_audit_logging()

        # Setup system settings cache
        from apps.core.utils.settings import initialize_system_settings
        initialize_system_settings()