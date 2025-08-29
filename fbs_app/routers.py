"""
FBS App Database Router

Database router for handling multi-database operations with solution-specific isolation.
The solution databases are created by the solution implementation, not by FBS apps.
"""

import logging

logger = logging.getLogger('fbs_app')


class FBSDatabaseRouter:
    """Database router for FBS multi-database architecture with solution isolation"""
    
    def db_for_read(self, model, **hints):
        """Route models to appropriate databases based on app and context"""
        if not hasattr(model, '_meta') or not hasattr(model._meta, 'app_label'):
            return None
            
        app_label = model._meta.app_label
        
        # Check for solution-specific database hints first (highest priority)
        if 'solution_db' in hints:
            solution_db = hints['solution_db']
            if solution_db in self._get_solution_databases():
                logger.debug(f"Routing to solution database: {solution_db}")
                return solution_db
            else:
                logger.warning(f"Solution database {solution_db} not found, falling back to default")
                return None
        
        # Check for company_id-based routing (only if database exists)
        if 'company_id' in hints:
            company_id = hints['company_id']
            solution_db = f"djo_{company_id}_db"
            if solution_db in self._get_solution_databases():
                logger.debug(f"Routing to company database: {solution_db}")
                return solution_db
        
        # License manager models go to default database (embedded licensing)
        if app_label == 'fbs_license_manager':
            return 'default'
        
        # FBS app models go to system database (default)
        if app_label == 'fbs_app':
            return 'default'
        
        # DMS models can go to solution databases if specified and exist
        if app_label == 'fbs_dms' and 'company_id' in hints:
            company_id = hints['company_id']
            solution_db = f"djo_{company_id}_db"
            if solution_db in self._get_solution_databases():
                return solution_db
        
        # DMS models default to default database if no specific routing
        if app_label == 'fbs_dms':
            return 'default'
        
        return None
    
    def db_for_write(self, model, **hints):
        """Route models to appropriate databases for writes"""
        if not hasattr(model, '_meta') or not hasattr(model._meta, 'app_label'):
            return None
            
        app_label = model._meta.app_label
        
        # Check for solution-specific database hints first (highest priority)
        if 'solution_db' in hints:
            solution_db = hints['solution_db']
            if solution_db in self._get_solution_databases():
                logger.debug(f"Routing write to solution database: {solution_db}")
                return solution_db
            else:
                logger.warning(f"Solution database {solution_db} not found, falling back to default")
                return None
        
        # Check for company_id-based routing (only if database exists)
        if 'company_id' in hints:
            company_id = hints['company_id']
            solution_db = f"djo_{company_id}_db"
            if solution_db in self._get_solution_databases():
                logger.debug(f"Routing write to company database: {solution_db}")
                return solution_db
        
        # License manager models go to default database (embedded licensing)
        if app_label == 'fbs_license_manager':
            return 'default'
        
        # FBS app models go to system database (default)
        if app_label == 'fbs_app':
            return 'default'
        
        # DMS models can go to solution databases if specified and exist
        if app_label == 'fbs_dms' and 'company_id' in hints:
            company_id = hints['company_id']
            solution_db = f"djo_{company_id}_db"
            if solution_db in self._get_solution_databases():
                return solution_db
        
        # DMS models default to default database if no specific routing
        if app_label == 'fbs_dms':
            return 'default'
        
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations within the same database"""
        # Get the database for each object
        db1 = self.db_for_read(obj1)
        db2 = self.db_for_read(obj2)
        
        # If both objects are routed to the same database, allow the relation
        if db1 == db2:
            return True
        
        # Special case: allow relations between auth.User and fbs_app models
        # since they both go to the default database
        if hasattr(obj1, '_meta') and hasattr(obj2, '_meta'):
            app1 = obj1._meta.app_label
            app2 = obj2._meta.app_label
            
            # Allow relations between auth and fbs_app (both go to default)
            if (app1 == 'auth' and app2 == 'fbs_app') or (app1 == 'fbs_app' and app2 == 'auth'):
                return True
            
            # Allow relations between auth and fbs_dms (both go to default)
            if (app1 == 'auth' and app2 == 'fbs_dms') or (app1 == 'fbs_dms' and app2 == 'auth'):
                return True
            
            # Allow relations between auth and fbs_license_manager (both go to default)
            if (app1 == 'auth' and app2 == 'fbs_license_manager') or (app1 == 'fbs_license_manager' and app2 == 'auth'):
                return True
        
        # Only allow relations between objects in the same database
        return False
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Route migrations to appropriate databases"""
        if app_label == 'fbs_license_manager':
            # License manager models go to licensing database
            return db == 'licensing'
        elif app_label == 'fbs_app':
            # FBS app models go to system database
            return db == 'default'
        elif app_label == 'fbs_dms':
            # DMS models can go to solution databases or default
            if db.startswith('djo_') or db.startswith('fbs_'):
                return True  # Allow migration to solution databases
            return db == 'default'  # Also allow to default
        return None
    
    def allow_join(self, model, **hints):
        """Allow joins within the same database"""
        # Only allow joins within the same database context
        return True
    
    def _get_solution_databases(self):
        """Get list of available solution databases from settings"""
        from django.conf import settings
        solution_dbs = []
        for db_name in settings.DATABASES.keys():
            if db_name.startswith('djo_') or db_name.startswith('fbs_'):
                solution_dbs.append(db_name)
        return solution_dbs
