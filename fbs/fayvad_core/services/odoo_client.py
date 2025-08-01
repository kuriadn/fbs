import requests
import json
import logging
from typing import Dict, Any, Optional, List
from django.conf import settings
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

logger = logging.getLogger('odoo_client')


class OdooClientError(Exception):
    """Custom exception for Odoo client errors"""
    pass


class OdooClient:
    """HTTP client for communicating with Odoo API"""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or settings.ODOO_CONFIG['BASE_URL']
        self.timeout = timeout or settings.ODOO_CONFIG['TIMEOUT']
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry strategy"""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=settings.ODOO_CONFIG['MAX_RETRIES'],
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=settings.ODOO_CONFIG['CONNECTION_POOL_SIZE'],
            pool_maxsize=settings.ODOO_CONFIG['CONNECTION_POOL_SIZE']
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, 
                     headers: Dict = None, params: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to Odoo API"""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        default_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if headers:
            default_headers.update(headers)
        
        try:
            start_time = time.time()
            
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                headers=default_headers,
                params=params,
                timeout=self.timeout
            )
            
            response_time = time.time() - start_time
            
            logger.info(f"Odoo API {method} {endpoint} - Status: {response.status_code}, Time: {response_time:.3f}s")
            
            if response.status_code >= 400:
                error_msg = f"Odoo API error {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise OdooClientError(error_msg)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise OdooClientError(f"Request failed: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            raise OdooClientError(f"Invalid JSON response: {str(e)}")
    
    def list_records(self, model_name: str, token: str, database: str,
                    domain: List = None, fields: List = None, 
                    order: str = None, limit: int = None, offset: int = None) -> Dict[str, Any]:
        """List records from Odoo model"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        params = {}
        if domain:
            params['domain'] = json.dumps(domain)
        if fields:
            params['fields'] = ','.join(fields)
        if order:
            params['order'] = order
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        return self._make_request(
            method='GET',
            endpoint=f'/api/v1/{model_name}',
            headers=headers,
            params=params
        )
    
    def get_record(self, model_name: str, record_id: int, token: str, database: str,
                  fields: List = None) -> Dict[str, Any]:
        """Get a specific record from Odoo model"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        params = {}
        if fields:
            params['fields'] = ','.join(fields)
        
        return self._make_request(
            method='GET',
            endpoint=f'/api/v1/{model_name}/{record_id}',
            headers=headers,
            params=params
        )
    
    def create_record(self, model_name: str, data: Dict, token: str, database: str) -> Dict[str, Any]:
        """Create a new record in Odoo model"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request(
            method='POST',
            endpoint=f'/api/v1/{model_name}',
            data={'data': data},
            headers=headers
        )
    
    def update_record(self, model_name: str, record_id: int, data: Dict, 
                     token: str, database: str) -> Dict[str, Any]:
        """Update an existing record in Odoo model"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request(
            method='PUT',
            endpoint=f'/api/v1/{model_name}/{record_id}',
            data={'data': data},
            headers=headers
        )
    
    def delete_record(self, model_name: str, record_id: int, token: str, database: str) -> Dict[str, Any]:
        """Delete a record from Odoo model"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request(
            method='DELETE',
            endpoint=f'/api/v1/{model_name}/{record_id}',
            headers=headers
        )
    
    def profile_models(self, token: str, database: str, models: List = None) -> Dict[str, Any]:
        """Get model profiling information"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        params = {}
        if models:
            params['models'] = models
        
        return self._make_request(
            method='GET',
            endpoint='/api/_profile',
            headers=headers,
            params=params
        )
    
    def get_model_fields(self, model_name: str, token: str, database: str) -> Dict[str, Any]:
        """Get field information for a specific model"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request(
            method='GET',
            endpoint=f'/api/_profile/fields/{model_name}',
            headers=headers
        )
    
    def list_allowed_models(self, token: str, database: str) -> Dict[str, Any]:
        """List all models accessible to the user"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request('GET', 'api/models/', headers=headers)
    
    # Business Intelligence Methods
    def get_analytics_data(self, model_name: str, token: str, database: str, 
                          report_type: str = 'summary', filters: Dict = None, 
                          group_by: List = None, measures: List = None) -> Dict[str, Any]:
        """Get analytics data from Odoo model"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        data = {
            'model': model_name,
            'report_type': report_type,
            'filters': filters or {},
            'group_by': group_by or [],
            'measures': measures or []
        }
        
        return self._make_request('POST', 'api/analytics/data/', data=data, headers=headers)
    
    def execute_report(self, report_id: int, token: str, database: str, 
                      parameters: Dict = None, format: str = 'json') -> Dict[str, Any]:
        """Execute Odoo report"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        data = {
            'report_id': report_id,
            'parameters': parameters or {},
            'format': format
        }
        
        return self._make_request('POST', 'api/reports/execute/', data=data, headers=headers)
    
    def get_dashboard_data(self, dashboard_id: int, token: str, database: str) -> Dict[str, Any]:
        """Get dashboard widgets data"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request('GET', f'api/dashboards/{dashboard_id}/', headers=headers)
    
    def list_reports(self, token: str, database: str, model: str = None) -> Dict[str, Any]:
        """List available reports"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        params = {}
        if model:
            params['model'] = model
            
        return self._make_request('GET', 'api/reports/', headers=headers, params=params)
    
    def list_dashboards(self, token: str, database: str) -> Dict[str, Any]:
        """List available dashboards"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request('GET', 'api/dashboards/', headers=headers)
    
    # Workflow Methods
    def create_workflow(self, workflow_data: Dict, token: str, database: str) -> Dict[str, Any]:
        """Create automated action workflow"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request('POST', 'api/workflows/', data=workflow_data, headers=headers)
    
    def execute_workflow(self, workflow_id: int, token: str, database: str, 
                        context: Dict = None, record_ids: List = None) -> Dict[str, Any]:
        """Execute workflow"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        data = {
            'workflow_id': workflow_id,
            'context': context or {},
            'record_ids': record_ids or []
        }
        
        return self._make_request('POST', f'api/workflows/{workflow_id}/execute/', data=data, headers=headers)
    
    def list_workflows(self, token: str, database: str, model: str = None, 
                      active: bool = None) -> Dict[str, Any]:
        """List available workflows"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        params = {}
        if model:
            params['model'] = model
        if active is not None:
            params['active'] = active
            
        return self._make_request('GET', 'api/workflows/', headers=headers, params=params)
    
    def get_workflow(self, workflow_id: int, token: str, database: str) -> Dict[str, Any]:
        """Get workflow details"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request('GET', f'api/workflows/{workflow_id}/', headers=headers)
    
    def update_workflow(self, workflow_id: int, workflow_data: Dict, token: str, database: str) -> Dict[str, Any]:
        """Update workflow"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request('PUT', f'api/workflows/{workflow_id}/', data=workflow_data, headers=headers)
    
    def delete_workflow(self, workflow_id: int, token: str, database: str) -> Dict[str, Any]:
        """Delete workflow"""
        headers = {
            'Authorization': f'Bearer {token}',
            'X-Database': database
        }
        
        return self._make_request('DELETE', f'api/workflows/{workflow_id}/', headers=headers)


# Global Odoo client instance
odoo_client = OdooClient()
