"""
FBS App Odoo Client Service

XML-RPC client for communicating with Odoo ERP system.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import xmlrpc.client

logger = logging.getLogger('odoo_client')


class OdooClientError(Exception):
    """Custom exception for Odoo client errors"""
    pass


class OdooClient:
    """XML-RPC client for communicating with Odoo"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        # Get configuration from FBS settings or Django settings
        fbs_config = getattr(settings, 'FBS_APP', {})
        self.base_url = base_url or fbs_config.get('ODOO_BASE_URL', 'http://localhost:8069')
        self.timeout = timeout or fbs_config.get('ODOO_TIMEOUT', 30)
        self.max_retries = fbs_config.get('ODOO_MAX_RETRIES', 3)
    
    def _get_odoo_credentials(self, database: str) -> Dict[str, str]:
        """Get Odoo credentials for the specified database"""
        # Get credentials from FBS settings or Django settings
        fbs_config = getattr(settings, 'FBS_APP', {})
        
        # Require explicit configuration - no hardcoded defaults
        username = fbs_config.get('DATABASE_USER')
        password = fbs_config.get('DATABASE_PASSWORD')
        
        if not username or not password:
            raise OdooClientError(
                'ODOO_DATABASE_USER and ODOO_DATABASE_PASSWORD must be configured in FBS_APP settings'
            )
        
        return {
            'username': username,
            'password': password,
            'database': database
        }
    
    def _authenticate(self, credentials: Dict[str, str]) -> int:
        """Authenticate with Odoo and return user ID"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/common')
            uid = common.authenticate(credentials['database'], credentials['username'], credentials['password'], {})
            if not uid:
                raise OdooClientError('Authentication failed')
            return uid
        except xmlrpc.client.Fault as e:
            logger.error(f"Odoo XML-RPC fault: {e.faultCode} - {e.faultString}")
            raise OdooClientError(f"Odoo authentication failed: {e.faultString}")
        except xmlrpc.client.ProtocolError as e:
            logger.error(f"Odoo protocol error: {e.errCode} - {e.errmsg}")
            raise OdooClientError(f"Odoo connection failed: {e.errmsg}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during Odoo authentication: {str(e)}")
            raise OdooClientError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected authentication error: {str(e)}")
            raise OdooClientError(f"Authentication failed: {str(e)}")
    
    def _get_models_proxy(self):
        """Get XML-RPC models proxy"""
        return xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
    
    def list_records(self, model_name: str, token: str, database: str,
                    domain: List = None, fields: List = None, 
                    order: str = None, limit: int = None, offset: int = None) -> Dict[str, Any]:
        """List records from Odoo model using XML-RPC"""
        try:
            credentials = self._get_odoo_credentials(database)
            return self.list_records_with_credentials(
                model_name=model_name,
                credentials=credentials,
                domain=domain,
                fields=fields,
                order=order,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"Error listing records: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve records'
            }
    
    def list_records_with_credentials(self, model_name: str, credentials: Dict[str, str],
                                   domain: List = None, fields: List = None,
                                   order: str = None, limit: int = None, offset: int = None) -> Dict[str, Any]:
        """List records using provided credentials"""
        try:
            uid = self._authenticate(credentials)
            models = self._get_models_proxy()
            
            # Prepare search parameters
            search_domain = domain or []
            search_fields = fields or ['id', 'name']
            
            # Search for records
            record_ids = models.execute_kw(
                credentials['database'], uid, credentials['password'],
                model_name, 'search',
                [search_domain], {'limit': limit or 100, 'offset': offset or 0}
            )
            
            if not record_ids:
                return {
                    'success': True,
                    'data': [],
                    'count': 0,
                    'message': 'No records found'
                }
            
            # Read the records
            records = models.execute_kw(
                credentials['database'], uid, credentials['password'],
                model_name, 'read',
                [record_ids], {'fields': search_fields}
            )
            
            # Apply ordering if specified
            if order and records:
                # Simple ordering - in production you might want more sophisticated ordering
                reverse = order.startswith('-')
                field = order[1:] if reverse else order
                records.sort(key=lambda x: x.get(field, ''), reverse=reverse)
            
            return {
                'success': True,
                'data': records,
                'count': len(records),
                'message': f'Retrieved {len(records)} records'
            }
            
        except Exception as e:
            logger.error(f"Error listing records with credentials: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve records'
            }
    
    def get_record(self, model_name: str, record_id: int, token: str, database: str,
                  fields: List = None) -> Dict[str, Any]:
        """Get a specific record from Odoo model using XML-RPC"""
        try:
            credentials = self._get_odoo_credentials(database)
            uid = self._authenticate(credentials)
            models = self._get_models_proxy()
            
            search_fields = fields or ['id', 'name']
            
            # Read the specific record
            records = models.execute_kw(
                credentials['database'], uid, credentials['password'],
                model_name, 'read',
                [[record_id]], {'fields': search_fields}
            )
            
            if not records:
                return {
                    'success': False,
                    'error': 'Record not found',
                    'message': f'Record {record_id} not found in {model_name}'
                }
            
            return {
                'success': True,
                'data': records[0],
                'message': 'Record retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"Error getting record: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve record'
            }
    
    def create_record(self, model_name: str, data: Dict[str, Any], token: str, database: str) -> Dict[str, Any]:
        """Create a new record in Odoo model"""
        try:
            credentials = self._get_odoo_credentials(database)
            uid = self._authenticate(credentials)
            models = self._get_models_proxy()
            
            # Create the record
            record_id = models.execute_kw(
                credentials['database'], uid, credentials['password'],
                model_name, 'create',
                [data]
            )
            
            if not record_id:
                return {
                    'success': False,
                    'error': 'Creation failed',
                    'message': 'Failed to create record'
                }
            
            return {
                'success': True,
                'data': {'id': record_id},
                'message': 'Record created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating record: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create record'
            }
    
    def update_record(self, model_name: str, record_id: int, data: Dict[str, Any], 
                     token: str, database: str) -> Dict[str, Any]:
        """Update an existing record in Odoo model"""
        try:
            credentials = self._get_odoo_credentials(database)
            uid = self._authenticate(credentials)
            models = self._get_models_proxy()
            
            # Update the record
            result = models.execute_kw(
                credentials['database'], uid, credentials['password'],
                model_name, 'write',
                [[record_id], data]
            )
            
            if not result:
                return {
                    'success': False,
                    'error': 'Update failed',
                    'message': 'Failed to update record'
                }
            
            return {
                'success': True,
                'data': {'id': record_id},
                'message': 'Record updated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error updating record: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to update record'
            }
    
    def delete_record(self, model_name: str, record_id: int, token: str, database: str) -> Dict[str, Any]:
        """Delete a record from Odoo model"""
        try:
            credentials = self._get_odoo_credentials(database)
            uid = self._authenticate(credentials)
            models = self._get_models_proxy()
            
            # Delete the record
            result = models.execute_kw(
                credentials['database'], uid, credentials['password'],
                model_name, 'unlink',
                [[record_id]]
            )
            
            if not result:
                return {
                    'success': False,
                    'error': 'Deletion failed',
                    'message': 'Failed to delete record'
                }
            
            return {
                'success': True,
                'data': {'id': record_id},
                'message': 'Record deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting record: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to delete record'
            }
    
    def execute_method(self, model_name: str, method_name: str, record_ids: List[int],
                      args: List = None, kwargs: Dict = None, token: str = None, 
                      database: str = None) -> Dict[str, Any]:
        """Execute a custom method on Odoo model"""
        try:
            credentials = self._get_odoo_credentials(database) if database else {}
            uid = self._authenticate(credentials) if credentials else None
            models = self._get_models_proxy()
            
            # Prepare arguments
            method_args = [record_ids] + (args or [])
            method_kwargs = kwargs or {}
            
            # Execute the method
            if uid and credentials:
                result = models.execute_kw(
                    credentials['database'], uid, credentials['password'],
                    model_name, method_name, method_args, method_kwargs
                )
            else:
                # For methods that don't require authentication
                result = models.execute_kw(
                    database, 0, '',  # No authentication
                    model_name, method_name, method_args, method_kwargs
                )
            
            return {
                'success': True,
                'data': result,
                'message': f'Method {method_name} executed successfully'
            }
            
        except Exception as e:
            logger.error(f"Error executing method {method_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to execute method {method_name}'
            }
    
    def get_model_fields(self, model_name: str, database: str) -> Dict[str, Any]:
        """Get field definitions for an Odoo model"""
        try:
            credentials = self._get_odoo_credentials(database)
            uid = self._authenticate(credentials)
            models = self._get_models_proxy()
            
            # Get field definitions
            fields = models.execute_kw(
                credentials['database'], uid, credentials['password'],
                model_name, 'fields_get',
                [], {'attributes': ['string', 'type', 'required', 'readonly']}
            )
            
            return {
                'success': True,
                'data': fields,
                'message': f'Retrieved field definitions for {model_name}'
            }
            
        except Exception as e:
            logger.error(f"Error getting model fields: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve field definitions'
            }
    
    def search_records(self, model_name: str, domain: List, database: str,
                      limit: int = None, offset: int = None) -> Dict[str, Any]:
        """Search for records in Odoo model"""
        try:
            credentials = self._get_odoo_credentials(database)
            uid = self._authenticate(credentials)
            models = self._get_models_proxy()
            
            # Search for records
            record_ids = models.execute_kw(
                credentials['database'], uid, credentials['password'],
                model_name, 'search',
                [domain], {'limit': limit or 100, 'offset': offset or 0}
            )
            
            return {
                'success': True,
                'data': record_ids,
                'count': len(record_ids),
                'message': f'Found {len(record_ids)} records'
            }
            
        except Exception as e:
            logger.error(f"Error searching records: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to search records'
            }
    
    def count_records(self, model_name: str, domain: List, database: str) -> Dict[str, Any]:
        """Count records in Odoo model matching domain"""
        try:
            credentials = self._get_odoo_credentials(database)
            uid = self._authenticate(credentials)
            models = self._get_models_proxy()
            
            # Count records
            count = models.execute_kw(
                credentials['database'], uid, credentials['password'],
                model_name, 'search_count',
                [domain]
            )
            
            return {
                'success': True,
                'data': {'count': count},
                'message': f'Found {count} records'
            }
            
        except Exception as e:
            logger.error(f"Error counting records: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to count records'
            }
