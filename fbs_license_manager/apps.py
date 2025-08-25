"""
Django App Configuration for FBS License Manager
"""

from django.apps import AppConfig


class FBSLicenseManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fbs_license_manager'
    verbose_name = 'FBS License Manager'
    
    def ready(self):
        """App initialization when ready"""
        try:
            import fbs_license_manager.signals
        except ImportError:
            pass



