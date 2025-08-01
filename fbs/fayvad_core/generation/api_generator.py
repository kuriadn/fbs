import logging
from typing import Dict, List, Any
from django.conf import settings
from .discovery import OdooDiscoveryService

logger = logging.getLogger(__name__)

class FBSAPIGenerator:
    """FBS API Generator that integrates with discovery system"""
    
    def __init__(self, solution_name: str, domain: str = None, db_credentials: dict = None):
        self.solution_name = solution_name
        self.domain = domain
        self.odoo_url = getattr(settings, 'ODOO_URL', 'http://localhost:8069')
        
        # Generate database name using FBS pattern
        self.database_name = f"fbs_{solution_name}_db"
        
        # Use provided credentials or defaults
        self.db_credentials = db_credentials or {
            'username': 'fayvad',
            'password': 'MeMiMo@0207'
        }
        
        # Initialize discovery service
        self.discovery_service = OdooDiscoveryService(self.odoo_url)
    
    def generate_all_apis(self, discovery_params: dict = None) -> Dict[str, Any]:
        """
        Generate all APIs for the solution based on discovered capabilities.
        
        Args:
            discovery_params: Optional parameters for discovery
            
        Returns:
            Dict with generated APIs and metadata
        """
        try:
            logger.info(f"Generating APIs for solution: {self.solution_name}")
            
            # Prepare discovery parameters
            if not discovery_params:
                discovery_params = {
                    'database': self.database_name,
                    'username': self.db_credentials['username'],
                    'password': self.db_credentials['password'],
                    'generate_apis': True,
                    'domain': self.domain
                }
            
            # Discover models and generate APIs
            result = self.discovery_service.discover_and_generate_apis(discovery_params)
            
            if result['success']:
                logger.info(f"✅ Successfully generated APIs for {len(result.get('generated_apis', {}))} domains")
                return {
                    'status': 'success',
                    'solution_name': self.solution_name,
                    'database': self.database_name,
                    'generated_apis': result.get('generated_apis', {}),
                    'models_discovered': len(result.get('models', {})),
                    'domains_generated': len(result.get('generated_apis', {})),
                    'message': result.get('message', 'API generation completed successfully')
                }
            else:
                logger.error(f"❌ API generation failed: {result.get('errors', [])}")
                return {
                    'status': 'error',
                    'solution_name': self.solution_name,
                    'errors': result.get('errors', []),
                    'message': 'API generation failed'
                }
                
        except Exception as e:
            logger.error(f"Error generating APIs: {str(e)}")
            return {
                'status': 'error',
                'solution_name': self.solution_name,
                'errors': [str(e)],
                'message': f'API generation failed: {str(e)}'
            }
    
    def generate_domain_apis(self, domain: str, models: List[str]) -> Dict[str, Any]:
        """
        Generate APIs for a specific domain.
        
        Args:
            domain: Business domain (e.g., 'sales', 'accounting')
            models: List of model names for this domain
            
        Returns:
            Dict with generated APIs for the domain
        """
        try:
            logger.info(f"Generating APIs for domain: {domain}")
            
            # Create domain-specific discovery parameters
            discovery_params = {
                'database': self.database_name,
                'username': self.db_credentials['username'],
                'password': self.db_credentials['password'],
                'generate_apis': True,
                'domain': domain,
                'model_filter': models
            }
            
            # Generate APIs for this domain
            result = self.discovery_service.generate_dynamic_apis(
                {model: {} for model in models},  # Convert to model dict format
                discovery_params
            )
            
            return {
                'status': 'success',
                'domain': domain,
                'generated_apis': result,
                'models': models,
                'message': f'Generated APIs for {domain} domain'
            }
            
        except Exception as e:
            logger.error(f"Error generating APIs for domain {domain}: {str(e)}")
            return {
                'status': 'error',
                'domain': domain,
                'errors': [str(e)],
                'message': f'API generation failed for {domain}: {str(e)}'
            }
    
    def get_api_endpoints(self, domain: str = None) -> List[Dict[str, Any]]:
        """
        Get list of available API endpoints.
        
        Args:
            domain: Optional domain filter
            
        Returns:
            List of API endpoints
        """
        try:
            # First generate APIs if not already done
            api_result = self.generate_all_apis()
            
            if api_result['status'] != 'success':
                return []
            
            generated_apis = api_result.get('generated_apis', {})
            endpoints = []
            
            for api_domain, api_data in generated_apis.items():
                if domain and api_domain != domain:
                    continue
                    
                domain_endpoints = api_data.get('endpoints', [])
                for endpoint in domain_endpoints:
                    endpoint['domain'] = api_domain
                    endpoints.append(endpoint)
            
            return endpoints
            
        except Exception as e:
            logger.error(f"Error getting API endpoints: {str(e)}")
            return []
    
    def generate_apis_from_fbs_discovery(self) -> Dict[str, Any]:
        """
        Generate APIs using the existing FBS discovery system.
        This method uses the already discovered models from FBS instead of
        connecting directly to Odoo.
        
        Returns:
            Dict with generated APIs and metadata
        """
        try:
            logger.info(f"Generating APIs from FBS discovery for solution: {self.solution_name}")
            
            # Import FBS discovery service
            from fayvad_core.discovery.integration_service import FBSAPIIntegrationService
            from fayvad_core.discovery.services import FBSDiscoveryService
            
            # Get discovery service
            discovery_service = FBSDiscoveryService()
            
            # Get discovered models from FBS cache
            from fayvad_core.models import FBSDiscovery
            
            # Query cached discoveries from database
            cached_discoveries = FBSDiscovery.objects.filter(
                domain=self.domain or 'general',
                discovery_type='models',
                is_active=True
            ).order_by('-created_at').first()
            
            if not cached_discoveries:
                return {
                    'status': 'error',
                    'solution_name': self.solution_name,
                    'errors': ['No models found in FBS discovery cache'],
                    'message': 'No models available for API generation'
                }
            
            # Parse the cached discovery data
            models_discovery = {
                'discovered_models': cached_discoveries.metadata.get('discovered_models', {})
            }
            
            if not models_discovery or 'discovered_models' not in models_discovery:
                return {
                    'status': 'error',
                    'solution_name': self.solution_name,
                    'errors': ['No models found in FBS discovery cache'],
                    'message': 'No models available for API generation'
                }
            
            discovered_models = models_discovery['discovered_models']
            
            # Group models by domain
            domain_models = self._group_models_by_domain(discovered_models)
            
            # Generate APIs for each domain
            generated_apis = {}
            for domain, models in domain_models.items():
                try:
                    # Generate domain service
                    service_file = self._generate_domain_service(domain, models)
                    
                    # Generate viewset
                    viewset_file = self._generate_viewset(domain, models)
                    
                    # Generate endpoints
                    endpoints = self._generate_endpoint_list(domain, models)
                    
                    generated_apis[domain] = {
                        'service_file': service_file,
                        'viewset_file': viewset_file,
                        'endpoints': endpoints,
                        'models': list(models.keys())
                    }
                    
                except Exception as e:
                    logger.error(f"Error generating API for domain {domain}: {e}")
                    continue
            
            return {
                'status': 'success',
                'solution_name': self.solution_name,
                'database': self.database_name,
                'generated_apis': generated_apis,
                'models_discovered': len(discovered_models),
                'domains_generated': len(generated_apis),
                'message': f'Generated APIs for {len(generated_apis)} domains from FBS discovery'
            }
            
        except Exception as e:
            logger.error(f"Error generating APIs from FBS discovery: {str(e)}")
            return {
                'status': 'error',
                'solution_name': self.solution_name,
                'errors': [str(e)],
                'message': f'API generation from FBS discovery failed: {str(e)}'
            }
    
    def _group_models_by_domain(self, models: dict) -> dict:
        """Group models by business domain based on model prefixes."""
        domain_mappings = {
            'sales': ['sale.', 'crm.'],
            'accounting': ['account.', 'payment.'],
            'inventory': ['stock.', 'product.'],
            'manufacturing': ['mrp.', 'quality.'],
            'hr': ['hr.', 'resource.'],
            'purchasing': ['purchase.', 'vendor.'],
            'project': ['project.'],
            'calendar': ['calendar.'],
            'crm': ['crm.'],
            'website': ['website.'],
            'helpdesk': ['helpdesk.'],
            'fleet': ['fleet.'],
            'maintenance': ['maintenance.'],
            'timesheet': ['hr_timesheet.'],
            'expense': ['hr_expense.'],
            'recruitment': ['hr_recruitment.'],
            'attendance': ['hr_attendance.'],
            'payroll': ['hr_payroll.'],
            'knowledge': ['knowledge.'],
            'survey': ['survey.'],
            'gamification': ['gamification.'],
            'social': ['social.'],
            'livechat': ['im_livechat.'],
            'discuss': ['mail.'],
            'notes': ['note.'],
            'contacts': ['res.partner'],
            'users': ['res.users'],
            'companies': ['res.company'],
            'settings': ['res.config'],
            'generic': ['ir.', 'base.']  # Generic models
        }
        
        domain_models = {}
        
        for model_name, model_data in models.items():
            assigned_domain = 'generic'  # Default domain
            
            for domain, prefixes in domain_mappings.items():
                if any(model_name.startswith(prefix) for prefix in prefixes):
                    assigned_domain = domain
                    break
            
            if assigned_domain not in domain_models:
                domain_models[assigned_domain] = {}
            
            domain_models[assigned_domain][model_name] = model_data
        
        return domain_models
    
    def _generate_domain_service(self, domain: str, models: dict) -> str:
        """Generate domain service file content."""
        service_content = f"""# Generated Domain Service for {domain}
from typing import Dict, List, Any
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

class {domain.title()}Service:
    \"\"\"Service for {domain} domain operations\"\"\"
    
    def __init__(self):
        self.models = {list(models.keys())}
    
    def get_models(self) -> List[str]:
        \"\"\"Get available models in this domain\"\"\"
        return self.models
    
    def get_model_data(self, model_name: str) -> Dict[str, Any]:
        \"\"\"Get model data and fields\"\"\"
        if model_name in self.models:
            return self.models[model_name]
        return {{}}
"""
        return service_content
    
    def _generate_viewset(self, domain: str, models: dict) -> str:
        """Generate viewset file content."""
        viewset_content = f"""# Generated ViewSet for {domain}
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class {domain.title()}ViewSet(viewsets.ViewSet):
    \"\"\"ViewSet for {domain} domain\"\"\"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.models = {list(models.keys())}
    
    @action(detail=False, methods=['get'])
    def models(self, request):
        \"\"\"Get available models\"\"\"
        return Response({{
            'domain': '{domain}',
            'models': self.models,
            'count': len(self.models)
        }})
    
    @action(detail=False, methods=['get'])
    def capabilities(self, request):
        \"\"\"Get domain capabilities\"\"\"
        return Response({{
            'domain': '{domain}',
            'capabilities': {{
                'models': len(self.models),
                'operations': ['list', 'retrieve', 'create', 'update', 'delete']
            }}
        }})
"""
        return viewset_content
    
    def _generate_endpoint_list(self, domain: str, models: dict) -> list:
        """Generate list of API endpoints."""
        endpoints = []
        
        # Base endpoints
        endpoints.extend([
            {
                'method': 'GET',
                'url': f'/api/{domain}/models/',
                'description': f'Get available models in {domain} domain'
            },
            {
                'method': 'GET',
                'url': f'/api/{domain}/capabilities/',
                'description': f'Get {domain} domain capabilities'
            }
        ])
        
        # Model-specific endpoints
        for model_name in models.keys():
            model_slug = model_name.replace('.', '_')
            endpoints.extend([
                {
                    'method': 'GET',
                    'url': f'/api/{domain}/{model_slug}/',
                    'description': f'List {model_name} records'
                },
                {
                    'method': 'POST',
                    'url': f'/api/{domain}/{model_slug}/',
                    'description': f'Create new {model_name} record'
                },
                {
                    'method': 'GET',
                    'url': f'/api/{domain}/{model_slug}/<id>/',
                    'description': f'Get {model_name} record by ID'
                },
                {
                    'method': 'PUT',
                    'url': f'/api/{domain}/{model_slug}/<id>/',
                    'description': f'Update {model_name} record'
                },
                {
                    'method': 'DELETE',
                    'url': f'/api/{domain}/{model_slug}/<id>/',
                    'description': f'Delete {model_name} record'
                }
            ])
        
        return endpoints

class UnifiedAPIGenerator:
    """Single generator for all business domain APIs (scaffold)"""
    def __init__(self, discovery_client):
        self.discovery = discovery_client 