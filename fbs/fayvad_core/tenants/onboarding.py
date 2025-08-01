import xmlrpc.client

class OnboardingService:
    """Service for onboarding new tenants/clients with module installation (spec-compliant)"""
    def __init__(self, odoo_url=None, master_password=None, common_client=None, db_service=None, object_client=None):
        self.odoo_url = odoo_url or 'http://localhost:8069'
        self.master_password = master_password or 'admin'
        
        if common_client and db_service and object_client:
            self.db_service = db_service
            self.common = common_client
            self.object = object_client
        else:
            self.db_service = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/db')
            self.common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.object = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')

    def onboard_client(self, client_data: dict) -> dict:
        """
        Onboard a new client with custom module installation.
        Args:
            client_data (dict): Client information including modules to install
        Returns:
            dict: Onboarding result
        """
        result = {'success': False, 'errors': [], 'database': None}
        
        # Extract client data
        client_name = client_data.get('name')
        modules_to_install = client_data.get('modules', [])
        admin_password = client_data.get('admin_password', 'admin123')
        
        if not client_name:
            result['errors'].append('Client name is required')
            return result
            
        # Generate database name
        database_name = f"fayvad_{client_name.lower().replace(' ', '_')}"
        
        try:
            # Check if database already exists
            existing_dbs = self.db_service.list()
            if database_name in existing_dbs:
                result['errors'].append(f'Database {database_name} already exists')
                return result
                
            # Create database
            success = self.db_service.create_database(
                self.master_password, 
                database_name, 
                'admin', 
                admin_password, 
                'en_US'
            )
            
            if not success:
                result['errors'].append('Failed to create database')
                return result
                
            # Authenticate with the new database
            uid = self.common.authenticate(database_name, 'admin', admin_password, {})
            if not uid:
                result['errors'].append('Failed to authenticate with new database')
                return result
                
            # Install base modules first
            base_modules = ['base', 'web', 'mail']
            for module in base_modules:
                self._install_module(database_name, uid, admin_password, module)
                
            # Install requested modules
            installed_modules = []
            for module in modules_to_install:
                if self._install_module(database_name, uid, admin_password, module):
                    installed_modules.append(module)
                    
            # Update database configuration
            self._configure_database(database_name, uid, admin_password, client_data)
            
            result['success'] = True
            result['database'] = database_name
            result['installed_modules'] = installed_modules
            result['message'] = f'Successfully onboarded client {client_name} with {len(installed_modules)} modules'
            
        except Exception as e:
            result['errors'].append(f'Onboarding failed: {e}')
            
        return result

    def _install_module(self, database_name: str, uid: int, password: str, module_name: str) -> bool:
        """
        Install a specific module in the database.
        """
        try:
            # Check if module is available
            module_ids = self.object.execute_kw(
                database_name, uid, password, 
                'ir.module.module', 'search', 
                [[('name', '=', module_name), ('state', '=', 'uninstalled')]]
            )
            
            if not module_ids:
                # Module might already be installed or not available
                return False
                
            # Install the module
            self.object.execute_kw(
                database_name, uid, password,
                'ir.module.module', 'button_immediate_install',
                [module_ids]
            )
            
            return True
            
        except Exception as e:
            print(f"Error installing module {module_name}: {e}")
            return False

    def _configure_database(self, database_name: str, uid: int, password: str, client_data: dict):
        """
        Configure the database with client-specific settings.
        """
        try:
            # Set company name
            company_ids = self.object.execute_kw(
                database_name, uid, password,
                'res.company', 'search', [[]]
            )
            
            if company_ids:
                self.object.execute_kw(
                    database_name, uid, password,
                    'res.company', 'write',
                    [[company_ids[0]], {'name': client_data.get('name', 'New Company')}]
                )
                
            # Set timezone and other settings based on client data
            # This can be extended based on client requirements
            
        except Exception as e:
            print(f"Error configuring database: {e}")

    def get_available_modules(self) -> dict:
        """
        Get list of available modules for installation.
        """
        result = {'success': False, 'modules': [], 'errors': []}
        
        try:
            # Use a template database to check available modules
            template_db = 'template0'  # or any existing database
            
            # Get all available modules
            module_ids = self.object.execute_kw(
                template_db, 1, 'admin',  # Use admin credentials
                'ir.module.module', 'search',
                [[('state', '!=', 'uninstalled')]]
            )
            
            modules = self.object.execute_kw(
                template_db, 1, 'admin',
                'ir.module.module', 'read',
                [module_ids],
                {'fields': ['name', 'shortdesc', 'category_id', 'state']}
            )
            
            # Group by category
            categories = {}
            for module in modules:
                category = module.get('category_id', ['', ''])[1] if module.get('category_id') else 'Other'
                if category not in categories:
                    categories[category] = []
                categories[category].append({
                    'name': module['name'],
                    'description': module.get('shortdesc', ''),
                    'state': module.get('state', '')
                })
                
            result['success'] = True
            result['modules'] = categories
            
        except Exception as e:
            result['errors'].append(f'Failed to get available modules: {e}')
            
        return result 