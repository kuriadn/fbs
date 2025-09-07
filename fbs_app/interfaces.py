"""
FBS App Service Interfaces

This module provides clean interfaces to all FBS app capabilities,
replacing the previous API endpoint approach with proper service-based access.

Usage:
    from fbs_app.interfaces import FBSInterface
    
    # Initialize with solution context
    fbs = FBSInterface('solution_name')
    
    # Access MSME capabilities
    dashboard = fbs.msme.get_dashboard()
    kpis = fbs.msme.calculate_kpis()
    
    # Access accounting capabilities
    ledger = fbs.accounting.get_basic_ledger()
    entry = fbs.accounting.create_cash_entry(amount=100, type='income')
    
    # Access business intelligence
    reports = fbs.bi.generate_reports()
    charts = fbs.bi.get_charts()
    
    # Access workflow management
    workflows = fbs.workflows.get_active_workflows()
    approval = fbs.workflows.create_approval_request()
    
    # Access compliance management
    compliance = fbs.compliance.get_compliance_status()
    audit = fbs.compliance.create_audit_trail()
    
    # Access notifications
    alerts = fbs.notifications.get_active_alerts()
    settings = fbs.notifications.update_settings()
    
    # Access Odoo integration
    models = fbs.odoo.discover_models()
    records = fbs.odoo.get_records('res.partner')
    
    # Access virtual fields
    custom_data = fbs.fields.get_custom_fields('res.partner', 1)
    fbs.fields.set_custom_field('res.partner', 1, 'custom_field', 'value')
"""

from typing import Dict, Any, Optional, List
from django.utils import timezone
import logging

logger = logging.getLogger('fbs_app')


