"""
FBS App Database Router

Database router for handling multi-database operations.
"""

import logging

logger = logging.getLogger('fbs_app')


class FBSDatabaseRouter:
    """Database router for FBS app multi-database operations"""
    
    def db_for_read(self, model, **hints):
        """Suggest the database to use for reads of model objects"""
        # Check if model has a specific database preference
        if hasattr(model, '_meta') and hasattr(model._meta, 'app_label'):
            if model._meta.app_label == 'fbs_app':
                # FBS app models can be read from any database
                # The middleware will set the appropriate database context
                # Check if we have a specific database hint
                if 'database' in hints:
                    return hints['database']
                return None  # Let Django decide based on request context
        
        return None
    
    def db_for_write(self, model, **hints):
        """Suggest the database to use for writes of model objects"""
        # Check if model has a specific database preference
        if hasattr(model, '_meta') and hasattr(model._meta, 'app_label'):
            if model._meta.app_label == 'fbs_app':
                # FBS app models can be written to any database
                # The middleware will set the appropriate database context
                return None  # Let Django decide based on request context
        
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation if a model in the FBS app is involved"""
        if obj1._meta.app_label == 'fbs_app' or obj2._meta.app_label == 'fbs_app':
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Make sure the FBS app models get created on the right database"""
        if app_label == 'fbs_app':
            # FBS app models should be created on the default database
            # This ensures the app's schema is available
            return db == 'default'
        return None
    
    def allow_join(self, model, **hints):
        """Allow joins between FBS app models"""
        if hasattr(model, '_meta') and model._meta.app_label == 'fbs_app':
            return True
        return None
