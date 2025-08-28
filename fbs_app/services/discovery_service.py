"""
FBS App Discovery Service

Service for Odoo model discovery and integration.
"""

import logging
import xmlrpc.client
from typing import Dict, Any, List, Optional
from django.conf import settings
from .odoo_client import OdooClient, OdooClientError

logger = logging.getLogger('fbs_app')


class DiscoveryService:
    """Service for discovering and managing Odoo models and modules"""
    
    def __init__(self, solution_name: str = None, database_name: str = None):
        self.fbs_config = getattr(settings, 'FBS_APP', {})
        self.solution_name = solution_name
        self.database_name = database_name
        self.odoo_client = OdooClient(solution_name)
    
    def discover_models(self, database_name: str = None) -> Dict[str, Any]:
        """Discover all models in an Odoo database"""
        try:
            db_name = database_name or self.database_name
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }
            
            # Get model list from Odoo
            result = self.odoo_client.execute_method(
                model_name='ir.model',
                method_name='search_read',
                record_ids=[],
                args=[],
                kwargs={
                    'domain': [('state', '!=', 'manual')],
                    'fields': ['name', 'model', 'state', 'modules', 'info']
                },
                database=db_name
            )
            
            if not result['success']:
                return result
            
            models = result['data']
            
            # Process and categorize models
            categorized_models = self._categorize_models(models)
            
            return {
                'success': True,
                'data': {
                    'models': models,
                    'categorized': categorized_models,
                    'total_count': len(models)
                },
                'message': f'Discovered {len(models)} models in {db_name}'
            }
            
        except Exception as e:
            logger.error(f"Error discovering models: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to discover models'
            }
    
    def discover_model_fields(self, model_name: str, database_name: str = None) -> Dict[str, Any]:
        """Discover fields for a specific model"""
        try:
            db_name = database_name or self.database_name
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }
            
            # Get field definitions
            result = self.odoo_client.get_model_fields(model_name, db_name)
            
            if not result['success']:
                return result
            
            fields = result['data']
            
            # Process field information
            processed_fields = self._process_field_info(fields)
            
            return {
                'success': True,
                'data': {
                    'model_name': model_name,
                    'fields': processed_fields,
                    'field_count': len(processed_fields)
                },
                'message': f'Discovered {len(processed_fields)} fields for {model_name}'
            }
            
        except Exception as e:
            logger.error(f"Error discovering model fields: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to discover model fields'
            }
    
    def discover_modules(self, database_name: str = None) -> Dict[str, Any]:
        """Discover installed modules in an Odoo database"""
        try:
            db_name = database_name or self.database_name
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }
            
            # Get module list from Odoo using the dedicated search_read method
            result = self.odoo_client.search_read_records(
                model_name='ir.module.module',
                domain=[('state', 'in', ['installed', 'to install', 'to upgrade'])],
                fields=['name', 'state', 'description', 'category_id', 'dependencies_id'],
                database=db_name
            )
            
            if not result['success']:
                return result
            
            modules = result['data']
            
            # Process module information
            processed_modules = self._process_module_info(modules)
            
            return {
                'success': True,
                'data': {
                    'modules': processed_modules,
                    'installed_count': len([m for m in processed_modules if m['state'] == 'installed']),
                    'total_count': len(processed_modules)
                },
                'message': f'Discovered {len(processed_modules)} modules in {db_name}'
            }
            
        except Exception as e:
            logger.error(f"Error discovering modules: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to discover modules'
            }
    
    def discover_fields(self, model_name: str, database_name: str = None) -> Dict[str, Any]:
        """Discover fields for a specific Odoo model"""
        try:
            db_name = database_name or self.database_name
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }
            
            # Get field definitions
            result = self.odoo_client.get_model_fields(model_name, db_name)
            
            if not result['success']:
                return result
            
            fields = result['data']
            
            # Process field information
            processed_fields = self._process_field_info(fields)
            
            return {
                'success': True,
                'data': {
                    'model_name': model_name,
                    'fields': processed_fields,
                    'field_count': len(processed_fields)
                },
                'message': f'Discovered {len(processed_fields)} fields for {model_name}'
            }
            
        except Exception as e:
            logger.error(f"Error discovering model fields: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to discover model fields'
            }
    
    def install_module(self, module_name: str, database_name: str = None) -> Dict[str, Any]:
        """Install a module in Odoo database"""
        try:
            db_name = database_name or self.database_name
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }
            
            # Install the module
            result = self.odoo_client.execute_method(
                model_name='ir.module.module',
                method_name='button_immediate_install',
                record_ids=[],  # Will be set by search
                args=[],
                kwargs={},
                database=db_name
            )
            
            if not result['success']:
                return result
            
            return {
                'success': True,
                'data': {
                    'module_name': module_name,
                    'action': 'install'
                },
                'message': f'Module {module_name} installation initiated'
            }
            
        except Exception as e:
            logger.error(f"Error installing module {module_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to install module {module_name}'
            }
    
    def uninstall_module(self, module_name: str, database_name: str = None) -> Dict[str, Any]:
        """Uninstall a module from Odoo database"""
        try:
            db_name = database_name or self.database_name
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }
            
            # Uninstall the module
            result = self.odoo_client.execute_method(
                model_name='ir.module.module',
                method_name='button_immediate_uninstall',
                record_ids=[],  # Will be set by search
                args=[],
                kwargs={},
                database=db_name
            )
            
            if not result['success']:
                return result
            
            return {
                'success': True,
                'data': {
                    'module_name': module_name,
                    'action': 'uninstall'
                },
                'message': f'Module {module_name} uninstallation initiated'
            }
            
        except Exception as e:
            logger.error(f"Error uninstalling module {module_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to uninstall module {module_name}'
            }
    
    def _categorize_models(self, models: List[Dict]) -> Dict[str, List]:
        """Categorize models by type"""
        categories = {
            'business': [],
            'technical': [],
            'system': [],
            'custom': []
        }
        
        for model in models:
            model_name = model.get('model', '')
            
            if model_name.startswith('ir.') or model_name.startswith('res.'):
                categories['system'].append(model)
            elif model_name.startswith('mail.') or model_name.startswith('web.'):
                categories['technical'].append(model)
            elif any(biz in model_name for biz in ['sale', 'purchase', 'stock', 'account', 'hr', 'project']):
                categories['business'].append(model)
            else:
                categories['custom'].append(model)
        
        return categories
    
    def _process_field_info(self, fields: Dict) -> List[Dict]:
        """Process field information for better readability"""
        processed_fields = []
        
        for field_name, field_info in fields.items():
            processed_field = {
                'name': field_name,
                'string': field_info.get('string', field_name),
                'type': field_info.get('type', 'unknown'),
                'required': field_info.get('required', False),
                'readonly': field_info.get('readonly', False),
                'help': field_info.get('help', ''),
                'selection': field_info.get('selection', []),
                'relation': field_info.get('relation', ''),
                'domain': field_info.get('domain', ''),
            }
            processed_fields.append(processed_field)
        
        return processed_fields
    
    def _process_module_info(self, modules: List[Dict]) -> List[Dict]:
        """Process module information for better readability"""
        processed_modules = []
        
        for module in modules:
            # Handle category_id - could be integer or list
            category_id = module.get('category_id')
            if isinstance(category_id, list) and len(category_id) > 1:
                category = category_id[1]
            elif isinstance(category_id, int):
                category = str(category_id)  # Convert ID to string
            else:
                category = ''
            
            # Handle dependencies_id - could be integer or list
            dependencies_id = module.get('dependencies_id')
            if isinstance(dependencies_id, list):
                dependencies = [str(dep) if isinstance(dep, int) else str(dep[1]) if isinstance(dep, list) and len(dep) > 1 else str(dep) for dep in dependencies_id]
            elif isinstance(dependencies_id, int):
                dependencies = [str(dependencies_id)]
            else:
                dependencies = []
            
            processed_module = {
                'name': module.get('name', ''),
                'state': module.get('state', 'unknown'),
                'description': module.get('description', ''),
                'category': category,
                'dependencies': dependencies
            }
            processed_modules.append(processed_module)
        
        return processed_modules
