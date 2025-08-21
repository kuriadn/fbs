"""
FBS App Database Routing Middleware

Middleware to handle database routing based on headers, tokens, or request context.
"""

from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import logging

logger = logging.getLogger('fbs_app')


class DatabaseRoutingMiddleware(MiddlewareMixin):
    """Middleware to handle database routing based on headers or tokens"""
    
    def process_request(self, request):
        """Process incoming request to determine database routing"""
        # PRIORITY 1: Use handshake authentication context (highest priority)
        if hasattr(request, 'handshake') and hasattr(request, 'database_name') and request.database_name:
            database_name = request.database_name
            # Extract solution name from database name if it follows the pattern fbs_{solution}_db
            if database_name.startswith('fbs_') and database_name.endswith('_db'):
                solution_name = database_name[4:-3]  # Remove 'fbs_' prefix and '_db' suffix
                database_type = 'fbs'
            else:
                # For non-standard database names, try to infer solution
                solution_name = self._infer_solution_from_database(database_name)
                database_type = 'fbs'
            
            logger.debug(f"Handshake authentication routing: solution={solution_name}, type={database_type}, db={database_name}")
            
        # PRIORITY 2: Check for handshake headers directly (for pre-authentication routing)
        elif request.META.get('HTTP_X_HANDSHAKE_TOKEN') and request.META.get('HTTP_X_HANDSHAKE_SECRET'):
            # Extract database from handshake headers or query parameters
            database_name = request.GET.get('db') or request.META.get('HTTP_X_DATABASE')
            
            if not database_name:
                # Try to infer from URL path or default to system database
                if '/fbs/' in request.path:
                    # This is an FBS app endpoint, try to get database from query params
                    database_name = request.GET.get('db', 'fbs_system_db')
                else:
                    database_name = 'fbs_system_db'
            
            # Extract solution name from database name
            if database_name.startswith('fbs_') and database_name.endswith('_db'):
                solution_name = database_name[4:-3]
                database_type = 'fbs'
            else:
                solution_name = self._infer_solution_from_database(database_name)
                database_type = 'fbs'
                
            logger.debug(f"Handshake header routing: solution={solution_name}, type={database_type}, db={database_name}")
            
        # PRIORITY 3: Use explicit headers
        elif request.META.get('HTTP_X_SOLUTION') or request.META.get('HTTP_X_DATABASE_TYPE'):
            solution_name = request.META.get('HTTP_X_SOLUTION')
            database_type = request.META.get('HTTP_X_DATABASE_TYPE', 'fbs')
            
            if solution_name:
                if database_type == 'fbs':
                    database_name = f"fbs_{solution_name}_db"
                elif database_type == 'django':
                    database_name = f"djo_{solution_name}_db"
                elif database_type == 'system':
                    database_name = "fbs_system_db"
                else:
                    database_name = f"fbs_{solution_name}_db"  # Default to FBS
            else:
                database_name = "fbs_system_db"  # Default to system database
                
            logger.debug(f"Header-based routing: solution={solution_name}, type={database_type}, db={database_name}")
            
        # PRIORITY 4: Check query parameters for database specification
        elif request.GET.get('db'):
            database_name = request.GET.get('db')
            if database_name.startswith('fbs_') and database_name.endswith('_db'):
                solution_name = database_name[4:-3]
                database_type = 'fbs'
            else:
                solution_name = self._infer_solution_from_database(database_name)
                database_type = 'fbs'
                
            logger.debug(f"Query parameter routing: solution={solution_name}, type={database_type}, db={database_name}")
            
        # PRIORITY 5: Check if this is a solution operation that needs a solution database
        elif self._is_solution_operation(request.path):
            # For solution operations, we MUST have a solution database, not the system database
            # Check if we can infer from previous requests or use a default solution
            database_name = self._get_default_solution_database()
            if database_name:
                solution_name = database_name[4:-3] if database_name.startswith('fbs_') and database_name.endswith('_db') else None
                database_type = 'fbs'
                logger.debug(f"Solution operation routing: solution={solution_name}, type={database_type}, db={database_name}")
            else:
                # No solution database available, this will cause an error
                solution_name = None
                database_type = 'fbs'
                database_name = None
                logger.warning(f"Solution operation detected but no solution database available for path: {request.path}")
            
        # PRIORITY 6: Default fallback (ONLY for system operations, NEVER for solution operations)
        else:
            # Check if this is a solution-specific operation
            if self._is_solution_operation(request.path):
                # This is a solution operation, we MUST use a solution database
                # Get solution name from available solutions
                available_solutions = ['rental', 'retail', 'manufacturing', 'ecommerce']
                solution_name = available_solutions[0] if available_solutions else 'rental'  # Default to rental
                
                # Use Django database for solution operations, NOT FBS database
                django_database = self._get_django_database_for_solution(solution_name)
                database_name = django_database
                database_type = 'django'  # Use Django database for solution operations
                logger.debug(f"Solution operation routing: solution={solution_name}, type={database_type}, db={database_name}")
            else:
                # This is truly a system operation (FBS core functionality)
                solution_name = None
                database_type = 'system'
                database_name = "fbs_system_db"  # ONLY for FBS system operations
                logger.debug(f"System operation routing: solution={solution_name}, type={database_type}, db={database_name}")
        
        # CRITICAL: Never allow solution operations to use system database
        if self._is_solution_operation(request.path) and database_name == 'fbs_system_db':
            logger.error(f"CRITICAL: Solution operation would route to system database! This is a security risk!")
            # Force routing to solution Django database
            fbs_database = self._get_default_solution_database() or 'fbs_rental_db'
            solution_name = fbs_database[4:-3] if fbs_database.startswith('fbs_') and fbs_database.endswith('_db') else 'rental'
            django_database = self._get_django_database_for_solution(solution_name)
            database_name = django_database
            database_type = 'django'
            logger.warning(f"FORCED routing to solution Django database: {database_name}")
        
        # Store database information in request for later use
        request.solution_name = solution_name
        request.database_type = database_type
        request.database_name = database_name
        
        # Enhanced logging for database routing decisions
        if database_type == 'system':
            logger.info(f"🔒 SYSTEM OPERATION: Routed to {database_name} (FBS core operations only)")
        elif database_type == 'django':
            logger.info(f"🏢 SOLUTION DJANGO: Routed to {database_name} (solution-specific Django operations)")
        elif database_type == 'fbs':
            logger.info(f"📊 SOLUTION ODOO: Routed to {database_name} (solution-specific Odoo operations)")
        
        logger.debug(f"Final database routing: solution={solution_name}, type={database_type}, db={database_name}")
        
        return None
    
    def _is_solution_operation(self, path):
        """Check if the request path is for a solution-specific operation"""
        solution_paths = [
            '/fbs/',  # FBS App operations (solution-specific)
            '/fbs/auth/',  # FBS App authentication operations
            '/fbs/health/',  # FBS App health operations
            '/fbs/admin/',  # FBS App admin operations
            '/fbs/dashboard/',  # FBS App dashboard operations
        ]
        return any(solution_path in path for solution_path in solution_paths)
    
    def _get_default_solution_database(self):
        """Get a default solution database for solution operations"""
        # Try to find an available solution database from settings
        fbs_config = getattr(settings, 'FBS_APP', {})
        default_solutions = fbs_config.get('default_solutions', ['fbs_rental_db'])
        
        # Return the first available one
        return default_solutions[0] if default_solutions else None
    
    def _get_django_database_for_solution(self, solution_name):
        """Get the Django database name for a solution"""
        if not solution_name:
            return None
        return f"djo_{solution_name}_db"
    
    def _get_fbs_database_for_solution(self, solution_name):
        """Get the FBS database name for a solution"""
        if not solution_name:
            return None
        return f"fbs_{solution_name}_db"
    
    def _get_all_database_names_for_solution(self, solution_name):
        """Get all database names for a solution"""
        if not solution_name:
            return {'system': 'fbs_system_db'}
        
        return {
            'fbs': f"fbs_{solution_name}_db",
            'django': f"djo_{solution_name}_db",
            'system': 'fbs_system_db'
        }
    
    def _infer_solution_from_database(self, database_name):
        """Infer solution name from database name"""
        # Common patterns
        if 'rental' in database_name.lower():
            return 'rental'
        elif 'retail' in database_name.lower():
            return 'retail'
        elif 'manufacturing' in database_name.lower():
            return 'manufacturing'
        elif 'ecommerce' in database_name.lower():
            return 'ecommerce'
        elif 'inventory' in database_name.lower():
            return 'inventory'
        elif 'system' in database_name.lower():
            return 'system'
        else:
            # Try to extract from fbs_{solution}_db pattern
            if database_name.startswith('fbs_') and database_name.endswith('_db'):
                return database_name[4:-3]
            return None
