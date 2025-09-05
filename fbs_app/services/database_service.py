"""
FBS App Database Service

Service for managing database operations in the new FBS architecture:
- fbs_{solution}_db: FBS (Odoo) database for data warehouse operations
- djo_{solution}_db: Django database for Django application operations
- fbs_system_db: FBS system database for FBS Django operations
"""

import os
import psycopg2
import logging
from typing import Dict, List, Optional, Tuple, Any
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from django.utils import timezone

logger = logging.getLogger('fbs_app')


class DatabaseService:
    """Service for managing database operations in the new FBS architecture"""
    
    def __init__(self, solution_name: str = None):
        """
        Initialize the database service
        
        Args:
            solution_name: Name of the solution (e.g., 'rental', 'mail', 'ecommerce')
        """
        self.solution_name = solution_name
        self.fbs_config = getattr(settings, 'FBS_APP', {})
        
        # Database naming patterns
        self.db_patterns = self.fbs_config.get('database_naming_patterns', {
            'fbs': 'fbs_{solution_name}_db',
            'django': 'djo_{solution_name}_db',
            'system': 'fbs_system_db'
        })
        
        # Base database configuration - prioritize environment variables
        self.base_db_config = {
            'host': os.environ.get('FBS_DB_HOST', 'localhost'),
            'port': os.environ.get('FBS_DB_PORT', '5432'),
            'user': os.environ.get('FBS_DB_USER', 'odoo'),
            'password': os.environ.get('FBS_DB_PASSWORD'),  # Required from environment
        }
        
        # Different user configurations for different operations
        self.user_configs = {
            'odoo': {
                'user': os.environ.get('FBS_DB_USER', 'odoo'),
                'password': os.environ.get('FBS_DB_PASSWORD', 'four@One2')
            },
            'django': {
                'user': os.environ.get('FBS_DJANGO_USER', 'fayvad'),
                'password': os.environ.get('FBS_DJANGO_PASSWORD', 'MeMiMo@0207')
            },
            'admin': {
                'user': os.environ.get('FBS_ADMIN_USER', 'postgres'),
                'password': os.environ.get('FBS_ADMIN_PASSWORD', 'MeMiMo@0207')
            }
        }
        
        # Override with Django settings if provided
        django_db_config = self.fbs_config.get('default_database_config', {})
        for key in ['host', 'port', 'user', 'password']:
            if django_db_config.get(key):
                self.base_db_config[key] = django_db_config[key]
        
        # Validate required configuration (only if we need to connect to databases)
        self._db_connection_required = True
    
    def _validate_db_connection(self):
        """Validate database connection configuration"""
        if not self.base_db_config['password']:
            raise ValueError(
                'Database password must be configured in FBS_APP.default_database_config or environment variables'
            )
    
    def _get_user_config(self, operation_type: str = 'odoo') -> Dict[str, str]:
        """
        Get user configuration for specific operation type
        
        Args:
            operation_type: Type of operation ('odoo', 'django', 'admin')
            
        Returns:
            Dict with user and password for the operation
        """
        if operation_type not in self.user_configs:
            operation_type = 'odoo'  # Default to odoo
        
        return {
            'host': self.base_db_config['host'],
            'port': self.base_db_config['port'],
            'user': self.user_configs[operation_type]['user'],
            'password': self.user_configs[operation_type]['password']
        }
    
    def get_database_names(self, solution_name):
        """Get all database names for a solution"""
        if not solution_name:
            return {'system': self.db_patterns['system']}
        
        return {
            'fbs': f"fbs_{solution_name}_db",
            'django': f"djo_{solution_name}_db",
            'system': self.db_patterns['system']
        }
    
    def get_database_name(self, database_type: str, solution_name: str = None) -> str:
        """
        Get database name for the specified database type and solution
        
        Args:
            database_type: Type of database ('fbs', 'django', 'system')
            solution_name: Name of the solution
            
        Returns:
            str: Database name
        """
        if database_type == 'system':
            return self.db_patterns['system']
        elif solution_name:
            if database_type == 'fbs':
                return f"fbs_{solution_name}_db"
            elif database_type == 'django':
                return f"djo_{solution_name}_db"
            else:
                raise ValueError(f"Invalid database type: {database_type}")
        else:
            return self.db_patterns['system']
    
    def get_database_config(self, database_type: str, solution_name: str = None) -> Dict:
        """
        Get database configuration for the specified database
        
        Args:
            database_type: Type of database ('fbs', 'django', 'system')
            solution_name: Name of the solution
            
        Returns:
            Dict: Database configuration
        """
        database_name = self.get_database_name(database_type, solution_name)
        
        config = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': database_name,
            'USER': self.base_db_config['user'],
            'PASSWORD': self.base_db_config['password'],
            'HOST': self.base_db_config['host'],
            'PORT': self.base_db_config['port'],
        }
        
        return config
    
    def create_database(self, database_type: str, solution_name: str = None) -> Dict[str, Any]:
        """
        Create a new database
        
        Args:
            database_type: Type of database ('fbs', 'django', 'system')
            solution_name: Name of the solution
            
        Returns:
            Dict: Result of database creation
        """
        try:
            # Validate database connection before proceeding
            self._validate_db_connection()
            
            database_name = self.get_database_name(database_type, solution_name)
            
            # Connect to PostgreSQL server using appropriate user based on database type
            if database_type == 'fbs':
                # Use odoo user for Odoo databases
                db_config = self._get_user_config('odoo')
            else:
                # Use fayvad user for Django databases
                db_config = self._get_user_config('django')
            
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database='postgres'  # Connect to default database
            )
            
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            exists = cursor.fetchone()
            
            if exists:
                return {
                    'success': False,
                    'error': f'Database {database_name} already exists'
                }
            
            # Create database
            cursor.execute(f'CREATE DATABASE "{database_name}"')
            
            cursor.close()
            conn.close()
            
            logger.info(f"Database {database_name} created successfully")
            
            return {
                'success': True,
                'database_name': database_name,
                'database_type': database_type,
                'solution_name': solution_name,
                'message': f'Database {database_name} created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def drop_database(self, database_type: str, solution_name: str = None) -> Dict[str, Any]:
        """
        Drop a database
        
        Args:
            database_type: Type of database ('fbs', 'django', 'system')
            solution_name: Name of the solution
            
        Returns:
            Dict: Result of database deletion
        """
        try:
            # Validate database connection before proceeding
            self._validate_db_connection()
            
            database_name = self.get_database_name(database_type, solution_name)
            
            # Connect to PostgreSQL server using appropriate user based on database type
            if database_type == 'fbs':
                # Use odoo user for Odoo databases
                db_config = self._get_user_config('odoo')
            else:
                # Use fayvad user for Django databases
                db_config = self._get_user_config('django')
            
            conn = psycopg2.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password'],
                database='postgres'  # Connect to default database
            )
            
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            exists = cursor.fetchone()
            
            if not exists:
                return {
                    'success': False,
                    'error': f'Database {database_name} does not exist'
                }
            
            # Drop database
            cursor.execute(f'DROP DATABASE "{database_name}"')
            
            cursor.close()
            conn.close()
            
            logger.info(f"Database {database_name} dropped successfully")
            
            return {
                'success': True,
                'database_name': database_name,
                'database_type': database_type,
                'solution_name': solution_name,
                'message': f'Database {database_name} dropped successfully'
            }
            
        except Exception as e:
            logger.error(f"Error dropping database: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_database_connection(self, database_type: str, solution_name: str = None) -> Dict[str, Any]:
        """
        Test connection to a database
        
        Args:
            database_type: Type of database ('fbs', 'django', 'system')
            solution_name: Name of the solution
            
        Returns:
            Dict: Connection test result
        """
        try:
            database_name = self.get_database_name(database_type, solution_name)
            
            # Try to connect to the database
            conn = psycopg2.connect(
                host=self.base_db_config['host'],
                port=self.base_db_config['port'],
                user=self.base_db_config['user'],
                password=self.base_db_config['password'],
                database=database_name
            )
            
            # Test connection with a simple query
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result and result[0] == 1:
                return {
                    'success': True,
                    'database_name': database_name,
                    'connection_status': 'connected',
                    'message': f'Successfully connected to {database_name}'
                }
            else:
                return {
                    'success': False,
                    'database_name': database_name,
                    'connection_status': 'failed',
                    'error': 'Connection test query failed'
                }
                
        except Exception as e:
            logger.error(f"Error testing database connection: {str(e)}")
            return {
                'success': False,
                'database_name': database_name if 'database_name' in locals() else 'unknown',
                'connection_status': 'failed',
                'error': str(e)
            }
    
    def get_database_info(self, database_type: str, solution_name: str = None) -> Dict[str, Any]:
        """
        Get information about a database
        
        Args:
            database_type: Type of database ('fbs', 'django', 'system')
            solution_name: Name of the solution
            
        Returns:
            Dict: Database information
        """
        try:
            database_name = self.get_database_name(database_type, solution_name)
            
            # Connect to the database
            conn = psycopg2.connect(
                host=self.base_db_config['host'],
                port=self.base_db_config['port'],
                user=self.base_db_config['user'],
                password=self.base_db_config['password'],
                database=database_name
            )
            
            cursor = conn.cursor()
            
            # Get database size
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(%s)) as size
            """, (database_name,))
            size_result = cursor.fetchone()
            database_size = size_result[0] if size_result else 'Unknown'
            
            # Get table count
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            table_count = cursor.fetchone()[0]
            
            # Get user count (for Odoo databases)
            user_count = 0
            if database_type == 'fbs':
                try:
                    cursor.execute("SELECT COUNT(*) FROM res_users")
                    user_count = cursor.fetchone()[0]
                except:
                    pass
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'database_name': database_name,
                'database_type': database_type,
                'solution_name': solution_name,
                'size': database_size,
                'table_count': table_count,
                'user_count': user_count,
                'connection_status': 'connected'
            }
            
        except Exception as e:
            logger.error(f"Error getting database info: {str(e)}")
            return {
                'success': False,
                'database_name': database_name if 'database_name' in locals() else 'unknown',
                'database_type': database_type,
                'solution_name': solution_name,
                'error': str(e)
            }
    
    def backup_database(self, database_type: str, solution_name: str = None, 
                       backup_path: str = None) -> Dict[str, Any]:
        """
        Create a backup of a database
        
        Args:
            database_type: Type of database ('fbs', 'django', 'system')
            solution_name: Name of the solution
            backup_path: Path to save the backup file
            
        Returns:
            Dict: Backup result
        """
        try:
            database_name = self.get_database_name(database_type, solution_name)
            
            if not backup_path:
                backup_path = f"/tmp/{database_name}_backup.sql"
            
            # Create backup using pg_dump
            import subprocess
            
            cmd = [
                'pg_dump',
                '-h', self.base_db_config['host'],
                '-p', str(self.base_db_config['port']),
                '-U', self.base_db_config['user'],
                '-d', database_name,
                '-f', backup_path
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.base_db_config['password']
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'database_name': database_name,
                    'backup_path': backup_path,
                    'backup_size': os.path.getsize(backup_path) if os.path.exists(backup_path) else 0,
                    'message': f'Database {database_name} backed up successfully to {backup_path}'
                }
            else:
                return {
                    'success': False,
                    'database_name': database_name,
                    'error': f'Backup failed: {result.stderr}'
                }
                
        except Exception as e:
            logger.error(f"Error backing up database: {str(e)}")
            return {
                'success': False,
                'database_name': database_name if 'database_name' in locals() else 'unknown',
                'error': str(e)
            }
    
    def restore_database(self, database_type: str, solution_name: str = None, 
                        backup_path: str = None) -> Dict[str, Any]:
        """
        Restore a database from backup
        
        Args:
            database_type: Type of database ('fbs', 'django', 'system')
            solution_name: Name of the solution
            backup_path: Path to the backup file
            
        Returns:
            Dict: Restore result
        """
        try:
            database_name = self.get_database_name(database_type, solution_name)
            
            if not backup_path or not os.path.exists(backup_path):
                return {
                    'success': False,
                    'error': f'Backup file not found: {backup_path}'
                }
            
            # Drop existing database if it exists
            drop_result = self.drop_database(database_type, solution_name)
            if not drop_result['success'] and 'already exists' not in drop_result.get('error', ''):
                return drop_result
            
            # Create new database
            create_result = self.create_database(database_type, solution_name)
            if not create_result['success']:
                return create_result
            
            # Restore from backup using psql
            import subprocess
            
            cmd = [
                'psql',
                '-h', self.base_db_config['host'],
                '-p', str(self.base_db_config['port']),
                '-U', self.base_db_config['user'],
                '-d', database_name,
                '-f', backup_path
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = self.base_db_config['password']
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'database_name': database_name,
                    'backup_path': backup_path,
                    'message': f'Database {database_name} restored successfully from {backup_path}'
                }
            else:
                return {
                    'success': False,
                    'database_name': database_name,
                    'error': f'Restore failed: {result.stderr}'
                }
                
        except Exception as e:
            logger.error(f"Error restoring database: {str(e)}")
            return {
                'success': False,
                'database_name': database_name if 'database_name' in locals() else 'unknown',
                'error': str(e)
            }
    
    def list_all_databases(self) -> Dict[str, Any]:
        """
        List all databases in the system
        
        Returns:
            Dict: List of databases
        """
        try:
            # Connect to PostgreSQL server
            conn = psycopg2.connect(
                host=self.base_db_config['host'],
                port=self.base_db_config['port'],
                user=self.base_db_config['user'],
                password=self.base_db_config['password'],
                database='postgres'  # Connect to default database
            )
            
            cursor = conn.cursor()
            
            # Get all databases
            cursor.execute("""
                SELECT datname, pg_size_pretty(pg_database_size(datname)) as size
                FROM pg_database 
                WHERE datistemplate = false
                ORDER BY pg_database_size(datname) DESC
            """)
            
            databases = []
            for row in cursor.fetchall():
                database_name = row[0]
                size = row[1]
                
                # Determine database type
                if database_name.startswith('fbs_') and database_name.endswith('_db'):
                    db_type = 'fbs'
                    solution_name = database_name[4:-3]  # Remove 'fbs_' and '_db'
                elif database_name.startswith('djo_') and database_name.endswith('_db'):
                    db_type = 'django'
                    solution_name = database_name[4:-3]  # Remove 'djo_' and '_db'
                elif database_name == 'fbs_system_db':
                    db_type = 'system'
                    solution_name = None
                else:
                    db_type = 'other'
                    solution_name = None
                
                databases.append({
                    'name': database_name,
                    'type': db_type,
                    'solution_name': solution_name,
                    'size': size
                })
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'databases': databases,
                'total_count': len(databases)
            }
            
        except Exception as e:
            logger.error(f"Error listing databases: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def create_fbs_tables(self, database_name: str = None, solution_name: str = None) -> Dict[str, Any]:
        """
        Create required FBS database tables for the solution
        
        Args:
            database_name: Name of the database (optional, auto-generated if not provided)
            solution_name: Name of the solution (optional, uses self.solution_name if not provided)
            
        Returns:
            Dict: Result of table creation operation
        """
        try:
            sol_name = solution_name or self.solution_name
            if not sol_name and not database_name:
                return {
                    'success': False,
                    'error': 'Solution name or database name must be specified',
                    'message': 'Please provide a solution name or database name'
                }
            
            # Get database configuration - use correct field names
            if database_name:
                # Use provided database name
                db_name = database_name
            else:
                # Generate database name from solution
                db_name = f"fbs_{sol_name}_db"
            
            db_config = self.get_database_config('fbs', sol_name)
            
            # Connect to the FBS database using correct config keys
            conn = psycopg2.connect(
                host=db_config['HOST'],
                port=db_config['PORT'],
                user=db_config['USER'],
                password=db_config['PASSWORD'],
                database=db_name
            )
            
            cursor = conn.cursor()
            
            # Create fbs_msme_analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fbs_msme_analytics (
                    id SERIAL PRIMARY KEY,
                    solution_name VARCHAR(100) NOT NULL,
                    business_id INTEGER NOT NULL,
                    metric_name VARCHAR(200) NOT NULL,
                    metric_value DECIMAL(15,2),
                    metric_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create fbs_reports table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fbs_reports (
                    id SERIAL PRIMARY KEY,
                    solution_name VARCHAR(100) NOT NULL,
                    report_name VARCHAR(200) NOT NULL,
                    report_type VARCHAR(100) NOT NULL,
                    report_data JSONB,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'active'
                )
            """)
            
            # Create fbs_compliance_rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fbs_compliance_rules (
                    id SERIAL PRIMARY KEY,
                    solution_name VARCHAR(100) NOT NULL,
                    rule_name VARCHAR(200) NOT NULL,
                    rule_type VARCHAR(100) NOT NULL,
                    rule_definition JSONB,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fbs_msme_analytics_solution_business 
                ON fbs_msme_analytics(solution_name, business_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fbs_reports_solution_type 
                ON fbs_reports(solution_name, report_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_fbs_compliance_rules_solution_type 
                ON fbs_compliance_rules(solution_name, rule_type)
            """)
            
            # Commit the changes
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'database_name': db_name,
                'tables_created': ['fbs_msme_analytics', 'fbs_reports', 'fbs_compliance_rules'],
                'message': f'FBS tables created successfully in {db_name}'
            }
            
        except Exception as e:
            logger.error(f"Error creating FBS tables: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create FBS tables'
            }
    
    def ensure_solution_databases(self, solution_name: str) -> Dict[str, Any]:
        """
        Ensure that the required databases exist for a solution.
        This method can be called by solutions to verify/create their databases.
        
        Args:
            solution_name: Name of the solution (e.g., 'rental', 'retail')
            
        Returns:
            Dict with database status and creation results
        """
        try:
            results = {}
            
            # Generate database names using FBS pattern
            django_db_name = f"djo_{solution_name}_db"
            odoo_db_name = f"fbs_{solution_name}_db"
            
            # Check Django database configuration
            django_status = self._check_django_database(django_db_name)
            results['django'] = django_status
            
            # Check Odoo database
            odoo_status = self._check_odoo_database(odoo_db_name)
            results['odoo'] = odoo_status
            
            # If Odoo database doesn't exist, provide guidance
            if not odoo_status.get('exists', False):
                results['odoo']['creation_guidance'] = {
                    'message': f'Odoo database "{odoo_db_name}" does not exist',
                    'action_required': 'Solution needs to create this database',
                    'sql_command': f'CREATE DATABASE "{odoo_db_name}";',
                    'postgres_command': f'createdb -U postgres "{odoo_db_name}"',
                    'docker_command': f'docker exec -it postgres_container createdb -U postgres "{odoo_db_name}"'
                }
            
            # If Django database not configured, provide guidance
            if not django_status.get('configured', False):
                results['django']['configuration_guidance'] = {
                    'message': f'Django database "{django_db_name}" not configured',
                    'action_required': 'Solution needs to add this database to Django settings',
                    'example_config': {
                        'ENGINE': 'django.db.backends.postgresql',
                        'NAME': django_db_name,
                        'USER': 'your_db_user',
                        'PASSWORD': 'your_db_password',
                        'HOST': 'localhost',
                        'PORT': '5432'
                    }
                }
            
            return {
                'success': True,
                'message': f'Database verification completed for solution "{solution_name}"',
                'solution_name': solution_name,
                'database_names': {
                    'django': django_db_name,
                    'odoo': odoo_db_name
                },
                'results': results,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to verify solution databases: {str(e)}',
                'message': 'Database verification failed',
                'solution_name': solution_name
            }
    
    def _check_django_database(self, db_name: str) -> Dict[str, Any]:
        """Check if Django database is configured"""
        try:
            from django.conf import settings
            
            if db_name in settings.DATABASES:
                return {
                    'name': db_name,
                    'exists': True,
                    'configured': True,
                    'status': 'ready'
                }
            else:
                return {
                    'name': db_name,
                    'exists': False,
                    'configured': False,
                    'status': 'not_configured'
                }
                
        except Exception as e:
            return {
                'name': db_name,
                'exists': False,
                'configured': False,
                'status': 'error',
                'error': str(e)
            }
    
    def _check_odoo_database(self, db_name: str) -> Dict[str, Any]:
        """Check if Odoo database exists and is accessible"""
        try:
            # Try to connect to the database
            import psycopg2
            from django.conf import settings
            
            # Get database connection details from Django settings
            db_config = settings.DATABASES.get('default', {})
            
            connection_params = {
                'host': db_config.get('HOST', 'localhost'),
                'port': db_config.get('PORT', '5432'),
                'database': db_name,
                'user': db_config.get('USER', 'postgres'),
                'password': db_config.get('PASSWORD', ''),
            }
            
            # Try to connect
            conn = psycopg2.connect(**connection_params)
            conn.close()
            
            return {
                'name': db_name,
                'exists': True,
                'accessible': True,
                'status': 'ready'
            }
            
        except psycopg2.OperationalError as e:
            if "does not exist" in str(e):
                return {
                    'name': db_name,
                    'exists': False,
                    'accessible': False,
                    'status': 'not_exists',
                    'error': str(e)
                }
            else:
                return {
                    'name': db_name,
                    'exists': True,
                    'accessible': False,
                    'status': 'connection_failed',
                    'error': str(e)
                }
        except Exception as e:
            return {
                'name': db_name,
                'exists': False,
                'accessible': False,
                'status': 'error',
                'error': str(e)
            }
    
    def create_odoo_schema(self, solution_name: str, database_name: str = None) -> Dict[str, Any]:
        """
        Create Odoo-specific schema and tables in the solution's database.
        This can be called by solutions after they create their databases.
        
        Args:
            solution_name: Name of the solution
            database_name: Optional database name override
            
        Returns:
            Dict with schema creation results
        """
        if database_name is None:
            database_name = f"fbs_{solution_name}_db"
        
        try:
            # Create FBS-specific tables
            fbs_tables_result = self.create_fbs_tables(database_name)
            
            # Create Odoo-specific tables if needed
            odoo_tables_result = self._create_odoo_tables(database_name)
            
            return {
                'success': True,
                'message': f'Odoo schema created for solution "{solution_name}"',
                'database': database_name,
                'fbs_tables': fbs_tables_result,
                'odoo_tables': odoo_tables_result,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create Odoo schema: {str(e)}',
                'message': 'Schema creation failed',
                'database': database_name
            }
    
    def _create_odoo_tables(self, database_name: str) -> Dict[str, Any]:
        """Create Odoo-specific tables in the database"""
        try:
            # Note: Odoo creates its own tables during database initialization
            # This method is kept for compatibility but Odoo handles table creation
            logger.info(f"Odoo tables are created automatically during database initialization for {database_name}")
            return {
                'status': 'skipped',
                'message': 'Odoo tables are created automatically during database initialization',
                'database': database_name
            }
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'database': database_name
            }
    
    def create_odoo_database(self, solution_name: str, modules: List[str] = None) -> Dict[str, Any]:
        """
        Create and initialize an Odoo database using odoo-bin
        
        Args:
            solution_name: Name of the solution
            modules: List of modules to install during initialization
            
        Returns:
            Dict: Result of Odoo database creation
        """
        try:
            database_name = f"fbs_{solution_name}_db"
            
            # Default modules for basic Odoo functionality
            if modules is None:
                modules = ['base', 'web']
            
            # Check if database already exists
            if self._check_odoo_database_exists(database_name):
                return {
                    'success': False,
                    'error': f'Odoo database {database_name} already exists',
                    'database_name': database_name
                }
            
            # Prepare odoo-bin command
            odoo_bin_path = '/opt/odoo/odoo/odoo-bin'
            venv_python = '/opt/odoo/venv/bin/python'
            
            # Build command with proper arguments
            cmd = [
                venv_python,
                odoo_bin_path,
                '--database', database_name,
                '--init', ','.join(modules),
                '--stop-after-init',
                '--no-http',
                '--log-level', 'info'
            ]
            
            # Set environment variables for odoo user
            env = os.environ.copy()
            env['PATH'] = f"/opt/odoo/venv/bin:{env.get('PATH', '')}"
            
            # Run odoo-bin command
            import subprocess
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Odoo database {database_name} created successfully")
                
                # Change admin password from default to expected password
                password_result = self._change_admin_password(database_name)
                if password_result.get('success'):
                    logger.info(f"Admin password changed successfully in {database_name}")
                else:
                    logger.warning(f"Admin password change failed: {password_result.get('error')}")
                
                return {
                    'success': True,
                    'database_name': database_name,
                    'modules_installed': modules,
                    'message': f'Odoo database {database_name} created and initialized successfully',
                    'password_changed': password_result.get('success', False)
                }
            else:
                logger.error(f"Odoo database creation failed: {result.stderr}")
                return {
                    'success': False,
                    'error': f'Odoo database creation failed: {result.stderr}',
                    'database_name': database_name,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"Odoo database creation timed out for {database_name}")
            return {
                'success': False,
                'error': 'Odoo database creation timed out',
                'database_name': database_name
            }
        except Exception as e:
            logger.error(f"Error creating Odoo database: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'database_name': database_name if 'database_name' in locals() else 'unknown'
            }
    
    def _check_odoo_database_exists(self, database_name: str) -> bool:
        """Check if Odoo database exists"""
        try:
            # Use odoo user to check database existence
            odoo_config = self._get_user_config('odoo')
            conn = psycopg2.connect(
                host=odoo_config['host'],
                port=odoo_config['port'],
                user=odoo_config['user'],
                password=odoo_config['password'],
                database='postgres'  # Connect to default database
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            exists = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return bool(exists)
            
        except Exception as e:
            logger.error(f"Error checking Odoo database existence: {str(e)}")
            return False
    
    def _change_admin_password(self, database_name: str) -> Dict[str, Any]:
        """Change admin user password from default to expected password"""
        try:
            # Use odoo user to connect to the newly created database
            odoo_config = self._get_user_config('odoo')
            conn = psycopg2.connect(
                host=odoo_config['host'],
                port=odoo_config['port'],
                user=odoo_config['user'],
                password=odoo_config['password'],
                database=database_name
            )
            
            cursor = conn.cursor()
            
            # Update admin user password
            cursor.execute(
                "UPDATE res_users SET password = %s WHERE login = 'admin'",
                ('MeMiMo@0207',)
            )
            
            if cursor.rowcount > 0:
                conn.commit()
                cursor.close()
                conn.close()
                
                logger.info(f"Admin password updated successfully in {database_name}")
                return {
                    'success': True,
                    'message': f'Admin password changed in {database_name}'
                }
            else:
                cursor.close()
                conn.close()
                
                logger.warning(f"No admin user found to update in {database_name}")
                return {
                    'success': False,
                    'error': 'No admin user found to update'
                }
                
        except Exception as e:
            logger.error(f"Error changing admin password: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def install_odoo_modules(self, solution_name: str, modules: List[str], 
                            database_name: str = None) -> Dict[str, Any]:
        """
        Install additional Odoo modules in an existing database
        
        Args:
            solution_name: Name of the solution
            modules: List of modules to install
            database_name: Optional database name override
            
        Returns:
            Dict: Result of module installation
        """
        try:
            if database_name is None:
                database_name = f"fbs_{solution_name}_db"
            
            # Check if database exists
            if not self._check_odoo_database_exists(database_name):
                return {
                    'success': False,
                    'error': f'Odoo database {database_name} does not exist',
                    'database_name': database_name
                }
            
            # Prepare odoo-bin command for module installation
            odoo_bin_path = '/opt/odoo/odoo/odoo-bin'
            venv_python = '/opt/odoo/venv/bin/python'
            
            # Build command for module installation
            cmd = [
                venv_python,
                odoo_bin_path,
                '--database', database_name,
                '--init', ','.join(modules),
                '--stop-after-init',
                '--no-http',
                '--log-level', 'info'
            ]
            
            # Set environment variables for odoo user
            env = os.environ.copy()
            env['PATH'] = f"/opt/odoo/venv/bin:{env.get('PATH', '')}"
            
            # Run odoo-bin command
            import subprocess
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Modules {modules} installed successfully in {database_name}")
                return {
                    'success': True,
                    'database_name': database_name,
                    'modules_installed': modules,
                    'message': f'Modules {modules} installed successfully in {database_name}'
                }
            else:
                logger.error(f"Module installation failed: {result.stderr}")
                return {
                    'success': False,
                    'error': f'Module installation failed: {result.stderr}',
                    'database_name': database_name,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"Module installation timed out for {database_name}")
            return {
                'success': False,
                'error': 'Module installation timed out',
                'database_name': database_name
            }
        except Exception as e:
            logger.error(f"Error installing modules: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'database_name': database_name if 'database_name' in locals() else 'unknown'
            }
    
    def get_available_odoo_modules(self) -> Dict[str, Any]:
        """
        Get list of available Odoo modules that can be installed
        
        Returns:
            Dict: Available modules information
        """
        try:
            # This would typically query Odoo's module registry
            # For now, return a curated list of common modules
            available_modules = {
                'core': ['base', 'web', 'mail', 'calendar', 'contacts'],
                'sales': ['sale', 'sale_management', 'crm', 'point_of_sale'],
                'inventory': ['stock', 'purchase', 'mrp', 'quality'],
                'finance': ['account', 'accounting', 'payment', 'expense'],
                'hr': ['hr', 'hr_attendance', 'hr_expense', 'hr_payroll'],
                'manufacturing': ['mrp', 'mrp_workorder', 'mrp_plm'],
                'ecommerce': ['website', 'website_sale', 'website_blog'],
                'project': ['project', 'project_forecast', 'project_timesheet'],
                'helpdesk': ['helpdesk', 'knowledge', 'survey'],
                'custom': ['custom_module_1', 'custom_module_2']  # Placeholder for custom modules
            }
            
            return {
                'success': True,
                'available_modules': available_modules,
                'message': 'Available Odoo modules retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error getting available modules: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve available modules'
            }
