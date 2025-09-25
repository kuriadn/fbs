"""
FBS Database Router Middleware

Handles multi-tenant database routing for FBS solutions.
Routes database operations to the appropriate solution database.
"""
import threading
from django.db import connections
from django.conf import settings
from typing import Optional


# Thread-local storage for current solution context
_local = threading.local()


class FBSDatabaseRouter:
    """
    Database router for FBS multi-tenant architecture.

    Routes database operations based on the current solution context.
    """

    def db_for_read(self, model, **hints):
        """Route read operations to the appropriate database"""
        solution_name = self._get_current_solution()
        if solution_name and self._is_solution_model(model):
            return f'djo_{solution_name}_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """Route write operations to the appropriate database"""
        solution_name = self._get_current_solution()
        if solution_name and self._is_solution_model(model):
            return f'djo_{solution_name}_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between objects in the same solution"""
        solution1 = getattr(obj1, 'solution', None)
        solution2 = getattr(obj2, 'solution', None)

        # If both objects belong to the same solution, allow the relation
        if solution1 and solution2 and solution1 == solution2:
            return True

        # Allow relations between system models and solution models
        if self._is_system_model(obj1.__class__) or self._is_system_model(obj2.__class__):
            return True

        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Control which models can be migrated to which databases"""
        if db == 'default':
            # System models go to default database
            return app_label == 'core' and model_name in [
                'fbssolution', 'fbssystemsettings'
            ]
        elif db.startswith('djo_') and db.endswith('_db'):
            # Solution-specific models go to solution databases
            return app_label != 'core' or model_name not in [
                'fbssolution', 'fbssystemsettings'
            ]

        return None

    def _is_solution_model(self, model) -> bool:
        """Check if a model belongs to a solution database"""
        # Models with a 'solution' field are solution-scoped
        return hasattr(model, 'solution')

    def _is_system_model(self, model_class) -> bool:
        """Check if a model is a system-level model"""
        from apps.core.models import FBSSolution, FBSSystemSettings
        return model_class in [FBSSolution, FBSSystemSettings]

    def _get_current_solution(self) -> Optional[str]:
        """Get the current solution name from thread-local storage"""
        return getattr(_local, 'solution_name', None)


class DatabaseRouterMiddleware:
    """
    Middleware to set database routing context based on request.

    Sets the current solution context for database routing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract solution from request
        solution_name = self._get_solution_from_request(request)

        # Set solution context
        if solution_name:
            _local.solution_name = solution_name

        response = self.get_response(request)

        # Clean up solution context
        if hasattr(_local, 'solution_name'):
            delattr(_local, 'solution_name')

        return response

    def _get_solution_from_request(self, request) -> Optional[str]:
        """Extract solution name from various request sources"""

        # Check URL parameters
        solution_name = getattr(request, 'solution_name', None)
        if solution_name:
            return solution_name

        # Check authenticated user
        if hasattr(request, 'user') and request.user.is_authenticated:
            if hasattr(request.user, 'solution'):
                return request.user.solution.name

        # Check headers
        solution_header = request.META.get('HTTP_X_SOLUTION_NAME')
        if solution_header:
            return solution_header

        # Check session
        if hasattr(request, 'session'):
            solution_name = request.session.get('current_solution')
            if solution_name:
                return solution_name

        # Check query parameters
        solution_param = request.GET.get('solution') or request.POST.get('solution')
        if solution_param:
            return solution_param

        return None


# Utility functions for solution context management
def set_current_solution(solution_name: str):
    """Set the current solution context"""
    _local.solution_name = solution_name


def get_current_solution() -> Optional[str]:
    """Get the current solution context"""
    return getattr(_local, 'solution_name', None)


def clear_current_solution():
    """Clear the current solution context"""
    if hasattr(_local, 'solution_name'):
        delattr(_local, 'solution_name')


def get_solution_database_name(solution_name: str) -> str:
    """Get the database name for a solution"""
    return f'djo_{solution_name}_db'


def ensure_solution_database(solution_name: str):
    """
    Ensure a solution database exists and is configured.

    This would typically be called during solution creation/setup.
    """
    from django.db import connections

    db_name = get_solution_database_name(solution_name)

    # Check if database connection is configured
    if db_name not in connections.databases:
        # Configure the database connection dynamically
        base_config = settings.DATABASES['default'].copy()

        # Modify database name for solution
        if 'NAME' in base_config:
            base_config['NAME'] = f'djo_{solution_name}_db'

        # Register the new database connection
        connections.databases[db_name] = base_config

    return db_name