class MSMEInterface:
    """Interface for MSME-specific operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.msme_service import MSMEService
        self._service = MSMEService(solution_name)
    
    def setup_business(self, business_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup MSME business"""
        return self._service.setup_msme_business(business_type, config)
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get MSME dashboard data"""
        return self._service.get_analytics_summary()
    
    def calculate_kpis(self) -> Dict[str, Any]:
        """Calculate MSME KPIs"""
        return self._service.get_business_kpis()
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status"""
        return self._service.get_compliance_status()
    
    def update_business_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update business profile"""
        return self._service.update_business_profile(profile_data)
    
    def get_marketing_data(self) -> Dict[str, Any]:
        """Get marketing data"""
        return self._service.get_marketing_data()
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        return self._service.get_analytics_summary()
    
    def create_custom_field(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom field"""
        return self._service.create_custom_field(field_data)
    
    def get_business_templates(self) -> Dict[str, Any]:
        """Get business templates"""
        return self._service.get_business_templates()
    
    def apply_business_template(self, template_name: str) -> Dict[str, Any]:
        """Apply business template"""
        return self._service.apply_business_template(template_name)
    
    def get_setup_wizard_status(self) -> Dict[str, Any]:
        """Get setup wizard status"""
        return self._service.get_setup_wizard_status()
    
    def update_setup_wizard_step(self, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update setup wizard step"""
        return self._service.update_setup_wizard_step(step_name, step_data)


class BusinessIntelligenceInterface:
    """Interface for Business Intelligence and Analytics operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.bi_service import BusinessIntelligenceService
        self._service = BusinessIntelligenceService(solution_name)
    
    def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dashboard"""
        return self._service.create_dashboard(dashboard_data)
    
    def get_dashboards(self, dashboard_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all dashboards or by type"""
        return self._service.get_dashboards(dashboard_type)
    
    def update_dashboard(self, dashboard_id: int, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update dashboard"""
        return self._service.update_dashboard(dashboard_id, dashboard_data)
    
    def delete_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        """Delete dashboard"""
        return self._service.delete_dashboard(dashboard_id)
    
    def create_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report"""
        return self._service.create_report(report_data)
    
    def get_reports(self, report_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all reports or by type"""
        return self._service.get_reports(report_type)
    
    def generate_report(self, report_id: int, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate report with parameters"""
        return self._service.generate_report(report_id, parameters)
    
    def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI"""
        return self._service.create_kpi(kpi_data)
    
    def get_kpis(self, kpi_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all KPIs or by type"""
        return self._service.get_kpis(kpi_type)
    
    def calculate_kpi(self, kpi_id: int) -> Dict[str, Any]:
        """Calculate KPI value"""
        return self._service.calculate_kpi(kpi_id)
    
    def create_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chart"""
        return self._service.create_chart(chart_data)
    
    def get_charts(self, chart_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all charts or by type"""
        return self._service.get_charts(chart_type)
    
    def get_analytics_data(self, data_source: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get analytics data from various sources"""
        return self._service.get_analytics_data(data_source, filters)


class WorkflowInterface:
    """Interface for Workflow Management operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.workflow_service import WorkflowService
        self._service = WorkflowService(solution_name)
    
    def create_workflow_definition(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow definition"""
        return self._service.create_workflow_definition(workflow_data)
    
    def get_workflow_definitions(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all workflow definitions or by type"""
        return self._service.get_workflow_definitions(workflow_type)
    
    def start_workflow(self, workflow_definition_id: int, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new workflow instance"""
        return self._service.start_workflow(workflow_definition_id, initial_data)
    
    def get_active_workflows(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get active workflow instances"""
        return self._service.get_active_workflows(user_id)
    
    def execute_workflow_step(self, workflow_instance_id: int, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow step"""
        return self._service.execute_workflow_step(workflow_instance_id, step_data)
    
    def create_approval_request(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an approval request"""
        return self._service.create_approval_request(approval_data)
    
    def get_approval_requests(self, status: Optional[str] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get approval requests"""
        return self._service.get_approval_requests(status, user_id)
    
    def respond_to_approval(self, approval_id: int, response: str, comments: str = '') -> Dict[str, Any]:
        """Respond to an approval request"""
        return self._service.respond_to_approval(approval_id, response, comments)
    
    def get_workflow_analytics(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow analytics and metrics"""
        return self._service.get_workflow_analytics(workflow_type)


class ComplianceInterface:
    """Interface for Compliance Management operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.compliance_service import ComplianceService
        self._service = ComplianceService(solution_name)
    
    def create_compliance_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new compliance rule"""
        return self._service.create_compliance_rule(rule_data)
    
    def get_compliance_rules(self, compliance_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all compliance rules or by type"""
        return self._service.get_compliance_rules(compliance_type)
    
    def check_compliance(self, rule_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance against a rule"""
        return self._service.check_compliance(rule_id, data)
    
    def get_compliance_status(self, compliance_type: Optional[str] = None) -> Dict[str, Any]:
        """Get overall compliance status"""
        return self._service.get_compliance_status(compliance_type)
    
    def create_audit_trail(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an audit trail entry"""
        return self._service.create_audit_trail(audit_data)
    
    def get_audit_trails(self, entity_type: Optional[str] = None, entity_id: Optional[int] = None) -> Dict[str, Any]:
        """Get audit trails"""
        return self._service.get_audit_trails(entity_type, entity_id)
    
    def generate_compliance_report(self, report_type: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate compliance report"""
        return self._service.generate_compliance_report(report_type, parameters)
    
    def get_compliance_deadlines(self, compliance_type: Optional[str] = None) -> Dict[str, Any]:
        """Get compliance deadlines"""
        return self._service.get_compliance_deadlines(compliance_type)
    
    def update_compliance_status(self, rule_id: int, status: str, notes: str = '') -> Dict[str, Any]:
        """Update compliance status"""
        return self._service.update_compliance_status(rule_id, status, notes)


class NotificationInterface:
    """Interface for Notification Management operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.notification_service import NotificationService
        self._service = NotificationService(solution_name)
    
    def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new notification"""
        return self._service.create_notification(notification_data)
    
    def get_notifications(self, notification_type: Optional[str] = None, is_read: Optional[bool] = None) -> Dict[str, Any]:
        """Get notifications"""
        return self._service.get_notifications(notification_type, is_read)
    
    def mark_notification_read(self, notification_id: int) -> Dict[str, Any]:
        """Mark notification as read"""
        return self._service.mark_notification_read(notification_id)
    
    def mark_all_notifications_read(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Mark all notifications as read"""
        return self._service.mark_all_notifications_read(user_id)
    
    def delete_notification(self, notification_id: int) -> Dict[str, Any]:
        """Delete notification"""
        return self._service.delete_notification(notification_id)
    
    def get_notification_settings(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get notification settings"""
        return self._service.get_notification_settings(user_id)
    
    def update_notification_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification settings"""
        return self._service.update_notification_settings(settings_data)
    
    def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an alert notification"""
        return self._service.send_alert(alert_data)
    
    def get_active_alerts(self, alert_type: Optional[str] = None) -> Dict[str, Any]:
        """Get active alerts"""
        return self._service.get_active_alerts(alert_type)


class OnboardingInterface:
    """Interface for Client Onboarding operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.onboarding_service import OnboardingService
        self._service = OnboardingService(solution_name)
    
    def start_onboarding(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start client onboarding process"""
        return self._service.start_onboarding(client_data)
    
    def get_onboarding_status(self, client_id: int) -> Dict[str, Any]:
        """Get onboarding status"""
        return self._service.get_onboarding_status(client_id)
    
    def update_onboarding_step(self, client_id: int, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update onboarding step"""
        return self._service.update_onboarding_step(client_id, step_name, step_data)
    
    def complete_onboarding(self, client_id: int) -> Dict[str, Any]:
        """Complete onboarding process"""
        return self._service.complete_onboarding(client_id)
    
    def get_onboarding_templates(self, business_type: Optional[str] = None) -> Dict[str, Any]:
        """Get onboarding templates"""
        return self._service.get_onboarding_templates(business_type)
    
    def apply_onboarding_template(self, client_id: int, template_name: str) -> Dict[str, Any]:
        """Apply onboarding template"""
        return self._service.apply_onboarding_template(client_id, template_name)
    
    def import_demo_data(self, client_id: int, demo_type: str) -> Dict[str, Any]:
        """Import demo data for client"""
        return self._service.import_demo_data(client_id, demo_type)
    
    def get_onboarding_timeline(self, client_id: int) -> Dict[str, Any]:
        """Get onboarding timeline"""
        return self._service.get_onboarding_timeline(client_id)


class OdooIntegrationInterface:
    """Interface for Odoo ERP Integration operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.odoo_client import OdooClient
        from .services.discovery_service import DiscoveryService
        self._odoo_client = OdooClient(solution_name)
        self._discovery_service = DiscoveryService(solution_name)
    
    def discover_models(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover Odoo models"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        return self._discovery_service.discover_models(db_name)
    
    def discover_fields(self, model_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover Odoo model fields"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        return self._discovery_service.discover_fields(model_name, db_name)
    
    def discover_modules(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover Odoo modules"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        return self._discovery_service.discover_modules(db_name)
    
    def install_module(self, module_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Install Odoo module"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        return self._discovery_service.install_module(module_name, db_name)
    
    def uninstall_module(self, module_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Uninstall Odoo module"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        return self._discovery_service.uninstall_module(module_name, db_name)
    
    def get_records(self, model_name: str, filters: Optional[Dict[str, Any]] = None, 
                   fields: Optional[List[str]] = None, limit: Optional[int] = None, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get records from Odoo"""
        # Map filters to domain format expected by OdooClient
        domain = filters if filters else []
        db_name = database_name or f"fbs_{self.solution_name}_db"
        corrected_model_name = self._map_model_name(model_name)
        return self._odoo_client.list_records(corrected_model_name, '', db_name, domain, fields, None, limit, 0)
    
    def get_record(self, model_name: str, record_id: int, fields: Optional[List[str]] = None, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get single record from Odoo"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        corrected_model_name = self._map_model_name(model_name)
        return self._odoo_client.get_record(corrected_model_name, record_id, '', db_name, fields)
    
    def create_record(self, model_name: str, record_data: Dict[str, Any], database_name: Optional[str] = None) -> Dict[str, Any]:
        """Create record in Odoo"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        corrected_model_name = self._map_model_name(model_name)
        return self._odoo_client.create_record(corrected_model_name, record_data, '', db_name)
    
    def update_record(self, model_name: str, record_id: int, record_data: Dict[str, Any], database_name: Optional[str] = None) -> Dict[str, Any]:
        """Update record in Odoo"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        corrected_model_name = self._map_model_name(model_name)
        return self._odoo_client.update_record(corrected_model_name, record_id, record_data, '', db_name)
    
    def delete_record(self, model_name: str, record_id: int, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Delete record from Odoo"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        corrected_model_name = self._map_model_name(model_name)
        return self._odoo_client.delete_record(corrected_model_name, record_id, '', db_name)
    
    def search_read(self, model_name: str, domain: Optional[List] = None, 
                   fields: Optional[List[str]] = None, limit: Optional[int] = None, 
                   offset: Optional[int] = None, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Search and read records from Odoo model - compatibility method for rental endpoints"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        search_domain = domain or []
        
        # Apply model name mapping for backwards compatibility
        corrected_model_name = self._map_model_name(model_name)
        
        # Log the operation for debugging
        logger = logging.getLogger('fbs_app')
        if corrected_model_name != model_name:
            logger.info(f"search_read: Using mapped model '{corrected_model_name}' for requested '{model_name}'")
        else:
            logger.debug(f"search_read: Using model '{model_name}' directly")
        
        try:
            result = self._odoo_client.search_read_records(
                model_name=corrected_model_name,
                domain=search_domain,
                fields=fields,
                database=db_name,
                limit=limit,
                offset=offset
            )
            
            # If the query failed with a field error, provide helpful context
            if not result.get('success') and 'Invalid field' in str(result.get('error', '')):
                error_msg = result.get('error', '')
                enhanced_error = f"Field validation failed for model '{corrected_model_name}'. "
                if corrected_model_name != model_name:
                    enhanced_error += f"Note: '{model_name}' was mapped to '{corrected_model_name}'. "
                enhanced_error += f"Original error: {error_msg}"
                
                logger.error(enhanced_error)
                result['error'] = enhanced_error
                result['debug_info'] = {
                    'requested_model': model_name,
                    'mapped_model': corrected_model_name,
                    'requested_fields': fields,
                    'domain': search_domain
                }
            
            return result
            
        except Exception as e:
            logger.error(f"search_read failed for model '{corrected_model_name}': {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'debug_info': {
                    'requested_model': model_name,
                    'mapped_model': corrected_model_name,
                    'requested_fields': fields,
                    'domain': search_domain
                }
            }
    
    def _map_model_name(self, model_name: str) -> str:
        """Map deprecated or incorrect model names to correct Odoo model names
        
        This method provides backwards compatibility for deprecated 'inventory.*' models
        while ensuring direct 'stock.*' model usage works correctly.
        """
        # Only map deprecated 'inventory.*' models - leave everything else unchanged
        deprecated_mapping = {
            'inventory.location': 'stock.location',    # Deprecated → Correct
            'inventory.warehouse': 'stock.warehouse',  # Deprecated → Correct  
            'inventory.picking': 'stock.picking',      # Deprecated → Correct
            'inventory.move': 'stock.move',            # Deprecated → Correct
        }
        
        # Only apply mapping for deprecated models
        if model_name.startswith('inventory.'):
            mapped_name = deprecated_mapping.get(model_name, model_name)
            if mapped_name != model_name:
                logger = logging.getLogger('fbs_app')
                logger.warning(f"Deprecated model mapping: {model_name} -> {mapped_name}")
            return mapped_name
        
        # Return all other models unchanged (including stock.*, res.*, etc.)
        return model_name
    
    def _validate_model_exists(self, model_name: str, database_name: str) -> bool:
        """Validate that a model exists in the Odoo database
        
        Args:
            model_name: Name of the model to validate
            database_name: Name of the Odoo database
            
        Returns:
            bool: True if model exists, False otherwise
        """
        try:
            # Use discovery service to check if model exists
            models_result = self._discovery_service.discover_models(database_name)
            if not models_result.get('success'):
                logger.warning(f"Could not validate model '{model_name}' - discovery failed")
                return True  # Assume valid if we can't check
            
            models_data = models_result.get('data', [])
            if isinstance(models_data, dict) and 'models' in models_data:
                models = models_data['models']
            elif isinstance(models_data, list):
                models = models_data
            else:
                return True  # Assume valid if format unexpected
            
            # Check if model exists
            model_names = [m.get('name', '') for m in models if isinstance(m, dict)]
            exists = model_name in model_names
            
            if not exists:
                logger.error(f"Model '{model_name}' not found in database '{database_name}'. Available models: {model_names[:10]}...")
                
            return exists
            
        except Exception as e:
            logger.warning(f"Model validation failed for '{model_name}': {str(e)}")
            return True  # Assume valid if validation fails
    
    def execute_method(self, model_name: str, method_name: str, record_ids: List[int], 
                      parameters: Optional[Dict[str, Any]] = None, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Execute method on Odoo records"""
        db_name = database_name or f"fbs_{self.solution_name}_db"
        return self._odoo_client.execute_method(
            model_name=model_name, 
            method_name=method_name, 
            record_ids=record_ids,
            args=[],
            kwargs=parameters or {},
            database=db_name
        )
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get Odoo database information"""
        return self._odoo_client.get_database_info()
    
    def create_fbs_tables(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Create required FBS database tables"""
        from .services.database_service import DatabaseService
        db_service = DatabaseService(self.solution_name)
        return db_service.create_fbs_tables(database_name=database_name, solution_name=self.solution_name)
    
    def create_solution_databases(self) -> Dict[str, Any]:
        """Create both Django and Odoo databases for the solution"""
        from .services.database_service import DatabaseService
        db_service = DatabaseService(self.solution_name)
        
        results = {}
        
        # Create Django database
        django_result = db_service.create_database('django', self.solution_name)
        results['django'] = django_result
        
        # Create Odoo database using the new method that properly initializes Odoo
        odoo_result = db_service.create_odoo_database(self.solution_name, ['base', 'web'])
        results['odoo'] = odoo_result
        
        # Check if both were successful
        both_success = django_result.get('success', False) and odoo_result.get('success', False)
        
        return {
            'success': both_success,
            'message': f'Database creation completed for solution "{self.solution_name}"',
            'solution_name': self.solution_name,
            'results': results,
            'django_db_name': f"djo_{self.solution_name}_db",
            'odoo_db_name': f"fbs_{self.solution_name}_db"
        }
    
    def install_modules(self, modules: List[str], database_name: str = None) -> Dict[str, Any]:
        """
        Install additional Odoo modules in the solution's database
        
        Args:
            modules: List of modules to install
            database_name: Optional database name override
            
        Returns:
            Dict: Result of module installation
        """
        from .services.database_service import DatabaseService
        db_service = DatabaseService(self.solution_name)
        return db_service.install_odoo_modules(self.solution_name, modules, database_name)
    
    def get_available_modules(self) -> Dict[str, Any]:
        """
        Get list of available Odoo modules that can be installed
        
        Returns:
            Dict: Available modules information
        """
        from .services.database_service import DatabaseService
        db_service = DatabaseService(self.solution_name)
        return db_service.get_available_odoo_modules()
    
    def create_solution_databases_with_modules(self, core_modules: List[str] = None, 
                                             additional_modules: List[str] = None) -> Dict[str, Any]:
        """
        Create solution databases with specific module requirements
        
        Args:
            core_modules: Core modules to install during initialization (default: ['base', 'web'])
            additional_modules: Additional modules to install during initialization (not after)
            
        Returns:
            Dict: Result of database creation with modules
        """
        from .services.database_service import DatabaseService
        db_service = DatabaseService(self.solution_name)
        
        results = {}
        
        # Create Django database
        django_result = db_service.create_database('django', self.solution_name)
        results['django'] = django_result
        
        # Combine all modules for Odoo database creation
        if core_modules is None:
            core_modules = ['base', 'web']
        
        # Install ALL modules in one step during database creation
        all_modules = core_modules + (additional_modules or [])
        
        print(f"🔧 Installing all modules in one step: {', '.join(all_modules)}")
        
        odoo_result = db_service.create_odoo_database(self.solution_name, all_modules)
        results['odoo'] = odoo_result
        
        # Check if all operations were successful or if databases already exist
        django_success = django_result.get('success', False) or 'already exists' in django_result.get('error', '')
        odoo_success = odoo_result.get('success', False) or 'already exists' in odoo_result.get('error', '')
        
        all_success = django_success and odoo_success
        
        # Determine the appropriate message
        if all_success:
            if django_success and odoo_success:
                if 'already exists' in django_result.get('error', '') or 'already exists' in odoo_result.get('error', ''):
                    message = f'Solution databases already exist and are ready for solution "{self.solution_name}"'
                else:
                    message = f'Database creation with all modules completed for solution "{self.solution_name}"'
            else:
                message = f'Database creation with all modules completed for solution "{self.solution_name}"'
        else:
            message = f'Database creation failed for solution "{self.solution_name}"'
        
        return {
            'success': all_success,
            'message': message,
            'solution_name': self.solution_name,
            'results': results,
            'django_db_name': f"djo_{self.solution_name}_db",
            'odoo_db_name': f"fbs_{self.solution_name}_db",
            'core_modules': core_modules,
            'additional_modules': additional_modules or [],
            'all_modules_installed': all_modules,
            'django_exists': 'already exists' in django_result.get('error', ''),
            'odoo_exists': 'already exists' in odoo_result.get('error', '')
        }


class VirtualFieldsInterface:
    """Interface for Virtual Fields and Custom Data operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.field_merger_service import FieldMergerService
        self._service = FieldMergerService(solution_name)
    
    def set_custom_field(self, model_name: str, record_id: int, field_name: str, 
                        field_value: Any, field_type: str = 'char', 
                        database_name: Optional[str] = None) -> Dict[str, Any]:
        """Set custom field value"""
        return self._service.set_custom_field(
            model_name, record_id, field_name, field_value, field_type, database_name
        )
    
    def get_custom_field(self, model_name: str, record_id: int, field_name: str,
                        database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get custom field value"""
        return self._service.get_custom_field(model_name, record_id, field_name, database_name)
    
    def get_custom_fields(self, model_name: str, record_id: int,
                         database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get all custom fields for a record"""
        return self._service.get_custom_fields(model_name, record_id, database_name)
    
    def delete_custom_field(self, model_name: str, record_id: int, field_name: str,
                           database_name: Optional[str] = None) -> Dict[str, Any]:
        """Delete custom field"""
        return self._service.delete_custom_field(model_name, record_id, field_name, database_name)
    
    def merge_odoo_with_custom(self, model_name: str, record_id: int,
                              odoo_fields: Optional[List[str]] = None,
                              database_name: Optional[str] = None) -> Dict[str, Any]:
        """Merge Odoo data with custom fields"""
        return self._service.merge_odoo_with_custom(
            model_name, record_id, odoo_fields, database_name
        )
    
    def get_virtual_model_schema(self, model_name: str, 
                                database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get virtual model schema including custom fields"""
        return self._service.get_virtual_model_schema(model_name, database_name)


class CacheInterface:
    """Interface for Cache Management operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.cache_service import CacheService
        self._service = CacheService(solution_name)
    
    def get_cache(self, key: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get cached value"""
        return self._service.get_cache(key, database_name)
    
    def set_cache(self, key: str, value: Any, expiry_hours: int = 24,
                  database_name: Optional[str] = None) -> Dict[str, Any]:
        """Set cache value"""
        return self._service.set_cache(key, value, expiry_hours, database_name)
    
    def delete_cache(self, key: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Delete cache entry"""
        return self._service.delete_cache(key, database_name)
    
    def clear_cache(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Clear all cache for database"""
        return self._service.clear_cache(database_name)
    
    def get_cache_stats(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get cache statistics"""
        return self._service.get_cache_stats(database_name)


class AccountingInterface:
    """Interface for accounting operations"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        from .services.simple_accounting_service import SimpleAccountingService
        self._service = SimpleAccountingService(solution_name)
    
    def create_cash_entry(self, entry_type: str, amount: float, description: str, 
                         category: str = '', date: Optional[str] = None) -> Dict[str, Any]:
        """Create cash basis accounting entry"""
        return self._service.create_cash_basis_entry(
            entry_type=entry_type,
            amount=amount,
            description=description,
            category=category,
            date=date
        )
    
    def get_basic_ledger(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None, 
                         account_type: Optional[str] = None) -> Dict[str, Any]:
        """Get simple general ledger"""
        return self._service.get_basic_ledger(
            start_date=start_date,
            end_date=end_date,
            account_type=account_type
        )
    
    def track_income_expense(self, transaction_type: str, amount: float, 
                           description: str, category: str = '', 
                           date: Optional[str] = None) -> Dict[str, Any]:
        """Track simple income and expense"""
        return self._service.create_income_expense_record(
            record_type=transaction_type,
            amount=amount,
            description=description,
            category=category,
            date=date
        )
    
    def get_income_expense_summary(self, period: str = 'month') -> Dict[str, Any]:
        """Get income and expense summary"""
        return self._service.get_income_expense_summary(period)
    
    def get_financial_health_indicators(self) -> Dict[str, Any]:
        """Get basic financial health indicators"""
        return self._service.get_financial_health_indicators()
    
    def calculate_tax(self, amount: float, tax_type: str = 'vat', 
                     tax_rate: Optional[float] = None) -> Dict[str, Any]:
        """Calculate tax amounts"""
        return self._service.calculate_tax(amount, tax_type, tax_rate)
    
    def get_cash_position(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get current cash position"""
        return self._service.get_cash_position(date)
    
    def create_recurring_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create recurring transaction"""
        return self._service.create_recurring_transaction(transaction_data)
    
    def get_recurring_transactions(self, status: Optional[str] = None) -> Dict[str, Any]:
        """Get recurring transactions"""
        return self._service.get_recurring_transactions(status)


class FBSInterface:
    """Main interface for all FBS app capabilities"""
    
    def __init__(self, solution_name: str, license_key: str = None):
        self.solution_name = solution_name
        self.license_key = license_key
        
        # Auto-generate database names
        self.django_db_name = f"djo_{solution_name}_db"
        self.odoo_db_name = f"fbs_{solution_name}_db"
        
        # Initialize licensing system (optional)
        if license_key is None:
            # No license key provided - use no licensing mode
            self.license_manager = None
            self.feature_flags = None
            self._licensing_available = False
        else:
            try:
                from fbs_license_manager import LicenseManager, FeatureFlags
                self.license_manager = LicenseManager(solution_name, license_key)
                self.feature_flags = FeatureFlags(solution_name, self.license_manager)
                self._licensing_available = True
            except ImportError:
                # Fallback to no licensing
                self.license_manager = None
                self.feature_flags = None
                self._licensing_available = False
        
        # Initialize core interfaces (always available)
        self.odoo = OdooIntegrationInterface(solution_name)
        
        # Initialize licensed interfaces conditionally
        if self._licensing_available and self.feature_flags:
            if self.feature_flags.is_enabled('msme'):
                self.msme = MSMEInterface(solution_name)
            
            if self.feature_flags.is_enabled('bi'):
                self.bi = BusinessIntelligenceInterface(solution_name)
            
            if self.feature_flags.is_enabled('workflows'):
                self.workflows = WorkflowInterface(solution_name)
            
            if self.feature_flags.is_enabled('compliance'):
                self.compliance = ComplianceInterface(solution_name)
            
            if self.feature_flags.is_enabled('accounting'):
                self.accounting = AccountingInterface(solution_name)
            
            if self.feature_flags.is_enabled('notifications'):
                self.notifications = NotificationInterface(solution_name)
            
            if self.feature_flags.is_enabled('onboarding'):
                self.onboarding = OnboardingInterface(solution_name)
            
            if self.feature_flags.is_enabled('fields'):
                self.fields = VirtualFieldsInterface(solution_name)
            
            if self.feature_flags.is_enabled('cache'):
                self.cache = CacheInterface(solution_name)
        else:
            # No licensing - initialize all interfaces
            self.msme = MSMEInterface(solution_name)
            self.bi = BusinessIntelligenceInterface(solution_name)
            self.workflows = WorkflowInterface(solution_name)
            self.compliance = ComplianceInterface(solution_name)
            self.accounting = AccountingInterface(solution_name)
            self.notifications = NotificationInterface(solution_name)
            self.onboarding = OnboardingInterface(solution_name)
            self.fields = VirtualFieldsInterface(solution_name)
            self.cache = CacheInterface(solution_name)
    
    def get_solution_info(self) -> Dict[str, Any]:
        """Get solution information"""
        return {
            'solution_name': self.solution_name,
            'timestamp': timezone.now().isoformat(),
            'capabilities': {
                'msme': 'MSME business management',
                'accounting': 'Simple accounting operations',
                'bi': 'Business Intelligence & Analytics',
                'workflows': 'Workflow management',
                'compliance': 'Compliance management',
                'notifications': 'Notification system',
                'onboarding': 'Client onboarding',
                'odoo': 'Odoo ERP integration',
                'fields': 'Virtual fields & custom data',
                'cache': 'Cache management'
            }
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        return {
            'solution_name': self.solution_name,
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': {
                'msme': 'operational',
                'accounting': 'operational',
                'bi': 'operational',
                'workflows': 'operational',
                'compliance': 'operational',
                'notifications': 'operational',
                'onboarding': 'operational',
                'odoo': 'operational',
                'fields': 'operational',
                'cache': 'operational'
            }
        }
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get comprehensive license information"""
        if self._licensing_available and self.license_manager:
            return self.license_manager.get_license_info()
        else:
            return {
                'license_type': 'unlimited',
                'status': 'active',
                'features': ['all_features'],
                'limits': {'unlimited': True},
                'expiry_date': None,
                'source': 'unlimited'
            }
    
    def get_odoo_client(self):
        """Get the Odoo client for direct access"""
        return self.odoo._odoo_client
    
    def is_odoo_available(self) -> bool:
        """Check if Odoo integration is available"""
        try:
            return self.odoo._odoo_client.is_available()
        except Exception:
            return False
    
    def check_feature_access(self, feature_name: str, **kwargs) -> Dict[str, Any]:
        """Check if user can access a feature"""
        if self._licensing_available and self.feature_flags:
            return self.feature_flags.check_feature_access(feature_name, **kwargs)
        else:
            return {
                'access': True,
                'remaining': -1,
                'limit': -1,
                'feature_name': feature_name,
                'licensing_available': False
            }
    
    def get_upgrade_prompt(self, feature_name: str) -> Dict[str, Any]:
        """Get upgrade prompt for a feature"""
        if self._licensing_available and self.license_manager:
            try:
                from fbs_license_manager import UpgradePrompts
                upgrade_prompts = UpgradePrompts(self.license_manager)
                return upgrade_prompts.get_upgrade_prompt(feature_name)
            except ImportError:
                pass
        
        return {'upgrade_required': False, 'message': 'No licensing system available'}
    
    def get_feature_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Get complete feature availability matrix"""
        if self._licensing_available and self.feature_flags:
            return self.feature_flags.get_feature_matrix()
        else:
            return {
                'all_features': {
                    'enabled': True,
                    'limit': -1,
                    'unlimited': True,
                    'dependencies_met': True,
                    'missing_dependencies': []
                }
            }
    
    def get_upgrade_analysis(self) -> Dict[str, Any]:
        """Get comprehensive upgrade analysis"""
        if self._licensing_available and self.license_manager:
            try:
                from fbs_license_manager import UpgradePrompts
                upgrade_prompts = UpgradePrompts(self.license_manager)
                return upgrade_prompts.get_comprehensive_upgrade_analysis()
            except ImportError:
                pass
        
        return {'analysis': 'No licensing system available'}

    def create_solution_databases(self) -> Dict[str, Any]:
        """Create both Django and Odoo databases for the solution"""
        return self.odoo.create_solution_databases()
    
    def ensure_databases_exist(self) -> Dict[str, Any]:
        """
        Ensure that the required databases exist for this solution.
        This method can be called by solutions to verify their database setup.
        
        Returns:
            Dict with database verification results and guidance
        """
        from .services.database_service import DatabaseService
        db_service = DatabaseService(self.solution_name)
        return db_service.ensure_solution_databases(self.solution_name)
    
    def create_odoo_schema(self) -> Dict[str, Any]:
        """
        Create Odoo-specific schema and tables in the solution's database.
        This should be called by solutions after they create their databases.
        
        Returns:
            Dict with schema creation results
        """
        from .services.database_service import DatabaseService
        db_service = DatabaseService(self.solution_name)
        return db_service.create_odoo_schema(self.solution_name)
    
    def get_database_status(self) -> Dict[str, Any]:
        """
        Get the current status of databases for this solution.
        
        Returns:
            Dict with database status information
        """
        from .services.database_service import DatabaseService
        db_service = DatabaseService(self.solution_name)
        return db_service.ensure_solution_databases(self.solution_name)


# Convenience function for quick access
def get_fbs_interface(solution_name: str, license_key: str = None) -> FBSInterface:
    """Get FBS interface for a solution"""
    return FBSInterface(solution_name, license_key)
