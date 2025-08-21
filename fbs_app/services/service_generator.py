"""
FBS App Service Interface Generator

Service for dynamically generating service interfaces based on discovered Odoo capabilities.
"""

import logging
from typing import Dict, Any, List, Optional
from django.conf import settings

logger = logging.getLogger('fbs_app')


class FBSServiceGenerator:
    """Service for generating service interfaces based on discovered Odoo capabilities"""
    
    def __init__(self):
        self.fbs_config = getattr(settings, 'FBS_APP', {})
        self.generated_services = {}
    
    def generate_model_service(self, model_name: str, model_fields: List[Dict], 
                             database_name: str, token: str) -> Dict[str, Any]:
        """Generate service interface for a specific Odoo model"""
        try:
            # Create dynamic service class
            service_class = self._create_dynamic_service(
                model_name, model_fields, database_name, token
            )
            
            # Store generated service
            self.generated_services[model_name] = {
                'service_class': service_class,
                'model_fields': model_fields,
                'database_name': database_name
            }
            
            return {
                'success': True,
                'model_name': model_name,
                'service_generated': True,
                'capabilities': self._get_capability_list(model_name),
                'message': f'Service interface generated successfully for {model_name}'
            }
            
        except Exception as e:
            logger.error(f"Error generating model service: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_dynamic_service(self, model_name: str, model_fields: List[Dict], 
                              database_name: str, token: str):
        """Create a dynamic service class for the model"""
        
        # Create field mappings
        field_mappings = {}
        for field in model_fields:
            field_name = field.get('name', '')
            field_type = field.get('type', 'char')
            field_mappings[field_name] = field_type
        
        # Create dynamic service class
        class DynamicModelService:
            """Dynamic service for Odoo model: {model_name}"""
            
            def __init__(self, database_name: str = None, token: str = None):
                self.model_name = model_name
                self.database_name = database_name or 'default'
                self.token = token
                self.fields = field_mappings
            
            def list_records(self, limit: int = 100, offset: int = 0, domain: List = None, fields: List = None):
                """List records from the model"""
                try:
                    from .odoo_client import OdooClient
                    
                    odoo_client = OdooClient()
                    
                    # Set defaults
                    domain = domain or []
                    fields = fields or []
                    
                    # Get records from Odoo
                    result = odoo_client.list_records(
                        model_name=self.model_name,
                        token=self.token,
                        database=self.database_name,
                        domain=domain,
                        fields=fields,
                        limit=int(limit),
                        offset=int(offset)
                    )
                    
                    if result['success']:
                        return {
                            'success': True,
                            'data': result.get('data', []),
                            'total_count': result.get('total_count', 0),
                            'model_name': self.model_name
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Unknown error')
                        }
                        
                except Exception as e:
                    logger.error(f"Error in list_records method: {str(e)}")
                    return {
                        'success': False,
                        'error': str(e)
                    }
            
            def get_record(self, record_id: int, fields: List = None):
                """Get a specific record"""
                try:
                    from .odoo_client import OdooClient
                    
                    odoo_client = OdooClient()
                    
                    # Set defaults
                    fields = fields or []
                    
                    # Get record from Odoo
                    result = odoo_client.get_record(
                        model_name=self.model_name,
                        record_id=int(record_id),
                        token=self.token,
                        database=self.database_name,
                        fields=fields
                    )
                    
                    if result['success']:
                        return {
                            'success': True,
                            'data': result.get('data', {}),
                            'model_name': self.model_name
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Record not found')
                        }
                        
                except Exception as e:
                    logger.error(f"Error in get_record method: {str(e)}")
                    return {
                        'success': False,
                        'error': str(e)
                    }
            
            def create_record(self, data: Dict[str, Any]):
                """Create a new record"""
                try:
                    from .odoo_client import OdooClient
                    
                    odoo_client = OdooClient()
                    
                    # Create record in Odoo
                    result = odoo_client.create_record(
                        model_name=self.model_name,
                        data=data,
                        token=self.token,
                        database=self.database_name
                    )
                    
                    if result['success']:
                        return {
                            'success': True,
                            'data': result.get('data', {}),
                            'model_name': self.model_name,
                            'record_id': result.get('record_id')
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Failed to create record')
                        }
                        
                except Exception as e:
                    logger.error(f"Error in create_record method: {str(e)}")
                    return {
                        'success': False,
                        'error': str(e)
                    }
            
            def update_record(self, record_id: int, data: Dict[str, Any]):
                """Update an existing record"""
                try:
                    from .odoo_client import OdooClient
                    
                    odoo_client = OdooClient()
                    
                    # Update record in Odoo
                    result = odoo_client.update_record(
                        model_name=self.model_name,
                        record_id=int(record_id),
                        data=data,
                        token=self.token,
                        database=self.database_name
                    )
                    
                    if result['success']:
                        return {
                            'success': True,
                            'data': result.get('data', {}),
                            'model_name': self.model_name,
                            'record_id': record_id
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Failed to update record')
                        }
                        
                except Exception as e:
                    logger.error(f"Error in update_record method: {str(e)}")
                    return {
                        'success': False,
                        'error': str(e)
                    }
            
            def delete_record(self, record_id: int):
                """Delete a record"""
                try:
                    from .odoo_client import OdooClient
                    
                    odoo_client = OdooClient()
                    
                    # Delete record in Odoo
                    result = odoo_client.delete_record(
                        model_name=self.model_name,
                        record_id=int(record_id),
                        token=self.token,
                        database=self.database_name
                    )
                    
                    if result['success']:
                        return {
                            'success': True,
                            'model_name': self.model_name,
                            'record_id': record_id,
                            'message': 'Record deleted successfully'
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Failed to delete record')
                        }
                        
                except Exception as e:
                    logger.error(f"Error in delete_record method: {str(e)}")
                    return {
                        'success': False,
                        'error': str(e)
                    }
            
            def execute_method(self, record_id: int, method_name: str, params: Dict = None):
                """Execute a method on a record"""
                try:
                    from .odoo_client import OdooClient
                    
                    odoo_client = OdooClient()
                    
                    # Set defaults
                    params = params or {}
                    
                    # Execute method in Odoo
                    result = odoo_client.execute_method(
                        model_name=self.model_name,
                        record_id=int(record_id),
                        method_name=method_name,
                        params=params,
                        token=self.token,
                        database=self.database_name
                    )
                    
                    if result['success']:
                        return {
                            'success': True,
                            'data': result.get('data', {}),
                            'model_name': self.model_name,
                            'method_name': method_name,
                            'record_id': record_id
                        }
                    else:
                        return {
                            'success': False,
                            'error': result.get('error', 'Failed to execute method')
                        }
                        
                except Exception as e:
                    logger.error(f"Error in execute_method: {str(e)}")
                    return {
                        'success': False,
                        'error': str(e)
                    }
            
            def get_model_info(self):
                """Get model information and field details"""
                return {
                    'success': True,
                    'model_name': self.model_name,
                    'fields': self.fields,
                    'capabilities': self._get_capabilities()
                }
            
            def _get_capabilities(self):
                """Get available capabilities for this service"""
                return [
                    'list_records',
                    'get_record',
                    'create_record',
                    'update_record',
                    'delete_record',
                    'execute_method',
                    'get_model_info'
                ]
        
        return DynamicModelService
    
    def _get_capability_list(self, model_name: str) -> List[str]:
        """Get list of capabilities for a model"""
        return [
            f'list_{model_name}s',
            f'get_{model_name}',
            f'create_{model_name}',
            f'update_{model_name}',
            f'delete_{model_name}',
            f'execute_{model_name}_method',
            f'get_{model_name}_info'
        ]
    
    def generate_bulk_services(self, models_data: List[Dict]) -> Dict[str, Any]:
        """Generate service interfaces for multiple models at once"""
        try:
            successful_generations = 0
            failed_generations = 0
            total_models = len(models_data)
            
            for model_data in models_data:
                result = self.generate_model_service(
                    model_name=model_data['model_name'],
                    model_fields=model_data['fields'],
                    database_name=model_data['database_name'],
                    token=model_data['token']
                )
                
                if result['success']:
                    successful_generations += 1
                else:
                    failed_generations += 1
            
            return {
                'success': True,
                'total_models': total_models,
                'successful_generations': successful_generations,
                'failed_generations': failed_generations,
                'message': f'Generated {successful_generations} out of {total_models} service interfaces'
            }
            
        except Exception as e:
            logger.error(f"Error in bulk service generation: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_generated_services(self) -> Dict[str, Any]:
        """Get all generated service interfaces"""
        try:
            return {
                'success': True,
                'generated_services': list(self.generated_services.keys()),
                'total_services': len(self.generated_services),
                'service_details': self.generated_services
            }
        except Exception as e:
            logger.error(f"Error getting generated services: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_generated_service(self, model_name: str) -> Dict[str, Any]:
        """Remove a generated service interface"""
        try:
            if model_name in self.generated_services:
                del self.generated_services[model_name]
                return {
                    'success': True,
                    'message': f'Service interface removed successfully for {model_name}'
                }
            else:
                return {
                    'success': False,
                    'error': f'No service interface found for model {model_name}'
                }
        except Exception as e:
            logger.error(f"Error removing generated service: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_service_instance(self, model_name: str):
        """Get an instance of a generated service"""
        try:
            if model_name in self.generated_services:
                service_class = self.generated_services[model_name]['service_class']
                return service_class()
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting service instance: {str(e)}")
            return None
