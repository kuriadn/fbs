"""
FBS DMS App Configuration

Django app configuration for the FBS Document Management System.
"""

from django.apps import AppConfig


class FBSDMSConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fbs_dms'
    verbose_name = 'FBS Document Management System'
    
    def ready(self):
        """Initialize app when Django is ready"""
        try:
            import fbs_dms.signals  # noqa
        except ImportError:
            pass
