#!/usr/bin/env python3
"""
Odoo Installer Service for FBS
Simple database creation and module installation
"""

import logging
import xmlrpc.client
import psycopg2
from typing import Dict, List, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

class OdooInstallerService:
    """Service to create solution databases and install modules"""
    
    def __init__(self):
        self.odoo_url = settings.ODOO_CONFIG['BASE_URL']
        self.odoo_db = settings.ODOO_CONFIG['DATABASE']  # Reference database (fayvad)
        self.odoo_user = settings.ODOO_CONFIG['USERNAME']
        self.odoo_password = settings.ODOO_CONFIG['PASSWORD']
        self.uid = None
        self.models = None
        
    def create_solution_database(self, solution_name: str, selected_modules: List[str] = None) -> Dict[str, Any]:
        """Create a solution database with selected modules"""
        try:
            db_name = f"fbs_{solution_name}_db"
            
            # Check if database exists
            if self._database_exists(db_name):
                logger.info(f"Database {db_name} already exists")
                return {
                    'status': 'success',
                    'database': db_name,
                    'message': f'Database {db_name} already exists'
                }
            
            # Create database
            success = self._create_database(db_name)
            if success:
                # Install selected modules if provided
                if selected_modules:
                    install_result = self._install_selected_modules(db_name, selected_modules)
                    return {
                        'status': 'success',
                        'database': db_name,
                        'message': f'Database {db_name} created with {len(selected_modules)} modules',
                        'modules_installed': install_result.get('modules_installed', [])
                    }
                else:
                    return {
                        'status': 'success',
                        'database': db_name,
                        'message': f'Database {db_name} created successfully'
                    }
            else:
                return {
                    'status': 'error',
                    'message': f'Failed to create database {db_name}'
                }
                
        except Exception as e:
            logger.error(f"Error creating solution database: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _install_selected_modules(self, db_name: str, selected_modules: List[str]) -> Dict[str, Any]:
        """Install selected modules in the solution database"""
        try:
            # Connect to solution database
            if not self._connect_to_solution_db(db_name):
                return {'status': 'error', 'message': f'Failed to connect to {db_name}'}
            
            results = {
                'status': 'success',
                'modules_installed': [],
                'modules_failed': [],
                'details': {}
            }
            
            # First, ensure base modules are installed
            base_modules = ['base', 'web', 'mail', 'contacts']
            logger.info("Installing base modules first...")
            
            for base_module in base_modules:
                try:
                    module_ids = self.models.execute_kw(
                        db_name, self.uid, 'admin',
                        'ir.module.module', 'search',
                        [[('name', '=', base_module)]]
                    )
                    
                    if module_ids:
                        module_info = self.models.execute_kw(
                            db_name, self.uid, 'admin',
                            'ir.module.module', 'read',
                            [module_ids[0]], {'fields': ['name', 'state']}
                        )[0]
                        
                        if module_info['state'] != 'installed':
                            logger.info(f"Installing base module {base_module}")
                            self.models.execute_kw(
                                db_name, self.uid, 'admin',
                                'ir.module.module', 'button_immediate_install',
                                [module_ids[0]]
                            )
                            results['modules_installed'].append(base_module)
                        else:
                            logger.info(f"Base module {base_module} already installed")
                            results['modules_installed'].append(base_module)
                            
                except Exception as e:
                    logger.error(f"Error installing base module {base_module}: {str(e)}")
                    results['modules_failed'].append(base_module)
            
            # Now install selected modules
            logger.info("Installing selected modules...")
            for module_name in selected_modules:
                # Skip base modules that were already installed
                if module_name in base_modules:
                    continue
                    
                try:
                    # Check if module exists
                    module_ids = self.models.execute_kw(
                        db_name, self.uid, 'admin',
                        'ir.module.module', 'search',
                        [[('name', '=', module_name)]]
                    )
                    
                    if not module_ids:
                        logger.warning(f"Module {module_name} not found")
                        results['modules_failed'].append(module_name)
                        continue
                    
                    # Check if already installed
                    module_info = self.models.execute_kw(
                        db_name, self.uid, 'admin',
                        'ir.module.module', 'read',
                        [module_ids[0]], {'fields': ['name', 'state']}
                    )[0]
                    
                    if module_info['state'] == 'installed':
                        logger.info(f"Module {module_name} already installed")
                        results['modules_installed'].append(module_name)
                        continue
                    
                    # Install module
                    logger.info(f"Installing module {module_name}")
                    result = self.models.execute_kw(
                        db_name, self.uid, 'admin',
                        'ir.module.module', 'button_immediate_install',
                        [module_ids[0]]
                    )
                    
                    if result:
                        results['modules_installed'].append(module_name)
                        logger.info(f"Successfully installed {module_name}")
                    else:
                        results['modules_failed'].append(module_name)
                        logger.error(f"Failed to install {module_name}")
                        
                except Exception as e:
                    logger.error(f"Error installing module {module_name}: {str(e)}")
                    results['modules_failed'].append(module_name)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in _install_selected_modules: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _database_exists(self, db_name: str) -> bool:
        """Check if database exists"""
        try:
            db_config = settings.FBS_CONFIG['default_database_config']
            
            conn = psycopg2.connect(
                database='postgres',
                user=db_config['user'],
                password=db_config['password'],
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', '5432')
            )
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
                exists = cursor.fetchone()
                conn.close()
                return exists is not None
                
        except Exception as e:
            logger.error(f"Error checking database existence: {str(e)}")
            return False
    
    def _create_database(self, db_name: str) -> bool:
        """Create a new Odoo database by duplicating the reference database"""
        try:
            # Duplicate the reference database (fayvad) which has Odoo's complete schema
            db_config = settings.FBS_CONFIG['default_database_config']
            
            # Step 1: Dump the reference database
            import subprocess
            import os
            
            dump_file = f"/tmp/{self.odoo_db}_dump.sql"
            dump_cmd = [
                'pg_dump',
                f'--host={db_config.get("host", "localhost")}',
                f'--port={db_config.get("port", "5432")}',
                f'--username={db_config["user"]}',
                f'--dbname={self.odoo_db}',
                f'--file={dump_file}',
                '--no-password'
            ]
            
            # Set password environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = db_config['password']
            
            logger.info(f"Dumping reference database {self.odoo_db}...")
            result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to dump database: {result.stderr}")
                return False
            
            # Step 2: Create new database
            create_cmd = [
                'createdb',
                f'--host={db_config.get("host", "localhost")}',
                f'--port={db_config.get("port", "5432")}',
                f'--username={db_config["user"]}',
                '--no-password',
                db_name
            ]
            
            logger.info(f"Creating new database {db_name}...")
            result = subprocess.run(create_cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to create database: {result.stderr}")
                return False
            
            # Step 3: Restore the dump to new database
            restore_cmd = [
                'psql',
                f'--host={db_config.get("host", "localhost")}',
                f'--port={db_config.get("port", "5432")}',
                f'--username={db_config["user"]}',
                f'--dbname={db_name}',
                f'--file={dump_file}',
                '--no-password'
            ]
            
            logger.info(f"Restoring data to {db_name}...")
            result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Failed to restore database: {result.stderr}")
                return False
            
            # Clean up dump file
            try:
                os.remove(dump_file)
            except:
                pass
            
            logger.info(f"Successfully created {db_name} by duplicating {self.odoo_db}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database: {str(e)}")
            return False
    
    def _create_empty_database(self, db_name: str) -> bool:
        """Create an empty database as fallback"""
        try:
            db_config = settings.FBS_CONFIG['default_database_config']
            
            conn = psycopg2.connect(
                database='postgres',
                user=db_config['user'],
                password=db_config['password'],
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', '5432')
            )
            
            conn.autocommit = True
            with conn.cursor() as cursor:
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                logger.info(f"Created empty database: {db_name}")
            
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating empty database: {str(e)}")
            return False
    
    def install_discovered_features(self, solution_db: str, discoveries: Dict[str, Any]) -> Dict[str, Any]:
        """Install discovered features in solution database"""
        try:
            installation_results = {
                'status': 'success',
                'database': solution_db,
                'modules_installed': [],
                'models_available': [],
                'workflows_available': [],
                'bi_features_available': [],
                'details': {}
            }
            
            # Connect to solution database
            if not self._connect_to_solution_db(solution_db):
                return {'status': 'error', 'message': f'Failed to connect to {solution_db}'}
            
            # Extract module names from discoveries
            module_names = self._extract_modules_from_discoveries(discoveries)
            
            # Install modules
            if module_names:
                module_results = self._install_modules(solution_db, module_names)
                installation_results['details']['modules'] = module_results
                installation_results['modules_installed'] = module_results.get('modules_installed', [])
            
            # Verify features
            if 'models' in discoveries and discoveries['models'].get('status') == 'success':
                models_data = discoveries['models'].get('discovered_models', {})
                for model_name in models_data.keys():
                    if self._verify_model_exists(solution_db, model_name):
                        installation_results['models_available'].append(model_name)
            
            return installation_results
            
        except Exception as e:
            logger.error(f"Error in install_discovered_features: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _connect_to_solution_db(self, db_name: str) -> bool:
        """Connect to solution database"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            
            # Try with admin user (default for new databases)
            uid = common.authenticate(db_name, 'admin', 'admin', {})
            if uid:
                self.uid = uid
                self.models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
                logger.info(f"Successfully connected to {db_name} with admin")
                return True
            
            logger.error(f"Failed to connect to {db_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error connecting to solution database: {str(e)}")
            return False
    
    def _install_modules(self, db_name: str, module_names: List[str]) -> Dict[str, Any]:
        """Install modules in solution database"""
        try:
            results = {
                'status': 'success',
                'modules_installed': [],
                'modules_failed': [],
                'details': {}
            }
            
            for module_name in module_names:
                try:
                    # Check if module exists
                    module_ids = self.models.execute_kw(
                        db_name, self.uid, 'admin',
                        'ir.module.module', 'search',
                        [[('name', '=', module_name)]]
                    )
                    
                    if not module_ids:
                        logger.warning(f"Module {module_name} not found")
                        continue
                    
                    # Check if already installed
                    module_info = self.models.execute_kw(
                        db_name, self.uid, 'admin',
                        'ir.module.module', 'read',
                        [module_ids[0]], {'fields': ['name', 'state']}
                    )[0]
                    
                    if module_info['state'] == 'installed':
                        logger.info(f"Module {module_name} already installed")
                        continue
                    
                    # Install module
                    logger.info(f"Installing module {module_name}")
                    result = self.models.execute_kw(
                        db_name, self.uid, 'admin',
                        'ir.module.module', 'button_immediate_install',
                        [module_ids[0]]
                    )
                    
                    if result:
                        results['modules_installed'].append(module_name)
                        logger.info(f"Successfully installed {module_name}")
                    else:
                        results['modules_failed'].append(module_name)
                        logger.error(f"Failed to install {module_name}")
                        
                except Exception as e:
                    logger.error(f"Error installing module {module_name}: {str(e)}")
                    results['modules_failed'].append(module_name)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in _install_modules: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _extract_modules_from_discoveries(self, discoveries: Dict[str, Any]) -> List[str]:
        """Extract module names from discovery results"""
        module_names = set()
        
        # Extract from models
        if 'models' in discoveries and discoveries['models'].get('status') == 'success':
            models_data = discoveries['models'].get('discovered_models', {})
            for model_name, model_data in models_data.items():
                module_name = model_name.split('.')[0]
                module_names.add(module_name)
        
        # Add essential modules
        essential_modules = ['base', 'mail', 'contacts', 'product', 'sale']
        module_names.update(essential_modules)
        
        return list(module_names)
    
    def _verify_model_exists(self, db_name: str, model_name: str) -> bool:
        """Verify if a model exists in the database"""
        try:
            model_ids = self.models.execute_kw(
                db_name, self.uid, 'admin',
                'ir.model', 'search',
                [[('model', '=', model_name)]]
            )
            return len(model_ids) > 0
            
        except Exception as e:
            logger.error(f"Error verifying model {model_name}: {str(e)}")
            return False 