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
        
        # Base database configuration
        self.base_db_config = self.fbs_config.get('default_database_config', {
            'host': 'localhost',
            'port': '5432',
            'user': 'odoo',
            'password': None  # Will be set from environment or settings
        })
        
        # Validate required configuration
        if not self.base_db_config['password']:
            raise ValueError(
                'Database password must be configured in FBS_APP.default_database_config or environment variables'
            )
    
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
            database_name = self.get_database_name(database_type, solution_name)
            
            # Connect to PostgreSQL server
            conn = psycopg2.connect(
                host=self.base_db_config['host'],
                port=self.base_db_config['port'],
                user=self.base_db_config['user'],
                password=self.base_db_config['password'],
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
            database_name = self.get_database_name(database_type, solution_name)
            
            # Connect to PostgreSQL server
            conn = psycopg2.connect(
                host=self.base_db_config['host'],
                port=self.base_db_config['port'],
                user=self.base_db_config['user'],
                password=self.base_db_config['password'],
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
