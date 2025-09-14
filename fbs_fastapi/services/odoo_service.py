"""
FBS FastAPI Odoo Service

Preserves the sophisticated Odoo integration framework from Django.
Converts XML-RPC client to async HTTP client while maintaining same interface.
"""

import xmlrpc.client
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin
import asyncio
from datetime import datetime

from .service_interfaces import OdooInterfaceProtocol, BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class OdooService(BaseService, AsyncServiceMixin, OdooInterfaceProtocol):
    """Odoo service preserving Django integration patterns"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)
        self.base_url = None
        self.database = None
        self.username = None
        self.password = None
        self.uid = None
        self._common = None
        self._models = None

    def configure_connection(self, base_url: str, database: str, username: str, password: str):
        """Configure Odoo connection (preserved from Django)"""
        self.base_url = base_url.rstrip('/')
        self.database = database
        self.username = username
        self.password = password

        # Initialize XML-RPC proxies
        self._common = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/common')
        self._models = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')

    def _ensure_authenticated(self) -> bool:
        """Ensure we have valid authentication (preserved from Django)"""
        if not all([self.base_url, self.database, self.username, self.password]):
            raise ValueError("Odoo connection not configured")

        if self.uid is None:
            try:
                self.uid = self._common.authenticate(
                    self.database, self.username, self.password, {}
                )
                if not self.uid:
                    raise ValueError("Authentication failed")
            except Exception as e:
                logger.error(f"Odoo authentication failed: {e}")
                raise

        return True

    async def discover_models(self) -> Dict[str, Any]:
        """Discover available Odoo models (preserved from Django)"""
        try:
            self._ensure_authenticated()

            # Get all installed models
            model_ids = self._models.execute_kw(
                self.database, self.uid, self.password,
                'ir.model', 'search',
                [[('state', '=', 'manual')]]  # Only user-created models
            )

            if not model_ids:
                return {
                    'success': True,
                    'models': [],
                    'count': 0,
                    'message': 'No models found'
                }

            # Get model details
            model_data = self._models.execute_kw(
                self.database, self.uid, self.password,
                'ir.model', 'read',
                [model_ids, ['model', 'name', 'info', 'state']]
            )

            models = []
            for model in model_data:
                models.append({
                    'model_name': model['model'],
                    'technical_name': model['model'],
                    'display_name': model['name'],
                    'description': model.get('info', ''),
                    'state': model['state'],
                    'capabilities': self._get_model_capabilities(model['model'])
                })

            return {
                'success': True,
                'models': models,
                'count': len(models),
                'message': f'Discovered {len(models)} models'
            }

        except Exception as e:
            logger.error(f"Error discovering models: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def discover_fields(self, model_name: str) -> Dict[str, Any]:
        """Discover fields for a specific model (preserved from Django)"""
        try:
            self._ensure_authenticated()

            # Get field definitions
            field_ids = self._models.execute_kw(
                self.database, self.uid, self.password,
                'ir.model.fields', 'search',
                [[('model', '=', model_name)]]
            )

            if not field_ids:
                return {
                    'success': True,
                    'fields': [],
                    'count': 0,
                    'message': f'No fields found for model {model_name}'
                }

            # Get field details
            field_data = self._models.execute_kw(
                self.database, self.uid, self.password,
                'ir.model.fields', 'read',
                [field_ids, [
                    'name', 'field_description', 'ttype', 'required',
                    'readonly', 'store', 'relation', 'selection'
                ]]
            )

            fields = []
            for field in field_data:
                fields.append({
                    'field_name': field['name'],
                    'technical_name': field['name'],
                    'display_name': field['field_description'] or field['name'],
                    'field_type': field['ttype'],
                    'required': field['required'],
                    'readonly': field['readonly'],
                    'stored': field['store'],
                    'relation_model': field.get('relation'),
                    'selection_options': field.get('selection', [])
                })

            return {
                'success': True,
                'model': model_name,
                'fields': fields,
                'count': len(fields),
                'message': f'Discovered {len(fields)} fields for {model_name}'
            }

        except Exception as e:
            logger.error(f"Error discovering fields for {model_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    def _get_model_capabilities(self, model_name: str) -> List[str]:
        """Get model capabilities (preserved from Django)"""
        capabilities = []

        try:
            # Check if model has create permission
            can_create = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'check_access_rights',
                ['create'], {'raise_exception': False}
            )
            if can_create:
                capabilities.append('create')

            # Check if model has read permission
            can_read = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'check_access_rights',
                ['read'], {'raise_exception': False}
            )
            if can_read:
                capabilities.append('read')

            # Check if model has write permission
            can_write = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'check_access_rights',
                ['write'], {'raise_exception': False}
            )
            if can_write:
                capabilities.append('write')

            # Check if model has unlink permission
            can_unlink = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'check_access_rights',
                ['unlink'], {'raise_exception': False}
            )
            if can_unlink:
                capabilities.append('delete')

        except Exception as e:
            logger.warning(f"Error checking capabilities for {model_name}: {e}")

        return capabilities

    async def get_records(self, model_name: str, domain: List, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get records from Odoo model (preserved from Django)"""
        try:
            self._ensure_authenticated()

            search_fields = fields or ['id', 'name']

            # Search and read records
            records = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'search_read',
                [domain, search_fields]
            )

            return {
                'success': True,
                'model': model_name,
                'data': records,
                'count': len(records),
                'message': f'Found {len(records)} records'
            }

        except Exception as e:
            logger.error(f"Error getting records from {model_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def create_record(self, model_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in Odoo (preserved from Django)"""
        try:
            self._ensure_authenticated()

            record_id = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'create', [data]
            )

            return {
                'success': True,
                'model': model_name,
                'record_id': record_id,
                'data': data,
                'message': f'Record created successfully with ID {record_id}'
            }

        except Exception as e:
            logger.error(f"Error creating record in {model_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def update_record(self, model_name: str, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record in Odoo (preserved from Django)"""
        try:
            self._ensure_authenticated()

            result = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'write',
                [[record_id], data]
            )

            if result:
                return {
                    'success': True,
                    'model': model_name,
                    'record_id': record_id,
                    'data': data,
                    'message': f'Record {record_id} updated successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Update failed',
                    'message': f'Failed to update record {record_id}'
                }

        except Exception as e:
            logger.error(f"Error updating record {record_id} in {model_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def delete_record(self, model_name: str, record_id: int) -> Dict[str, Any]:
        """Delete a record in Odoo (preserved from Django)"""
        try:
            self._ensure_authenticated()

            result = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'unlink',
                [[record_id]]
            )

            if result:
                return {
                    'success': True,
                    'model': model_name,
                    'record_id': record_id,
                    'message': f'Record {record_id} deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Delete failed',
                    'message': f'Failed to delete record {record_id}'
                }

        except Exception as e:
            logger.error(f"Error deleting record {record_id} in {model_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def execute_workflow(self, model_name: str, record_id: int, action: str) -> Dict[str, Any]:
        """Execute a workflow action on a record (preserved from Django)"""
        try:
            self._ensure_authenticated()

            # Execute workflow action
            result = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'signal_workflow',
                [[record_id], action]
            )

            return {
                'success': True,
                'model': model_name,
                'record_id': record_id,
                'action': action,
                'result': result,
                'message': f'Workflow action {action} executed successfully'
            }

        except Exception as e:
            logger.error(f"Error executing workflow action {action} on {model_name}:{record_id}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def search_records(self, model_name: str, domain: List, fields: Optional[List[str]] = None,
                           limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
        """Search for records in Odoo model (preserved from Django)"""
        try:
            self._ensure_authenticated()

            # Search for record IDs
            record_ids = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'search',
                [domain], {
                    'limit': limit or 100,
                    'offset': offset or 0
                }
            )

            return {
                'success': True,
                'model': model_name,
                'record_ids': record_ids,
                'count': len(record_ids),
                'message': f'Found {len(record_ids)} records'
            }

        except Exception as e:
            logger.error(f"Error searching records in {model_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def count_records(self, model_name: str, domain: List) -> Dict[str, Any]:
        """Count records in Odoo model matching domain (preserved from Django)"""
        try:
            self._ensure_authenticated()

            count = self._models.execute_kw(
                self.database, self.uid, self.password,
                model_name, 'search_count',
                [domain]
            )

            return {
                'success': True,
                'model': model_name,
                'count': count,
                'message': f'Counted {count} records'
            }

        except Exception as e:
            logger.error(f"Error counting records in {model_name}: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        try:
            if not self.base_url:
                return {
                    'service': 'odoo',
                    'status': 'not_configured',
                    'message': 'Odoo connection not configured'
                }

            # Test connection
            version_info = self._common.version()
            return {
                'service': 'odoo',
                'status': 'healthy',
                'version': version_info.get('server_version'),
                'url': self.base_url,
                'database': self.database,
                'authenticated': self.uid is not None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'service': 'odoo',
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
