import xmlrpc.client
import os
import importlib.util
from pathlib import Path

class OdooDiscoveryService:
    """Service for Odoo model discovery and dynamic API generation (spec-compliant)"""
    def __init__(self, odoo_url=None, common_client=None, object_client=None):
        self.odoo_url = odoo_url or 'http://localhost:8069'
        if common_client and object_client:
            self.common = common_client
            self.object = object_client
        else:
            self.common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.object = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')

    def discover_models(self, discovery_params: dict) -> dict:
        """
        Discover Odoo models and their metadata.
        Args:
            discovery_params (dict): Parameters for discovery (e.g., database, filters)
        Returns:
            dict: Discovered models and metadata
        """
        result = {'success': False, 'errors': [], 'models': {}}
        db_name = discovery_params.get('database')
        username = discovery_params.get('username', 'admin')
        password = discovery_params.get('password', 'admin123')
        
        try:
            # Handle both token and password authentication
            if len(password) > 50:  # Likely a token
                uid = self.common.authenticate(db_name, username, password, {})
            else:
                uid = self.common.authenticate(db_name, username, password, {})
            
            if not uid:
                result['errors'].append('Authentication failed')
                return result
        except Exception as e:
            result['errors'].append(f'Authentication failed: {e}')
            return result
            
        try:
            model_records = self.object.execute_kw(db_name, uid, password, 'ir.model', 'search_read', [[('id', '>', 0)]], {'fields': ['model', 'name']})
            for model in model_records:
                model_name = model['model']
                try:
                    fields = self.object.execute_kw(db_name, uid, password, model_name, 'fields_get', [], {'attributes': ['string', 'type', 'required']})
                except Exception:
                    fields = {}
                
                # Discover workflows and BI features for this model
                try:
                    workflows = self.discover_model_workflows(model_name, db_name, uid, password)
                except Exception as e:
                    import logging
                    logger = logging.getLogger('fayvad_core.discovery')
                    logger.warning(f"Workflow discovery failed for {model_name}: {e}")
                    workflows = {
                        'available_triggers': [],
                        'suggested_workflows': [],
                        'existing_workflows': []
                    }
                
                try:
                    bi_features = self.discover_model_bi_features(model_name, fields)
                except Exception as e:
                    import logging
                    logger = logging.getLogger('fayvad_core.discovery')
                    logger.warning(f"BI feature discovery failed for {model_name}: {e}")
                    bi_features = {
                        'available_kpis': [],
                        'suggested_dashboards': [],
                        'reporting_capabilities': []
                    }
                
                result['models'][model_name] = {
                    'display_name': model['name'], 
                    'fields': fields,
                    'workflows': workflows,
                    'bi_features': bi_features
                }
        except Exception as e:
            result['errors'].append(f'Model discovery failed: {e}')
            return result
            
        result['success'] = len(result['errors']) == 0
        return result

    def discover_model_workflows(self, model_name: str, db_name: str, uid: int, password: str) -> dict:
        """
        Discover applicable workflows for a model.
        """
        workflows = {
            'available_triggers': [],
            'suggested_workflows': [],
            'existing_workflows': []
        }
        
        try:
            # Check for existing server actions (Odoo's built-in workflows)
            server_actions = self.object.execute_kw(
                db_name, uid, password, 'ir.actions.server', 'search_read',
                [[('model_id.model', '=', model_name)]],
                {'fields': ['name', 'state', 'model_id']}
            )
            
            if server_actions:
                try:
                    workflows['existing_workflows'] = [
                        {
                            'name': action['name'],
                            'type': 'server_action',
                            'state': action['state']
                        }
                        for action in server_actions
                    ]
                except Exception as e:
                    import logging
                    logger = logging.getLogger('fayvad_core.discovery')
                    logger.warning(f"Error processing server actions for {model_name}: {e}")
                    workflows['existing_workflows'] = []
            
            # Suggest common workflows based on model characteristics
            workflows['suggested_workflows'] = self.suggest_workflows_for_model(model_name)
            
            # Determine available triggers
            workflows['available_triggers'] = self.get_available_triggers(model_name)
            
        except Exception as e:
            # If discovery fails, return basic suggestions
            workflows['suggested_workflows'] = self.suggest_workflows_for_model(model_name)
            workflows['available_triggers'] = self.get_available_triggers(model_name)
            # Log the error for debugging
            import logging
            logger = logging.getLogger('fayvad_core.discovery')
            logger.warning(f"Workflow discovery failed for {model_name}: {e}")
            logger.warning(f"Error type: {type(e)}, Error details: {str(e)}")
        
        return workflows

    def discover_model_bi_features(self, model_name: str, fields: dict) -> dict:
        """
        Discover BI features applicable to a model.
        """
        bi_features = {
            'available_kpis': [],
            'suggested_dashboards': [],
            'reporting_capabilities': []
        }
        
        # Analyze fields to determine BI capabilities
        numeric_fields = []
        date_fields = []
        relation_fields = []
        
        for field_name, field_info in fields.items():
            field_type = field_info.get('type', '')
            
            if field_type in ['integer', 'float', 'monetary']:
                numeric_fields.append(field_name)
            elif field_type in ['date', 'datetime']:
                date_fields.append(field_name)
            elif field_type in ['many2one', 'many2many', 'one2many']:
                relation_fields.append(field_name)
        
        # Generate KPIs based on numeric fields
        bi_features['available_kpis'] = self.generate_kpis_for_model(model_name, numeric_fields)
        
        # Suggest dashboards based on model characteristics
        bi_features['suggested_dashboards'] = self.suggest_dashboards_for_model(model_name, fields)
        
        # Determine reporting capabilities
        bi_features['reporting_capabilities'] = self.get_reporting_capabilities(model_name, fields)
        
        return bi_features

    def suggest_workflows_for_model(self, model_name: str) -> list:
        """
        Suggest common workflows based on model name and characteristics.
        """
        suggestions = []
        
        # Common workflow patterns based on model prefixes
        if model_name.startswith('hr.'):
            if 'employee' in model_name:
                suggestions.extend([
                    {
                        'name': 'Employee Onboarding',
                        'description': 'Automated employee onboarding process',
                        'trigger_type': 'on_create',
                        'states': ['draft', 'document_collection', 'system_setup', 'active']
                    },
                    {
                        'name': 'Employee Offboarding',
                        'description': 'Automated employee offboarding process',
                        'trigger_type': 'on_state_change',
                        'states': ['active', 'notice_period', 'exit_interview', 'terminated']
                    }
                ])
            elif 'leave' in model_name:
                suggestions.extend([
                    {
                        'name': 'Leave Request Approval',
                        'description': 'Automated leave request approval workflow',
                        'trigger_type': 'on_create',
                        'states': ['draft', 'pending_approval', 'approved', 'rejected']
                    }
                ])
            elif 'expense' in model_name:
                suggestions.extend([
                    {
                        'name': 'Expense Report Approval',
                        'description': 'Automated expense report approval workflow',
                        'trigger_type': 'on_create',
                        'states': ['draft', 'submitted', 'approved', 'paid']
                    }
                ])
        
        elif model_name.startswith('crm.'):
            if 'lead' in model_name:
                suggestions.extend([
                    {
                        'name': 'Lead Qualification',
                        'description': 'Automated lead qualification process',
                        'trigger_type': 'on_create',
                        'states': ['new', 'contacted', 'qualified', 'converted']
                    }
                ])
            elif 'opportunity' in model_name:
                suggestions.extend([
                    {
                        'name': 'Opportunity Management',
                        'description': 'Automated opportunity management workflow',
                        'trigger_type': 'on_create',
                        'states': ['draft', 'qualified', 'proposal', 'negotiation', 'won']
                    }
                ])
        
        elif model_name.startswith('sale.'):
            if 'order' in model_name:
                suggestions.extend([
                    {
                        'name': 'Sales Order Approval',
                        'description': 'Automated sales order approval workflow',
                        'trigger_type': 'on_create',
                        'states': ['draft', 'pending_approval', 'confirmed', 'delivered']
                    }
                ])
        
        elif model_name.startswith('purchase.'):
            if 'order' in model_name:
                suggestions.extend([
                    {
                        'name': 'Purchase Order Approval',
                        'description': 'Automated purchase order approval workflow',
                        'trigger_type': 'on_create',
                        'states': ['draft', 'pending_approval', 'confirmed', 'received']
                    }
                ])
        
        # Generic workflows for any model
        suggestions.extend([
            {
                'name': 'Record Approval',
                'description': 'Generic approval workflow for any record',
                'trigger_type': 'on_create',
                'states': ['draft', 'pending_approval', 'approved', 'rejected']
            },
            {
                'name': 'Status Tracking',
                'description': 'Generic status tracking workflow',
                'trigger_type': 'on_state_change',
                'states': ['draft', 'in_progress', 'completed', 'cancelled']
            }
        ])
        
        return suggestions

    def get_available_triggers(self, model_name: str) -> list:
        """
        Get available triggers for a model.
        """
        triggers = [
            {
                'type': 'on_create',
                'description': 'Trigger when record is created',
                'applicable': True
            },
            {
                'type': 'on_update',
                'description': 'Trigger when record is updated',
                'applicable': True
            },
            {
                'type': 'on_delete',
                'description': 'Trigger when record is deleted',
                'applicable': True
            },
            {
                'type': 'on_state_change',
                'description': 'Trigger when state field changes',
                'applicable': self.has_state_field(model_name)
            },
            {
                'type': 'scheduled',
                'description': 'Trigger on schedule (cron)',
                'applicable': True
            },
            {
                'type': 'manual',
                'description': 'Manual trigger',
                'applicable': True
            }
        ]
        
        return [t for t in triggers if t['applicable']]

    def has_state_field(self, model_name: str) -> bool:
        """
        Check if model has a state field.
        """
        # Common state field names
        state_fields = ['state', 'status', 'stage_id', 'phase']
        
        # This would need to be implemented with actual field discovery
        # For now, return True for models that commonly have states
        models_with_states = [
            'hr.employee', 'hr.leave', 'hr.expense',
            'crm.lead', 'crm.opportunity',
            'sale.order', 'purchase.order',
            'stock.picking', 'account.move'
        ]
        
        return model_name in models_with_states

    def generate_kpis_for_model(self, model_name: str, numeric_fields: list) -> list:
        """
        Generate KPIs based on numeric fields in the model.
        """
        kpis = []
        
        for field in numeric_fields:
            kpis.extend([
                {
                    'name': f'Total {field.replace("_", " ").title()}',
                    'description': f'Sum of {field}',
                    'calculation': 'sum',
                    'field': field
                },
                {
                    'name': f'Average {field.replace("_", " ").title()}',
                    'description': f'Average of {field}',
                    'calculation': 'average',
                    'field': field
                },
                {
                    'name': f'Count by {field.replace("_", " ").title()}',
                    'description': f'Count grouped by {field}',
                    'calculation': 'count',
                    'field': field
                }
            ])
        
        # Add common KPIs
        kpis.extend([
            {
                'name': 'Total Records',
                'description': 'Total number of records',
                'calculation': 'count',
                'field': 'id'
            },
            {
                'name': 'Records This Month',
                'description': 'Records created this month',
                'calculation': 'count',
                'field': 'create_date',
                'filter': 'this_month'
            }
        ])
        
        return kpis

    def suggest_dashboards_for_model(self, model_name: str, fields: dict) -> list:
        """
        Suggest dashboards based on model characteristics.
        """
        suggestions = []
        
        # Analyze model to suggest appropriate dashboards
        if model_name.startswith('hr.'):
            if 'employee' in model_name:
                suggestions.append({
                    'name': 'Employee Management',
                    'description': 'Employee statistics and management overview',
                    'type': 'management'
                })
            elif 'attendance' in model_name:
                suggestions.append({
                    'name': 'Attendance Overview',
                    'description': 'Attendance tracking and analytics',
                    'type': 'analytics'
                })
            elif 'expense' in model_name:
                suggestions.append({
                    'name': 'Expense Management',
                    'description': 'Expense tracking and approval overview',
                    'type': 'management'
                })
        
        elif model_name.startswith('crm.'):
            suggestions.append({
                'name': 'Sales Pipeline',
                'description': 'Lead and opportunity pipeline overview',
                'type': 'pipeline'
            })
        
        elif model_name.startswith('sale.'):
            suggestions.append({
                'name': 'Sales Performance',
                'description': 'Sales metrics and performance overview',
                'type': 'performance'
            })
        
        elif model_name.startswith('purchase.'):
            suggestions.append({
                'name': 'Procurement Overview',
                'description': 'Purchase order and procurement analytics',
                'type': 'analytics'
            })
        
        # Generic dashboard suggestions
        suggestions.extend([
            {
                'name': 'Overview Dashboard',
                'description': 'General overview of records and metrics',
                'type': 'overview'
            },
            {
                'name': 'Activity Dashboard',
                'description': 'Recent activity and timeline',
                'type': 'activity'
            }
        ])
        
        return suggestions

    def get_reporting_capabilities(self, model_name: str, fields: dict) -> list:
        """
        Determine reporting capabilities for a model.
        """
        capabilities = [
            {
                'type': 'list_report',
                'description': 'List view with filtering and sorting',
                'available': True
            },
            {
                'type': 'summary_report',
                'description': 'Summary statistics and aggregations',
                'available': len([f for f in fields.values() if f.get('type') in ['float', 'monetary']]) > 0
            },
            {
                'type': 'trend_analysis',
                'description': 'Time-based trend analysis',
                'available': len([f for f in fields.values() if f.get('type') in ['date', 'datetime']]) > 0
            },
            {
                'type': 'comparison_report',
                'description': 'Comparison between different periods or categories',
                'available': True
            }
        ]
        
        return capabilities

    def discover_and_generate_apis(self, discovery_params: dict) -> dict:
        """
        Discover Odoo models and generate APIs dynamically.
        Args:
            discovery_params (dict): Parameters including generate_apis flag
        Returns:
            dict: Discovery result with generated APIs
        """
        # First discover models
        discovery_result = self.discover_models(discovery_params)
        
        if not discovery_result['success']:
            return discovery_result
            
        # If generate_apis is requested, generate the APIs
        if discovery_params.get('generate_apis'):
            try:
                generated_apis = self.generate_dynamic_apis(discovery_result['models'], discovery_params)
                discovery_result['generated_apis'] = generated_apis
                discovery_result['message'] = f"Generated APIs for {len(generated_apis)} domains"
            except Exception as e:
                discovery_result['errors'].append(f'API generation failed: {e}')
                discovery_result['success'] = False
                
        return discovery_result

    def generate_dynamic_apis(self, models: dict, discovery_params: dict) -> dict:
        """
        Generate domain services and viewsets dynamically.
        Args:
            models (dict): Discovered models
            discovery_params (dict): Generation parameters
        Returns:
            dict: Generated API information
        """
        generated_apis = {}
        
        # Group models by domain
        domain_models = self.group_models_by_domain(models)
        
        for domain, model_list in domain_models.items():
            try:
                # Generate domain service
                service_file = self.generate_domain_service(domain, model_list)
                
                # Generate viewset
                viewset_file = self.generate_viewset(domain, model_list)
                
                # Generate endpoints
                endpoints = self.generate_endpoint_list(domain, model_list)
                
                generated_apis[domain] = {
                    'service_file': service_file,
                    'viewset_file': viewset_file,
                    'endpoints': endpoints,
                    'models': model_list
                }
                
            except Exception as e:
                # Log error but continue with other domains
                print(f"Error generating API for domain {domain}: {e}")
                continue
                
        return generated_apis

    def group_models_by_domain(self, models: dict) -> dict:
        """
        Group models by business domain based on model prefixes.
        """
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
        
        for model_name in models.keys():
            assigned = False
            for domain, prefixes in domain_mappings.items():
                if any(model_name.startswith(prefix) for prefix in prefixes):
                    if domain not in domain_models:
                        domain_models[domain] = []
                    domain_models[domain].append(model_name)
                    assigned = True
                    break
            
            # If not assigned to any specific domain, add to generic
            if not assigned:
                if 'generic' not in domain_models:
                    domain_models['generic'] = []
                domain_models['generic'].append(model_name)
        
        return domain_models

    def generate_domain_service(self, domain: str, model_list: list) -> str:
        """
        Generate a domain service file.
        """
        service_content = f'''"""
{domain.title()} Domain Service

Auto-generated service for {domain} domain models.
"""

from typing import Dict, Any, List
from ..services.odoo_client import odoo_client
import logging

logger = logging.getLogger('fayvad_core.{domain}')

class {domain.title()}Service:
    """Service for {domain} domain operations"""
    
    def __init__(self):
        self.odoo_client = odoo_client
    
    def get_{domain}_models(self) -> List[str]:
        """Get list of {domain} models"""
        return {model_list}
    
    def get_{domain}_summary(self, token: str, database: str) -> Dict[str, Any]:
        """Get {domain} domain summary"""
        summary = {{}}
        
        for model in self.get_{domain}_models():
            try:
                # Get record count for each model
                result = self.odoo_client.list_records(
                    model_name=model,
                    token=token,
                    database=database,
                    limit=1
                )
                
                if result.get('success'):
                    summary[model] = {{
                        'count': result.get('count', 0),
                        'available': True
                    }}
                else:
                    summary[model] = {{
                        'count': 0,
                        'available': False,
                        'error': result.get('error', 'Unknown error')
                    }}
                    
            except Exception as e:
                logger.error(f"Error getting summary for {{model}}: {{str(e)}}")
                summary[model] = {{
                    'count': 0,
                    'available': False,
                    'error': str(e)
                }}
        
        return summary
'''
        
        # Write service file
        service_dir = Path('fbs/fayvad_core/services')
        service_dir.mkdir(exist_ok=True)
        
        service_file = service_dir / f'{domain}_service.py'
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        return str(service_file)

    def generate_viewset(self, domain: str, model_list: list) -> str:
        """
        Generate a viewset file for the domain.
        """
        viewset_content = f'''"""
{domain.title()} ViewSet

Auto-generated viewset for {domain} domain.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..auth.drf_auth import JWTAuthentication
from ..services.odoo_client import odoo_client
import logging

logger = logging.getLogger('fayvad_core.{domain}')

class {domain.title()}ViewSet(viewsets.ViewSet):
    """ViewSet for {domain} domain operations"""
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.odoo_client = odoo_client
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get {domain} domain summary"""
        try:
            from ..services.{domain}_service import {domain.title()}Service
            
            service = {domain.title()}Service()
            summary = service.get_{domain}_summary(
                token=request.auth,
                database=request.GET.get('db')
            )
            
            return Response({{
                'success': True,
                'data': summary
            }})
            
        except Exception as e:
            logger.error(f"Error getting {domain} summary: {{str(e)}}")
            return Response({{
                'success': False,
                'error': str(e)
            }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def models(self, request):
        """Get available {domain} models"""
        try:
            from ..services.{domain}_service import {domain.title()}Service
            
            service = {domain.title()}Service()
            models = service.get_{domain}_models()
            
            return Response({{
                'success': True,
                'data': {{
                    'models': models,
                    'count': len(models)
                }}
            }})
            
        except Exception as e:
            logger.error(f"Error getting {domain} models: {{str(e)}}")
            return Response({{
                'success': False,
                'error': str(e)
            }}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
'''
        
        # Write viewset file
        viewset_dir = Path('fbs/fayvad_core/api')
        viewset_dir.mkdir(exist_ok=True)
        
        viewset_file = viewset_dir / f'{domain}_views.py'
        with open(viewset_file, 'w') as f:
            f.write(viewset_content)
        
        return str(viewset_file)

    def update_url_configuration(self, domain: str, model_list: list):
        """Update URL configuration for the domain"""
        # This would update the main URLs file to include the new viewset
        pass

    def generate_endpoint_list(self, domain: str, model_list: list) -> list:
        """Generate list of endpoints for the domain"""
        endpoints = [
            {
                'path': f'/api/{domain}/summary/',
                'method': 'GET',
                'description': f'Get {domain} domain summary'
            },
            {
                'path': f'/api/{domain}/models/',
                'method': 'GET',
                'description': f'Get available {domain} models'
            }
        ]
        
        # Add generic model endpoints for each model
        for model in model_list:
            model_name = model.replace('.', '_')
            endpoints.extend([
                {
                    'path': f'/api/v1/{model}/',
                    'method': 'GET',
                    'description': f'List {model} records'
                },
                {
                    'path': f'/api/v1/{model}/',
                    'method': 'POST',
                    'description': f'Create {model} record'
                },
                {
                    'path': f'/api/v1/{model}/<id>/',
                    'method': 'GET',
                    'description': f'Get {model} record'
                },
                {
                    'path': f'/api/v1/{model}/<id>/',
                    'method': 'PUT',
                    'description': f'Update {model} record'
                },
                {
                    'path': f'/api/v1/{model}/<id>/',
                    'method': 'DELETE',
                    'description': f'Delete {model} record'
                }
            ])
        
        return endpoints 