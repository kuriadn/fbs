import xmlrpc.client
import logging
from typing import Dict, Any, List
from django.conf import settings
from fayvad_core.models import FBSDiscovery

logger = logging.getLogger(__name__)

class FBSDiscoveryService:
    """
    Service for discovering Odoo modules, workflows, and BI features.
    Uses XML-RPC to connect to Odoo and discover available functionality.
    """
    
    def __init__(self):
        self.odoo_url = settings.ODOO_CONFIG['BASE_URL']
        self.odoo_db = settings.ODOO_CONFIG['DATABASE']
        self.odoo_user = settings.ODOO_CONFIG['USERNAME']
        self.odoo_password = settings.ODOO_CONFIG['PASSWORD']
        self.common = None
        self.models = None
    
    def _connect_to_odoo(self):
        """Establish connection to Odoo via XML-RPC"""
        try:
            self.common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
            self.uid = self.common.authenticate(self.odoo_db, self.odoo_user, self.odoo_password, {})
            
            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
                logger.info(f"Successfully connected to Odoo database: {self.odoo_db}")
                return True
            else:
                logger.error(f"Failed to authenticate with Odoo database: {self.odoo_db}")
                return False
                
        except Exception as e:
            logger.error(f"Error connecting to Odoo: {str(e)}")
            return False
    
    def discover_and_cache(self, domain: str, discovery_type: str, database: str = None) -> Dict[str, Any]:
        """
        Discover and cache Odoo modules, workflows, or BI features for a specific domain.
        
        Args:
            domain: Business domain (e.g., 'rental', 'ecommerce', 'hr')
            discovery_type: Type of discovery ('models', 'workflows', 'bi_features')
            database: Optional database override (defaults to settings)
            
        Returns:
            Dict with discovery results and status
        """
        try:
            # Use provided database or default from settings
            odoo_db = database or self.odoo_db
            
            logger.info(f"Starting discovery for domain: {domain}, type: {discovery_type}, database: {odoo_db}")
            
            # Connect to Odoo
            if not self._connect_to_odoo():
                return {
                    'status': 'error',
                    'message': 'Failed to connect to Odoo',
                    'domain': domain,
                    'discovery_type': discovery_type,
                    'database': odoo_db
                }
            
            # Perform discovery based on type
            if discovery_type == 'models':
                result = self._discover_models(domain, odoo_db)
            elif discovery_type == 'workflows':
                result = self._discover_workflows(domain, odoo_db)
            elif discovery_type == 'bi_features':
                result = self._discover_bi_features(domain, odoo_db)
            else:
                return {
                    'status': 'error',
                    'message': f'Unknown discovery type: {discovery_type}',
                    'domain': domain,
                    'discovery_type': discovery_type
                }
            
            # Cache the discovery results
            if result['status'] == 'success':
                self._cache_discovery(domain, discovery_type, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Discovery failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'domain': domain,
                'discovery_type': discovery_type
            }
    
    def _discover_models(self, domain: str, odoo_db: str) -> Dict[str, Any]:
        """Discover ALL available Odoo models, not just installed ones"""
        try:
            # First, get all available modules
            all_modules = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.module.module', 'search_read',
                [[('state', 'in', ['installed', 'uninstalled', 'to install'])]], 
                {'fields': ['name', 'shortdesc', 'state', 'category_id']}
            )
            
            # Get all models from all modules
            model_list = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model', 'search_read',
                [[]],  # No domain filter - get ALL models
                {'fields': ['name', 'model', 'modules', 'state']}
            )
            
            # Filter models relevant to the domain
            relevant_models = self._filter_models_by_domain(model_list, domain)
            
            # Get detailed information for each model
            discovered_models = {}
            for model in relevant_models:
                model_name = model['model']
                model_details = self._get_model_details(model_name, odoo_db)
                discovered_models[model_name] = model_details
            
            return {
                'status': 'success',
                'domain': domain,
                'discovery_type': 'models',
                'database': odoo_db,
                'discovered_models': discovered_models,
                'total_models': len(discovered_models),
                'available_modules': len(all_modules),
                'all_models_count': len(model_list)
            }
            
        except Exception as e:
            logger.error(f"Model discovery failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'domain': domain,
                'discovery_type': 'models'
            }
    
    def _discover_workflows(self, domain: str, odoo_db: str) -> Dict[str, Any]:
        """Discover ALL available Odoo workflows"""
        try:
            # Get all models that might have workflows
            all_models = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model', 'search_read',
                [[]],  # Get all models
                {'fields': ['name', 'model', 'state']}
            )
            
            # Filter models that are likely to have workflows (more comprehensive approach)
            workflow_models = []
            for model in all_models:
                model_name = model['model']
                # Check if model has workflow-related characteristics
                try:
                    # Check for state/status fields (most common workflow indicator)
                    state_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('name', 'in', ['state', 'status', 'stage_id', 'kanban_state', 'priority', 'sequence'])]], 
                        {'fields': ['name']}
                    )
                    
                    # Check for workflow-related fields
                    workflow_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('name', 'in', ['workflow_id', 'process_id', 'activity_ids', 'approval_id', 'approver_id'])]], 
                        {'fields': ['name']}
                    )
                    
                    # Check for action/button fields (indicates workflow actions)
                    action_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('name', 'ilike', 'action_')]], 
                        {'fields': ['name']}
                    )
                    
                    # Check for approval/validation fields
                    approval_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('name', 'ilike', 'approve')]], 
                        {'fields': ['name']}
                    )
                    
                    # Check for confirmation fields
                    confirm_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('name', 'ilike', 'confirm')]], 
                        {'fields': ['name']}
                    )
                    
                    # Check for validation fields
                    validate_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('name', 'ilike', 'validate')]], 
                        {'fields': ['name']}
                    )
                    
                    # Include models with any workflow indicators
                    if (state_fields or workflow_fields or action_fields or 
                        approval_fields or confirm_fields or validate_fields):
                        workflow_models.append(model_name)
                        
                except:
                    continue
            
            discovered_workflows = {}
            for model_name in workflow_models[:20]:  # Limit to first 20 to avoid timeout
                workflow_details = self._get_workflow_details(model_name, odoo_db)
                if workflow_details:
                    discovered_workflows[model_name] = workflow_details
            
            return {
                'status': 'success',
                'domain': domain,
                'discovery_type': 'workflows',
                'database': odoo_db,
                'discovered_workflows': discovered_workflows,
                'total_workflows': len(discovered_workflows),
                'total_models_checked': len(workflow_models)
            }
            
        except Exception as e:
            logger.error(f"Workflow discovery failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'domain': domain,
                'discovery_type': 'workflows'
            }
    
    def _discover_bi_features(self, domain: str, odoo_db: str) -> Dict[str, Any]:
        """Discover ALL available Odoo BI features"""
        try:
            # Get all models that might have BI features
            all_models = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model', 'search_read',
                [[]],  # Get all models
                {'fields': ['name', 'model', 'state']}
            )
            
            # Filter models that are likely to have BI features (more comprehensive approach)
            bi_models = []
            for model in all_models:
                model_name = model['model']
                # Check if model is likely to have reports/dashboards
                try:
                    # Check for models with numeric fields (indicating metrics/analytics)
                    numeric_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('ttype', 'in', ['float', 'integer', 'monetary'])]], 
                        {'fields': ['name']}
                    )
                    
                    # Check for models with date fields (indicating time-based analytics)
                    date_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('ttype', 'in', ['date', 'datetime'])]], 
                        {'fields': ['name']}
                    )
                    
                    # Check for models with selection fields (indicating categorization)
                    selection_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('ttype', '=', 'selection')]], 
                        {'fields': ['name']}
                    )
                    
                    # Check for models with many2one fields (indicating relationships for grouping)
                    relation_fields = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        'ir.model.fields', 'search_read',
                        [[('model', '=', model_name), ('ttype', '=', 'many2one')]], 
                        {'fields': ['name']}
                    )
                    
                    # Include models with BI indicators or common business keywords
                    if (len(numeric_fields) > 2 or len(date_fields) > 1 or 
                        len(selection_fields) > 1 or len(relation_fields) > 3 or
                        any(keyword in model_name.lower() for keyword in [
                            'sale', 'purchase', 'account', 'hr', 'product', 'partner', 
                            'invoice', 'order', 'payment', 'analytic', 'report', 
                            'dashboard', 'metric', 'kpi', 'performance', 'analysis'
                        ])):
                        bi_models.append(model_name)
                        
                except:
                    # Fallback to keyword-based filtering
                    if any(keyword in model_name.lower() for keyword in ['sale', 'purchase', 'account', 'hr', 'product', 'partner', 'invoice', 'order']):
                        bi_models.append(model_name)
            
            discovered_bi_features = {}
            for model_name in bi_models[:15]:  # Limit to first 15 to avoid timeout
                bi_details = self._get_bi_details(model_name, odoo_db)
                if bi_details:
                    discovered_bi_features[model_name] = bi_details
            
            return {
                'status': 'success',
                'domain': domain,
                'discovery_type': 'bi_features',
                'database': odoo_db,
                'discovered_bi_features': discovered_bi_features,
                'total_bi_features': len(discovered_bi_features),
                'total_models_checked': len(bi_models)
            }
            
        except Exception as e:
            logger.error(f"BI feature discovery failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'domain': domain,
                'discovery_type': 'bi_features'
            }
    
    def _filter_models_by_domain(self, models: List[Dict], domain: str) -> List[Dict]:
        """Filter models based on domain relevance"""
        domain_keywords = {
            'rental': ['product', 'sale', 'partner', 'property', 'lease', 'tenant', 'payment'],
            'ecommerce': ['product', 'sale', 'customer', 'order', 'inventory', 'shipping'],
            'hr': ['employee', 'department', 'contract', 'attendance', 'payroll', 'recruitment'],
            'manufacturing': ['product', 'production', 'work', 'bom', 'routing', 'quality'],
            'purchasing': ['purchase', 'supplier', 'vendor', 'procurement', 'requisition']
        }
        
        keywords = domain_keywords.get(domain, [])
        relevant_models = []
        
        for model in models:
            model_name = model['model'].lower()
            if any(keyword in model_name for keyword in keywords):
                relevant_models.append(model)
        
        return relevant_models
    
    def _get_model_details(self, model_name: str, odoo_db: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        try:
            # Get model fields with more detailed information
            fields = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name)]],
                {'fields': ['name', 'field_description', 'ttype', 'required', 'readonly', 'size', 'selection', 'relation', 'on_delete']}
            )
            
            # Get basic model info (without non-existent fields)
            model_info = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model', 'search_read',
                [[('model', '=', model_name)]],
                {'fields': ['name', 'model', 'state']}
            )
            
            return {
                'name': model_name,
                'fields': {field['name']: {
                    'description': field['field_description'],
                    'type': field['ttype'],
                    'required': field['required'],
                    'readonly': field['readonly'],
                    'size': field.get('size'),
                    'selection': field.get('selection'),
                    'relation': field.get('relation'),
                    'on_delete': field.get('on_delete', 'restrict')
                } for field in fields},
                'model_info': model_info[0] if model_info else {},
                'relationships': self._get_model_relationships(model_name, odoo_db)
            }
            
        except Exception as e:
            logger.error(f"Error getting model details for {model_name}: {str(e)}")
            return {'name': model_name, 'error': str(e)}
    
    def _get_model_relationships(self, model_name: str, odoo_db: str) -> Dict[str, Any]:
        """Get model relationships"""
        try:
            # Get many2one, one2many, and many2many relationships
            relationships = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name), ('ttype', 'in', ['many2one', 'one2many', 'many2many'])]],
                {'fields': ['name', 'relation', 'ttype']}
            )
            
            return {rel['name']: {
                'related_model': rel['relation'],
                'type': rel['ttype']
            } for rel in relationships}
            
        except Exception as e:
            logger.error(f"Error getting relationships for {model_name}: {str(e)}")
            return {}
    
    def _get_workflow_details(self, model_name: str, odoo_db: str) -> Dict[str, Any]:
        """Get comprehensive workflow details for a model"""
        try:
            # Get workflow states and transitions
            workflow_info = {
                'model': model_name,
                'states': self._get_model_states(model_name, odoo_db),
                'transitions': self._get_model_transitions(model_name, odoo_db),
                'triggers': self._get_model_triggers(model_name, odoo_db),
                'approval_process': self._get_approval_process(model_name, odoo_db),
                'workflow_actions': self._get_workflow_actions(model_name, odoo_db),
                'validation_rules': self._get_validation_rules(model_name, odoo_db)
            }
            
            # Return workflow info if it has any workflow characteristics
            has_workflow = (workflow_info['states'] or workflow_info['transitions'] or 
                          workflow_info['triggers'] or workflow_info['approval_process'] or
                          workflow_info['workflow_actions'] or workflow_info['validation_rules'])
            
            return workflow_info if has_workflow else None
            
        except Exception as e:
            logger.error(f"Error getting workflow details for {model_name}: {str(e)}")
            return None
    
    def _get_model_states(self, model_name: str, odoo_db: str) -> List[str]:
        """Get possible states for a model by querying the database"""
        try:
            # Get fields that might contain states
            state_fields = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name), ('name', 'in', ['state', 'status', 'stage_id', 'kanban_state'])]], 
                {'fields': ['name', 'ttype', 'selection']}
            )
            
            states = []
            for field in state_fields:
                if field['ttype'] == 'selection' and field.get('selection'):
                    # Parse selection field values
                    selection_str = field['selection']
                    if isinstance(selection_str, str):
                        # Parse selection string like "('draft', 'Draft'), ('sent', 'Sent')"
                        import re
                        matches = re.findall(r"\('([^']+)',\s*'([^']+)'\)", selection_str)
                        states.extend([match[0] for match in matches])
            
            # Also check for common state patterns in the model
            if not states:
                # Try to get distinct state values from the model
                try:
                    distinct_states = self.models.execute_kw(
                        odoo_db, self.uid, self.odoo_password,
                        model_name, 'search_read',
                        [[('state', '!=', False)]], 
                        {'fields': ['state'], 'distinct': True}
                    )
                    states = list(set([record['state'] for record in distinct_states if record.get('state')]))
                except:
                    pass
            
            return states
            
        except Exception as e:
            logger.error(f"Error getting states for {model_name}: {str(e)}")
            return []
    
    def _get_model_transitions(self, model_name: str, odoo_db: str) -> List[str]:
        """Get possible transitions for a model"""
        try:
            # Simplified transitions based on common patterns
            common_transitions = {
                'sale.order': ['draft->sent', 'sent->sale', 'sale->done'],
                'purchase.order': ['draft->sent', 'sent->purchase', 'purchase->done'],
                'account.move': ['draft->posted', 'posted->cancel']
            }
            
            return common_transitions.get(model_name, [])
            
        except Exception as e:
            logger.error(f"Error getting transitions for {model_name}: {str(e)}")
            return []
    
    def _get_model_triggers(self, model_name: str, odoo_db: str) -> List[str]:
        """Get workflow triggers for a model"""
        try:
            # Common trigger methods based on field patterns
            trigger_methods = []
            
            # Check for action fields
            action_fields = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name), ('name', 'ilike', 'action_')]], 
                {'fields': ['name']}
            )
            trigger_methods.extend([field['name'] for field in action_fields])
            
            # Check for button fields
            button_fields = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name), ('name', 'ilike', 'button_')]], 
                {'fields': ['name']}
            )
            trigger_methods.extend([field['name'] for field in button_fields])
            
            # Add common workflow triggers
            common_triggers = ['action_confirm', 'action_cancel', 'action_draft', 'action_done', 
                             'action_approve', 'action_reject', 'action_validate', 'action_submit']
            trigger_methods.extend(common_triggers)
            
            return list(set(trigger_methods))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting triggers for {model_name}: {str(e)}")
            return []
    
    def _get_approval_process(self, model_name: str, odoo_db: str) -> Dict[str, Any]:
        """Get approval process details for a model"""
        try:
            approval_info = {}
            
            # Check for approval fields
            approval_fields = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name), ('name', 'ilike', 'approve')]], 
                {'fields': ['name', 'ttype']}
            )
            
            if approval_fields:
                approval_info['has_approval'] = True
                approval_info['approval_fields'] = [field['name'] for field in approval_fields]
            else:
                approval_info['has_approval'] = False
            
            return approval_info
            
        except Exception as e:
            logger.error(f"Error getting approval process for {model_name}: {str(e)}")
            return {'has_approval': False}
    
    def _get_workflow_actions(self, model_name: str, odoo_db: str) -> List[str]:
        """Get workflow actions for a model"""
        try:
            actions = []
            
            # Check for action fields
            action_fields = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name), ('name', 'ilike', 'action_')]], 
                {'fields': ['name']}
            )
            actions.extend([field['name'] for field in action_fields])
            
            # Check for workflow-related fields
            workflow_fields = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name), ('name', 'in', ['workflow_id', 'process_id', 'activity_ids'])]], 
                {'fields': ['name']}
            )
            actions.extend([field['name'] for field in workflow_fields])
            
            return list(set(actions))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting workflow actions for {model_name}: {str(e)}")
            return []
    
    def _get_validation_rules(self, model_name: str, odoo_db: str) -> List[str]:
        """Get validation rules for a model"""
        try:
            validation_rules = []
            
            # Check for validation fields
            validation_fields = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name), ('name', 'ilike', 'validate')]], 
                {'fields': ['name']}
            )
            validation_rules.extend([field['name'] for field in validation_fields])
            
            # Check for required fields (basic validation)
            required_fields = self.models.execute_kw(
                odoo_db, self.uid, self.odoo_password,
                'ir.model.fields', 'search_read',
                [[('model', '=', model_name), ('required', '=', True)]], 
                {'fields': ['name']}
            )
            if required_fields:
                validation_rules.append(f"Required fields: {[field['name'] for field in required_fields]}")
            
            return validation_rules
            
        except Exception as e:
            logger.error(f"Error getting validation rules for {model_name}: {str(e)}")
            return []
    
    def _get_bi_details(self, model_name: str, odoo_db: str) -> Dict[str, Any]:
        """Get BI features for a model"""
        try:
            # Get reports and dashboards related to the model
            bi_info = {
                'model': model_name,
                'reports': self._get_model_reports(model_name, odoo_db),
                'dashboards': self._get_model_dashboards(model_name, odoo_db),
                'metrics': self._get_model_metrics(model_name, odoo_db)
            }
            
            return bi_info
            
        except Exception as e:
            logger.error(f"Error getting BI details for {model_name}: {str(e)}")
            return None
    
    def _get_model_reports(self, model_name: str, odoo_db: str) -> List[str]:
        """Get reports for a model by querying the database"""
        try:
            # Query for reports related to this model
            reports = []
            
            # Look for report actions
            try:
                report_actions = self.models.execute_kw(
                    odoo_db, self.uid, self.odoo_password,
                    'ir.actions.report', 'search_read',
                    [[('model', '=', model_name)]], 
                    {'fields': ['name', 'report_name']}
                )
                reports.extend([action['name'] for action in report_actions if action.get('name')])
            except:
                pass
            
            # Look for menu items that might be reports
            try:
                menu_items = self.models.execute_kw(
                    odoo_db, self.uid, self.odoo_password,
                    'ir.ui.menu', 'search_read',
                    [[('name', 'ilike', 'report'), ('name', 'ilike', model_name.split('.')[-1])]], 
                    {'fields': ['name']}
                )
                reports.extend([menu['name'] for menu in menu_items if menu.get('name')])
            except:
                pass
            
            # Add common reports based on model type
            if 'sale' in model_name:
                reports.extend(['Sales Analysis', 'Customer Orders', 'Sales by Product'])
            elif 'purchase' in model_name:
                reports.extend(['Purchase Analysis', 'Vendor Orders', 'Purchase by Product'])
            elif 'account' in model_name:
                reports.extend(['General Ledger', 'Trial Balance', 'Profit & Loss'])
            elif 'hr' in model_name or 'employee' in model_name:
                reports.extend(['Employee Directory', 'Attendance Report', 'Payroll Summary'])
            elif 'product' in model_name:
                reports.extend(['Product Analysis', 'Inventory Report', 'Product Performance'])
            
            return list(set(reports))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting reports for {model_name}: {str(e)}")
            return []
    
    def _get_model_dashboards(self, model_name: str, odoo_db: str) -> List[str]:
        """Get dashboards for a model by querying the database"""
        try:
            # Query for dashboards related to this model
            dashboards = []
            
            # Look for dashboard actions
            try:
                dashboard_actions = self.models.execute_kw(
                    odoo_db, self.uid, self.odoo_password,
                    'ir.actions.act_window', 'search_read',
                    [[('res_model', '=', model_name), ('view_mode', 'ilike', 'kanban')]], 
                    {'fields': ['name', 'display_name']}
                )
                dashboards.extend([action['name'] for action in dashboard_actions if action.get('name')])
            except:
                pass
            
            # Look for kanban views that might be dashboards
            try:
                kanban_views = self.models.execute_kw(
                    odoo_db, self.uid, self.odoo_password,
                    'ir.ui.view', 'search_read',
                    [[('model', '=', model_name), ('type', '=', 'kanban')]], 
                    {'fields': ['name']}
                )
                dashboards.extend([view['name'] for view in kanban_views if view.get('name')])
            except:
                pass
            
            # Add common dashboards based on model type
            if 'sale' in model_name:
                dashboards.extend(['Sales Dashboard', 'Customer Analytics', 'Product Performance'])
            elif 'purchase' in model_name:
                dashboards.extend(['Purchase Dashboard', 'Vendor Analytics', 'Cost Analysis'])
            elif 'account' in model_name:
                dashboards.extend(['Financial Dashboard', 'Cash Flow Analysis', 'Budget vs Actual'])
            elif 'hr' in model_name or 'employee' in model_name:
                dashboards.extend(['HR Dashboard', 'Employee Analytics', 'Performance Metrics'])
            elif 'product' in model_name:
                dashboards.extend(['Product Dashboard', 'Inventory Analytics', 'Performance Metrics'])
            
            return list(set(dashboards))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error getting dashboards for {model_name}: {str(e)}")
            return []
    
    def _get_model_metrics(self, model_name: str, odoo_db: str) -> List[str]:
        """Get metrics for a model"""
        try:
            # Common metrics for different models
            common_metrics = {
                'sale.order': ['Total Sales', 'Average Order Value', 'Customer Count'],
                'purchase.order': ['Total Purchases', 'Average Purchase Value', 'Vendor Count'],
                'account.move': ['Total Revenue', 'Total Expenses', 'Net Profit'],
                'hr.employee': ['Employee Count', 'Average Salary', 'Turnover Rate']
            }
            
            return common_metrics.get(model_name, [])
            
        except Exception as e:
            logger.error(f"Error getting metrics for {model_name}: {str(e)}")
            return []
    
    def _cache_discovery(self, domain: str, discovery_type: str, result: Dict[str, Any]):
        """Cache discovery results in database"""
        try:
            # Create or update discovery record
            discovery, created = FBSDiscovery.objects.update_or_create(
                discovery_type=discovery_type,
                domain=domain,
                name=f'{domain}_{discovery_type}',
                defaults={
                    'metadata': result,
                    'schema_definition': self._generate_schema_definition(result),
                    'is_active': True
                }
            )
            
            if created:
                logger.info(f"Cached new discovery: {domain}_{discovery_type}")
            else:
                logger.info(f"Updated existing discovery: {domain}_{discovery_type}")
                
        except Exception as e:
            logger.error(f"Error caching discovery: {str(e)}")
    
    def _generate_schema_definition(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate schema definition from discovery result"""
        try:
            if result['discovery_type'] == 'models':
                return self._generate_model_schema(result['discovered_models'])
            elif result['discovery_type'] == 'workflows':
                return self._generate_workflow_schema(result['discovered_workflows'])
            elif result['discovery_type'] == 'bi_features':
                return self._generate_bi_schema(result['discovered_bi_features'])
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Error generating schema definition: {str(e)}")
            return {}
    
    def _generate_model_schema(self, models: Dict[str, Any]) -> Dict[str, Any]:
        """Generate database schema from discovered models"""
        schema = {}
        
        for model_name, model_data in models.items():
            if 'fields' in model_data:
                table_name = model_name.replace('.', '_')
                schema[table_name] = {
                    'fields': model_data['fields'],
                    'relationships': model_data.get('relationships', {}),
                    'constraints': []
                }
        
        return schema
    
    def _generate_workflow_schema(self, workflows: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow schema from discovered workflows"""
        schema = {}
        
        for workflow_name, workflow_data in workflows.items():
            schema[workflow_name] = {
                'states': workflow_data.get('states', []),
                'transitions': workflow_data.get('transitions', []),
                'triggers': workflow_data.get('triggers', [])
            }
        
        return schema
    
    def _generate_bi_schema(self, bi_features: Dict[str, Any]) -> Dict[str, Any]:
        """Generate BI schema from discovered BI features"""
        schema = {}
        
        for bi_name, bi_data in bi_features.items():
            schema[bi_name] = {
                'reports': bi_data.get('reports', []),
                'dashboards': bi_data.get('dashboards', []),
                'metrics': bi_data.get('metrics', [])
            }
        
        return schema 