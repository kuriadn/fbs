"""
FBS FastAPI Discovery Service

PRESERVED from Django discovery_service.py
Service for Odoo model discovery and integration.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .service_interfaces import BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class DiscoveryService(BaseService, AsyncServiceMixin):
    """Service for discovering and managing Odoo models and modules - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)

    async def discover_models(self, database_name: str = None) -> Dict[str, Any]:
        """Discover all models in an Odoo database - PRESERVED from Django"""
        try:
            from .odoo_service import OdooService
            odoo_service = OdooService(self.solution_name)

            db_name = database_name or f"{self.solution_name}_db"
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }

            # Get model list from Odoo
            result = await odoo_service.search_read_records(
                model_name='ir.model',
                domain=[('state', '!=', 'manual')],
                fields=['name', 'model', 'state', 'modules', 'info'],
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
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def discover_modules(self, database_name: str = None) -> Dict[str, Any]:
        """Discover installed modules in an Odoo database - PRESERVED from Django"""
        try:
            from .odoo_service import OdooService
            odoo_service = OdooService(self.solution_name)

            db_name = database_name or f"{self.solution_name}_db"
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }

            # Get module list from Odoo using the dedicated search_read method
            result = await odoo_service.search_read_records(
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
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def discover_fields(self, model_name: str, database_name: str = None) -> Dict[str, Any]:
        """Discover fields for a specific Odoo model - PRESERVED from Django"""
        try:
            from .odoo_service import OdooService
            odoo_service = OdooService(self.solution_name)

            db_name = database_name or f"{self.solution_name}_db"
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }

            # Get field definitions
            result = await odoo_service.get_model_fields(model_name, db_name)

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
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def install_module(self, module_name: str, database_name: str = None) -> Dict[str, Any]:
        """Install a module in Odoo database - PRESERVED from Django"""
        try:
            from .odoo_service import OdooService
            odoo_service = OdooService(self.solution_name)

            db_name = database_name or f"{self.solution_name}_db"
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }

            # First find the module
            search_result = await odoo_service.search_read_records(
                model_name='ir.module.module',
                domain=[('name', '=', module_name)],
                fields=['id'],
                database=db_name
            )

            if not search_result['success'] or not search_result['data']:
                return {
                    'success': False,
                    'error': 'Module not found',
                    'message': f'Module {module_name} not found in {db_name}'
                }

            module_id = search_result['data'][0]['id']

            # Install the module
            result = await odoo_service.execute_method(
                model_name='ir.module.module',
                method_name='button_immediate_install',
                record_ids=[module_id],
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
                    'module_id': module_id,
                    'action': 'install'
                },
                'message': f'Module {module_name} installation initiated'
            }

        except Exception as e:
            logger.error(f"Error installing module {module_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def uninstall_module(self, module_name: str, database_name: str = None) -> Dict[str, Any]:
        """Uninstall a module from Odoo database - PRESERVED from Django"""
        try:
            from .odoo_service import OdooService
            odoo_service = OdooService(self.solution_name)

            db_name = database_name or f"{self.solution_name}_db"
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }

            # First find the module
            search_result = await odoo_service.search_read_records(
                model_name='ir.module.module',
                domain=[('name', '=', module_name)],
                fields=['id'],
                database=db_name
            )

            if not search_result['success'] or not search_result['data']:
                return {
                    'success': False,
                    'error': 'Module not found',
                    'message': f'Module {module_name} not found in {db_name}'
                }

            module_id = search_result['data'][0]['id']

            # Uninstall the module
            result = await odoo_service.execute_method(
                model_name='ir.module.module',
                method_name='button_immediate_uninstall',
                record_ids=[module_id],
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
                    'module_id': module_id,
                    'action': 'uninstall'
                },
                'message': f'Module {module_name} uninstallation initiated'
            }

        except Exception as e:
            logger.error(f"Error uninstalling module {module_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_model_relationships(self, model_name: str, database_name: str = None) -> Dict[str, Any]:
        """Get relationships between models - PRESERVED from Django"""
        try:
            from .odoo_service import OdooService
            odoo_service = OdooService(self.solution_name)

            db_name = database_name or f"{self.solution_name}_db"
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }

            # Get field definitions to analyze relationships
            result = await odoo_service.get_model_fields(model_name, db_name)

            if not result['success']:
                return result

            fields = result['data']

            # Analyze relationships
            relationships = {
                'many2one': [],
                'one2many': [],
                'many2many': []
            }

            for field_name, field_info in fields.items():
                field_type = field_info.get('type', '')
                if field_type in relationships:
                    relationships[field_type].append({
                        'field_name': field_name,
                        'relation': field_info.get('relation', ''),
                        'string': field_info.get('string', field_name)
                    })

            return {
                'success': True,
                'data': {
                    'model_name': model_name,
                    'relationships': relationships,
                    'total_relationships': sum(len(rel) for rel in relationships.values())
                },
                'message': f'Found {sum(len(rel) for rel in relationships.values())} relationships for {model_name}'
            }

        except Exception as e:
            logger.error(f"Error getting model relationships: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def discover_workflows(self, model_name: str, database_name: str = None) -> Dict[str, Any]:
        """Discover workflows for a model - PRESERVED from Django"""
        try:
            from .odoo_service import OdooService
            odoo_service = OdooService(self.solution_name)

            db_name = database_name or f"{self.solution_name}_db"
            if not db_name:
                return {
                    'success': False,
                    'error': 'Database name not specified',
                    'message': 'Please provide a database name'
                }

            # Get workflow definitions
            result = await odoo_service.search_read_records(
                model_name='workflow',
                domain=[('osv', '=', model_name)],
                fields=['name', 'on_create', 'activities'],
                database=db_name
            )

            if not result['success']:
                return result

            workflows = result['data']

            return {
                'success': True,
                'data': {
                    'model_name': model_name,
                    'workflows': workflows,
                    'workflow_count': len(workflows)
                },
                'message': f'Found {len(workflows)} workflows for {model_name}'
            }

        except Exception as e:
            logger.error(f"Error discovering workflows: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    def _categorize_models(self, models: List[Dict]) -> Dict[str, List]:
        """Categorize models by type - PRESERVED from Django"""
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
        """Process field information for better readability - PRESERVED from Django"""
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
        """Process module information for better readability - PRESERVED from Django"""
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

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'discovery',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
