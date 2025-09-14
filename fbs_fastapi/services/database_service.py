"""
FBS FastAPI Database Service

PRESERVES the sophisticated Django database management functionality.
Handles multi-database creation, routing, and management.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations and multi-database management"""

    def __init__(self, solution_name: str):
        self.solution_name = solution_name

    async def create_database(
        self,
        db_type: str,
        solution_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create database for solution.

        PRESERVED from Django database service.
        Supports both Django and Odoo database creation.
        """
        try:
            if db_type == 'django':
                return await self._create_django_database(solution_name, config)
            elif db_type == 'fbs':
                return await self._create_odoo_database(solution_name, config)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported database type: {db_type}'
                }

        except Exception as e:
            logger.error(f"Error creating {db_type} database: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'database_type': db_type
            }

    async def _create_django_database(
        self,
        solution_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create Django/PostgreSQL database for solution.

        PRESERVED from Django implementation.
        """
        try:
            # Generate database name
            db_name = f"fbs_{solution_name}_db"

            # Implement actual database creation
            # Connect to PostgreSQL and create the database
            try:
                import asyncpg
                from ..core.config import config

                # Connect to default PostgreSQL database to create new database
                conn = await asyncpg.connect(
                    host=getattr(config, 'database_host', 'localhost'),
                    port=getattr(config, 'database_port', 5432),
                    user=getattr(config, 'database_user', 'postgres'),
                    password=getattr(config, 'database_password', ''),
                    database='postgres'  # Connect to default database
                )

                # Create the new database
                await conn.execute(f'CREATE DATABASE {db_name}')
                await conn.close()

                logger.info(f"Created PostgreSQL database: {db_name}")

                return {
                    'success': True,
                    'database_name': db_name,
                    'database_type': 'postgresql',
                    'host': getattr(config, 'database_host', 'localhost'),
                    'port': getattr(config, 'database_port', 5432),
                    'message': f'Database {db_name} created successfully'
                }

            except asyncpg.exceptions.DuplicateDatabaseError:
                logger.warning(f"Database {db_name} already exists")
                return {
                    'success': True,
                    'database_name': db_name,
                    'message': f'Database {db_name} already exists'
                }
            except Exception as e:
                logger.error(f"Failed to create database {db_name}: {str(e)}")
                return {
                    'success': False,
                    'database_name': db_name,
                    'error': str(e),
                    'message': f'Failed to create database {db_name}'
                }

        except Exception as e:
            logger.error(f"Error creating Django database: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'database_type': 'django'
            }

    async def _create_odoo_database(
        self,
        solution_name: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create Odoo database for solution.

        PRESERVED from Django implementation.
        """
        try:
            # Generate database name
            db_name = f"fbs_{solution_name}_db"

            # Implement actual Odoo database creation
            # Connect to Odoo and create the database
            try:
                from ..services.odoo_service import OdooService
                odoo_service = OdooService(solution_name)

                # Create Odoo database
                create_result = await odoo_service.create_database(db_name, config or {})

                if create_result['success']:
                    logger.info(f"Created Odoo database: {db_name}")
                    return {
                        'success': True,
                        'database_name': db_name,
                        'database_type': 'odoo',
                        'odoo_url': getattr(odoo_service, 'base_url', 'http://localhost:8069'),
                        'message': f'Odoo database {db_name} created successfully'
                    }
                else:
                    return {
                        'success': False,
                        'database_name': db_name,
                        'error': create_result.get('error', 'Unknown error'),
                        'message': f'Failed to create Odoo database {db_name}'
                    }

            except Exception as e:
                logger.error(f"Failed to create Odoo database {db_name}: {str(e)}")
                return {
                    'success': False,
                    'database_name': db_name,
                    'error': str(e),
                    'message': f'Failed to create Odoo database {db_name}'
                }

        except Exception as e:
            logger.error(f"Error creating Odoo database: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'database_type': 'odoo'
            }

    async def get_database_names(self, solution_name: str) -> Dict[str, str]:
        """
        Get database names for solution.

        PRESERVED from Django implementation.
        """
        return {
            'django': f"fbs_{solution_name}_db",
            'odoo': f"fbs_{solution_name}_db"
        }

    async def validate_database_connection(
        self,
        db_name: str,
        db_type: str = 'django'
    ) -> Dict[str, Any]:
        """
        Validate database connection.

        PRESERVED from Django implementation.
        """
        try:
            # Implement actual connection validation
            try:
                if db_type == 'postgresql':
                    import asyncpg
                    from ..core.config import config

                    # Test PostgreSQL connection
                    conn = await asyncpg.connect(
                        host=getattr(config, 'database_host', 'localhost'),
                        port=getattr(config, 'database_port', 5432),
                        user=getattr(config, 'database_user', 'postgres'),
                        password=getattr(config, 'database_password', ''),
                        database=db_name
                    )

                    # Execute a simple test query
                    result = await conn.fetchval('SELECT 1')
                    await conn.close()

                    if result == 1:
                        logger.info(f"PostgreSQL connection to {db_name} validated successfully")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'status': 'connected',
                            'message': f'PostgreSQL connection to {db_name} validated successfully'
                        }
                    else:
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'status': 'error',
                            'message': f'PostgreSQL connection test failed for {db_name}'
                        }

                elif db_type == 'odoo':
                    # Test Odoo connection
                    from ..services.odoo_service import OdooService
                    odoo_service = OdooService(self.solution_name)
                    health_result = await odoo_service.health_check()

                    if health_result.get('status') == 'healthy':
                        logger.info(f"Odoo connection to {db_name} validated successfully")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'status': 'connected',
                            'message': f'Odoo connection to {db_name} validated successfully'
                        }
                    else:
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'status': 'error',
                            'message': f'Odoo connection test failed for {db_name}'
                        }

                else:
                    return {
                        'success': False,
                        'database': db_name,
                        'type': db_type,
                        'status': 'unsupported',
                        'message': f'Unsupported database type: {db_type}'
                    }

            except Exception as e:
                logger.error(f"Connection validation failed for {db_name}: {str(e)}")
                return {
                    'success': False,
                    'database': db_name,
                    'type': db_type,
                    'status': 'error',
                    'error': str(e),
                    'message': f'Connection validation failed for {db_name}'
                }

        except Exception as e:
            logger.error(f"Database connection validation failed: {str(e)}")
            return {
                'success': False,
                'database': db_name,
                'type': db_type,
                'status': 'disconnected',
                'error': str(e),
                'message': f'Failed to connect to {db_type} database {db_name}'
            }

    async def setup_database_schema(
        self,
        db_name: str,
        db_type: str = 'django',
        schema_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Setup database schema and initial data.

        PRESERVED from Django implementation.
        """
        try:
            logger.info(f"Setting up schema for {db_type} database: {db_name}")

            # Implement schema setup
            try:
                if db_type == 'postgresql':
                    # Run Alembic migrations for PostgreSQL
                    import subprocess
                    import os

                    # Change to the FastAPI directory
                    os.chdir('/home/fayvad/pwa_android/fbs/fbs_fastapi')

                    # Run Alembic upgrade
                    result = subprocess.run(
                        ['alembic', 'upgrade', 'head'],
                        capture_output=True,
                        text=True,
                        cwd='/home/fayvad/pwa_android/fbs/fbs_fastapi'
                    )

                    if result.returncode == 0:
                        logger.info(f"Schema migrations completed for PostgreSQL database {db_name}")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'schema_version': 'latest',
                            'message': f'Schema setup completed for PostgreSQL database {db_name}'
                        }
                    else:
                        logger.error(f"Schema migration failed: {result.stderr}")
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'error': result.stderr,
                            'message': f'Schema migration failed for {db_name}'
                        }

                elif db_type == 'odoo':
                    # Setup Odoo schema and modules
                    from ..services.odoo_service import OdooService
                    odoo_service = OdooService(self.solution_name)

                    # Install base modules
                    base_modules = ['base', 'web', 'mail']
                    installed_modules = []

                    for module in base_modules:
                        install_result = await odoo_service.install_module(module)
                        if install_result['success']:
                            installed_modules.append(module)

                    if installed_modules:
                        logger.info(f"Odoo schema setup completed for database {db_name}")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'installed_modules': installed_modules,
                            'schema_version': 'odoo_base',
                            'message': f'Odoo schema setup completed for database {db_name}'
                        }
                    else:
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'message': f'Odoo schema setup failed for database {db_name}'
                        }

                else:
                    return {
                        'success': False,
                        'database': db_name,
                        'type': db_type,
                        'message': f'Unsupported database type for schema setup: {db_type}'
                    }

            except Exception as e:
                logger.error(f"Schema setup failed for {db_name}: {str(e)}")
                return {
                    'success': False,
                    'database': db_name,
                    'type': db_type,
                    'error': str(e),
                    'message': f'Schema setup failed for {db_name}'
                }

        except Exception as e:
            logger.error(f"Schema setup failed: {str(e)}")
            return {
                'success': False,
                'database': db_name,
                'type': db_type,
                'error': str(e),
                'message': f'Schema setup failed for {db_type} database {db_name}'
            }

    async def backup_database(
        self,
        db_name: str,
        db_type: str = 'django',
        backup_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Backup database.

        PRESERVED from Django implementation.
        """
        try:
            logger.info(f"Backing up {db_type} database: {db_name}")

            # Implement database backup
            try:
                import subprocess
                import os
                from datetime import datetime

                # Generate backup filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = backup_path or f"{db_name}_backup_{timestamp}.sql"
                backup_path_full = os.path.join('/tmp', backup_file)

                if db_type == 'postgresql':
                    from ..core.config import config

                    # Create PostgreSQL backup using pg_dump
                    pg_dump_cmd = [
                        'pg_dump',
                        '--host', getattr(config, 'database_host', 'localhost'),
                        '--port', str(getattr(config, 'database_port', 5432)),
                        '--username', getattr(config, 'database_user', 'postgres'),
                        '--dbname', db_name,
                        '--file', backup_path_full,
                        '--format', 'custom',
                        '--compress', '9',
                        '--no-password'
                    ]

                    # Set password environment variable
                    env = os.environ.copy()
                    env['PGPASSWORD'] = getattr(config, 'database_password', '')

                    result = subprocess.run(
                        pg_dump_cmd,
                        capture_output=True,
                        text=True,
                        env=env
                    )

                    if result.returncode == 0:
                        logger.info(f"PostgreSQL backup completed for database {db_name}")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'backup_file': backup_file,
                            'backup_path': backup_path_full,
                            'size': os.path.getsize(backup_path_full) if os.path.exists(backup_path_full) else 0,
                            'message': f'PostgreSQL backup completed for database {db_name}'
                        }
                    else:
                        logger.error(f"PostgreSQL backup failed: {result.stderr}")
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'error': result.stderr,
                            'message': f'PostgreSQL backup failed for database {db_name}'
                        }

                elif db_type == 'odoo':
                    # For Odoo, we can backup the filestore and database
                    from ..services.odoo_service import OdooService
                    odoo_service = OdooService(self.solution_name)

                    # Backup Odoo database and filestore
                    backup_result = await odoo_service.backup_database(backup_path_full)

                    if backup_result['success']:
                        logger.info(f"Odoo backup completed for database {db_name}")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'backup_file': backup_file,
                            'backup_path': backup_path_full,
                            'message': f'Odoo backup completed for database {db_name}'
                        }
                    else:
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'error': backup_result.get('error', 'Unknown error'),
                            'message': f'Odoo backup failed for database {db_name}'
                        }

                else:
                    return {
                        'success': False,
                        'database': db_name,
                        'type': db_type,
                        'message': f'Unsupported database type for backup: {db_type}'
                    }

            except Exception as e:
                logger.error(f"Database backup failed for {db_name}: {str(e)}")
                return {
                    'success': False,
                    'database': db_name,
                    'type': db_type,
                    'error': str(e),
                    'message': f'Database backup failed for {db_name}'
                }

        except Exception as e:
            logger.error(f"Database backup failed: {str(e)}")
            return {
                'success': False,
                'database': db_name,
                'type': db_type,
                'error': str(e),
                'message': f'Backup failed for {db_type} database {db_name}'
            }

    async def restore_database(
        self,
        db_name: str,
        backup_file: str,
        db_type: str = 'django'
    ) -> Dict[str, Any]:
        """
        Restore database from backup.

        PRESERVED from Django implementation.
        """
        try:
            logger.info(f"Restoring {db_type} database: {db_name} from {backup_file}")

            # Implement database restore
            try:
                import subprocess
                import os

                if not os.path.exists(backup_file):
                    return {
                        'success': False,
                        'database': db_name,
                        'type': db_type,
                        'backup_file': backup_file,
                        'message': f'Backup file not found: {backup_file}'
                    }

                if db_type == 'postgresql':
                    from ..core.config import config

                    # Restore PostgreSQL database using pg_restore
                    pg_restore_cmd = [
                        'pg_restore',
                        '--host', getattr(config, 'database_host', 'localhost'),
                        '--port', str(getattr(config, 'database_port', 5432)),
                        '--username', getattr(config, 'database_user', 'postgres'),
                        '--dbname', db_name,
                        '--clean',  # Drop existing objects before recreating
                        '--if-exists',
                        '--no-password',
                        backup_file
                    ]

                    # Set password environment variable
                    env = os.environ.copy()
                    env['PGPASSWORD'] = getattr(config, 'database_password', '')

                    result = subprocess.run(
                        pg_restore_cmd,
                        capture_output=True,
                        text=True,
                        env=env
                    )

                    if result.returncode == 0:
                        logger.info(f"PostgreSQL restore completed for database {db_name}")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'backup_file': backup_file,
                            'message': f'PostgreSQL restore completed for database {db_name}'
                        }
                    else:
                        logger.error(f"PostgreSQL restore failed: {result.stderr}")
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'backup_file': backup_file,
                            'error': result.stderr,
                            'message': f'PostgreSQL restore failed for database {db_name}'
                        }

                elif db_type == 'odoo':
                    # For Odoo, restore database and filestore
                    from ..services.odoo_service import OdooService
                    odoo_service = OdooService(self.solution_name)

                    restore_result = await odoo_service.restore_database(backup_file)

                    if restore_result['success']:
                        logger.info(f"Odoo restore completed for database {db_name}")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'backup_file': backup_file,
                            'message': f'Odoo restore completed for database {db_name}'
                        }
                    else:
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'backup_file': backup_file,
                            'error': restore_result.get('error', 'Unknown error'),
                            'message': f'Odoo restore failed for database {db_name}'
                        }

                else:
                    return {
                        'success': False,
                        'database': db_name,
                        'type': db_type,
                        'backup_file': backup_file,
                        'message': f'Unsupported database type for restore: {db_type}'
                    }

            except Exception as e:
                logger.error(f"Database restore failed for {db_name}: {str(e)}")
                return {
                    'success': False,
                    'database': db_name,
                    'type': db_type,
                    'backup_file': backup_file,
                    'error': str(e),
                    'message': f'Database restore failed for {db_name}'
                }

        except Exception as e:
            logger.error(f"Database restore failed: {str(e)}")
            return {
                'success': False,
                'database': db_name,
                'type': db_type,
                'backup_file': backup_file,
                'error': str(e),
                'message': f'Restore failed for {db_type} database {db_name}'
            }

    async def get_database_stats(
        self,
        db_name: str,
        db_type: str = 'django'
    ) -> Dict[str, Any]:
        """
        Get database statistics and information.

        PRESERVED from Django implementation.
        """
        try:
            logger.info(f"Getting stats for {db_type} database: {db_name}")

            # Implement database statistics gathering
            try:
                if db_type == 'postgresql':
                    import asyncpg
                    from ..core.config import config

                    # Connect to PostgreSQL and gather statistics
                    conn = await asyncpg.connect(
                        host=getattr(config, 'database_host', 'localhost'),
                        port=getattr(config, 'database_port', 5432),
                        user=getattr(config, 'database_user', 'postgres'),
                        password=getattr(config, 'database_password', ''),
                        database=db_name
                    )

                    # Get database size
                    size_result = await conn.fetchval("""
                        SELECT pg_size_pretty(pg_database_size($1))
                    """, db_name)

                    # Get table count
                    table_count = await conn.fetchval("""
                        SELECT count(*) FROM information_schema.tables
                        WHERE table_schema = 'public'
                    """)

                    # Get active connections
                    connection_count = await conn.fetchval("""
                        SELECT count(*) FROM pg_stat_activity
                        WHERE datname = $1 AND state = 'active'
                    """, db_name)

                    # Get last vacuum time (as approximation for maintenance)
                    last_vacuum = await conn.fetchval("""
                        SELECT max(last_vacuum) FROM pg_stat_user_tables
                    """)

                    await conn.close()

                    return {
                        'success': True,
                        'database': db_name,
                        'type': db_type,
                        'stats': {
                            'size': size_result,
                            'tables': table_count,
                            'connections': connection_count,
                            'last_maintenance': last_vacuum.isoformat() if last_vacuum else None,
                            'collected_at': datetime.now().isoformat()
                        },
                        'message': f'Database statistics gathered for {db_name}'
                    }

                elif db_type == 'odoo':
                    # Get Odoo-specific statistics
                    from ..services.odoo_service import OdooService
                    odoo_service = OdooService(self.solution_name)

                    # Get basic Odoo statistics
                    stats_result = await odoo_service.get_database_stats()

                    if stats_result['success']:
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'stats': stats_result['stats'],
                            'message': f'Odoo database statistics gathered for {db_name}'
                        }
                    else:
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'error': stats_result.get('error', 'Failed to get Odoo stats'),
                            'message': f'Failed to gather Odoo statistics for {db_name}'
                        }

                else:
                    return {
                        'success': False,
                        'database': db_name,
                        'type': db_type,
                        'message': f'Unsupported database type for statistics: {db_type}'
                    }

            except Exception as e:
                logger.error(f"Database statistics gathering failed for {db_name}: {str(e)}")
                return {
                    'success': False,
                    'database': db_name,
                    'type': db_type,
                    'error': str(e),
                    'message': f'Database statistics gathering failed for {db_name}'
                }

        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {
                'success': False,
                'database': db_name,
                'type': db_type,
                'error': str(e),
                'message': f'Failed to get statistics for {db_type} database {db_name}'
            }

    async def migrate_database(
        self,
        db_name: str,
        target_version: Optional[str] = None,
        db_type: str = 'django'
    ) -> Dict[str, Any]:
        """
        Run database migrations.

        PRESERVED from Django implementation.
        """
        try:
            logger.info(f"Running migrations for {db_type} database: {db_name}")

            # Implement migration runner
            try:
                import subprocess
                import os

                if db_type == 'postgresql':
                    # Use Alembic for PostgreSQL migrations
                    os.chdir('/home/fayvad/pwa_android/fbs/fbs_fastapi')

                    if target_version == 'latest' or target_version is None:
                        # Run all pending migrations
                        result = subprocess.run(
                            ['alembic', 'upgrade', 'head'],
                            capture_output=True,
                            text=True,
                            cwd='/home/fayvad/pwa_android/fbs/fbs_fastapi'
                        )
                    else:
                        # Run migrations up to specific version
                        result = subprocess.run(
                            ['alembic', 'upgrade', target_version],
                            capture_output=True,
                            text=True,
                            cwd='/home/fayvad/pwa_android/fbs/fbs_fastapi'
                        )

                    if result.returncode == 0:
                        logger.info(f"Migrations completed for PostgreSQL database {db_name}")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'migrations_applied': [],  # Would need to parse output to get applied migrations
                            'target_version': target_version or 'head',
                            'message': f'Migrations completed for PostgreSQL database {db_name}'
                        }
                    else:
                        logger.error(f"Migration failed: {result.stderr}")
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'error': result.stderr,
                            'message': f'Migration failed for PostgreSQL database {db_name}'
                        }

                elif db_type == 'odoo':
                    # For Odoo, migrations are handled by module updates
                    from ..services.odoo_service import OdooService
                    odoo_service = OdooService(self.solution_name)

                    # Update all installed modules (which runs migrations)
                    update_result = await odoo_service.update_modules()

                    if update_result['success']:
                        logger.info(f"Odoo migrations completed for database {db_name}")
                        return {
                            'success': True,
                            'database': db_name,
                            'type': db_type,
                            'migrations_applied': update_result.get('updated_modules', []),
                            'target_version': target_version or 'latest',
                            'message': f'Odoo migrations completed for database {db_name}'
                        }
                    else:
                        return {
                            'success': False,
                            'database': db_name,
                            'type': db_type,
                            'error': update_result.get('error', 'Migration failed'),
                            'message': f'Odoo migration failed for database {db_name}'
                        }

                else:
                    return {
                        'success': False,
                        'database': db_name,
                        'type': db_type,
                        'message': f'Unsupported database type for migrations: {db_type}'
                    }

            except Exception as e:
                logger.error(f"Migration runner failed for {db_name}: {str(e)}")
                return {
                    'success': False,
                    'database': db_name,
                    'type': db_type,
                    'error': str(e),
                    'message': f'Migration runner failed for {db_name}'
                }

        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            return {
                'success': False,
                'database': db_name,
                'type': db_type,
                'error': str(e),
                'target_version': target_version,
                'message': f'Migration failed for {db_type} database {db_name}'
            }

    async def cleanup_database(
        self,
        db_name: str,
        cleanup_config: Optional[Dict[str, Any]] = None,
        db_type: str = 'django'
    ) -> Dict[str, Any]:
        """
        Cleanup database (remove old data, optimize, etc.).

        PRESERVED from Django implementation.
        """
        try:
            logger.info(f"Cleaning up {db_type} database: {db_name}")

            # Implement database cleanup
            try:
                import asyncpg
                from ..core.config import config

                cleanup_actions = []
                space_freed = 0

                if db_type == 'postgresql':
                    # Connect to PostgreSQL for cleanup operations
                    conn = await asyncpg.connect(
                        host=getattr(config, 'database_host', 'localhost'),
                        port=getattr(config, 'database_port', 5432),
                        user=getattr(config, 'database_user', 'postgres'),
                        password=getattr(config, 'database_password', ''),
                        database=db_name
                    )

                    # VACUUM to reclaim space
                    await conn.execute("VACUUM")
                    cleanup_actions.append("VACUUM completed")

                    # ANALYZE to update statistics
                    await conn.execute("ANALYZE")
                    cleanup_actions.append("ANALYZE completed")

                    # REINDEX system catalogs if needed
                    await conn.execute("REINDEX SYSTEM")
                    cleanup_actions.append("REINDEX completed")

                    # Clean up old WAL files (if running as superuser)
                    try:
                        await conn.execute("SELECT pg_walfile_name(pg_switch_wal())")
                        cleanup_actions.append("WAL file cleanup completed")
                    except:
                        cleanup_actions.append("WAL cleanup skipped (insufficient privileges)")

                    # Get space freed (approximate)
                    size_before = await conn.fetchval("SELECT pg_database_size($1)", db_name)
                    await conn.execute("VACUUM FULL")  # More aggressive cleanup
                    size_after = await conn.fetchval("SELECT pg_database_size($1)", db_name)
                    space_freed = size_before - size_after

                    await conn.close()

                    return {
                        'success': True,
                        'database': db_name,
                        'type': db_type,
                        'cleanup_actions': cleanup_actions,
                        'space_freed': f"{space_freed / (1024*1024):.2f} MB",
                        'message': f'PostgreSQL cleanup completed for database {db_name}'
                    }

                elif db_type == 'odoo':
                    # Odoo-specific cleanup
                    from ..services.odoo_service import OdooService
                    odoo_service = OdooService(self.solution_name)

                    # Clean up old attachments
                    cleanup_result = await odoo_service.cleanup_attachments()
                    if cleanup_result['success']:
                        cleanup_actions.append(f"Cleaned up {cleanup_result.get('attachments_removed', 0)} old attachments")
                        space_freed += cleanup_result.get('space_freed', 0)

                    # Clean up audit logs
                    audit_cleanup = await odoo_service.cleanup_audit_logs()
                    if audit_cleanup['success']:
                        cleanup_actions.append(f"Cleaned up {audit_cleanup.get('logs_removed', 0)} audit log entries")

                    # Clean up temporary files
                    temp_cleanup = await odoo_service.cleanup_temp_files()
                    if temp_cleanup['success']:
                        cleanup_actions.append(f"Cleaned up {temp_cleanup.get('files_removed', 0)} temporary files")
                        space_freed += temp_cleanup.get('space_freed', 0)

                    return {
                        'success': True,
                        'database': db_name,
                        'type': db_type,
                        'cleanup_actions': cleanup_actions,
                        'space_freed': f"{space_freed / (1024*1024):.2f} MB",
                        'message': f'Odoo cleanup completed for database {db_name}'
                    }

                else:
                    return {
                        'success': False,
                        'database': db_name,
                        'type': db_type,
                        'message': f'Unsupported database type for cleanup: {db_type}'
                    }

            except Exception as e:
                logger.error(f"Database cleanup failed for {db_name}: {str(e)}")
                return {
                    'success': False,
                    'database': db_name,
                    'type': db_type,
                    'error': str(e),
                    'message': f'Database cleanup failed for {db_name}'
                }

        except Exception as e:
            logger.error(f"Database cleanup failed: {str(e)}")
            return {
                'success': False,
                'database': db_name,
                'type': db_type,
                'error': str(e),
                'message': f'Cleanup failed for {db_type} database {db_name}'
            }
