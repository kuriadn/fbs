from django.apps import AppConfig


class FBSAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fbs_app'
    verbose_name = 'FBS - Fayvad Business Suite'
    version = '2.0.3'
    
    def ready(self):
        """Initialize app when Django starts"""
        # Use lazy import to avoid circular import issues
        if not getattr(self, '_signals_loaded', False):
            try:
                import fbs_app.signals  # noqa
                self._signals_loaded = True
            except ImportError as e:
                # Log the error but don't fail app startup
                import logging
                logger = logging.getLogger('fbs_app')
                logger.warning(f"Could not load signals: {e}")
                pass
