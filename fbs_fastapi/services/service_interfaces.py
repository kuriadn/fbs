"""
FBS FastAPI Service Interfaces

Clean service-based architecture preserving the Django interface pattern.
Provides unified APIs for all FBS functionality with dependency injection.

This mirrors the sophisticated Django interfaces.py but optimized for FastAPI.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Protocol, Callable
from uuid import UUID
from datetime import datetime, date

# ============================================================================
# SERVICE INTERFACE PROTOCOLS
# ============================================================================

class MSMEInterfaceProtocol(Protocol):
    """MSME service interface protocol"""

    async def setup_business(self, business_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup MSME business with pre-configured data"""
        ...

    async def get_dashboard(self) -> Dict[str, Any]:
        """Get MSME dashboard data"""
        ...

    async def calculate_kpis(self) -> Dict[str, Any]:
        """Calculate MSME KPIs"""
        ...

    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status"""
        ...

    async def update_business_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update business profile"""
        ...

    async def get_marketing_data(self) -> Dict[str, Any]:
        """Get marketing data"""
        ...

    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        ...

    async def create_custom_field(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom field"""
        ...

    async def get_business_templates(self) -> Dict[str, Any]:
        """Get business templates"""
        ...

    async def apply_business_template(self, template_name: str) -> Dict[str, Any]:
        """Apply business template"""
        ...

    async def get_setup_wizard_status(self) -> Dict[str, Any]:
        """Get setup wizard status"""
        ...

    async def update_setup_wizard_step(self, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update setup wizard step"""
        ...

class BusinessIntelligenceInterfaceProtocol(Protocol):
    """Business Intelligence service interface protocol"""

    async def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dashboard"""
        ...

    async def get_dashboards(self, dashboard_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all dashboards or by type"""
        ...

    async def update_dashboard(self, dashboard_id: UUID, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update dashboard"""
        ...

    async def delete_dashboard(self, dashboard_id: UUID) -> Dict[str, Any]:
        """Delete dashboard"""
        ...

    async def create_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report"""
        ...

    async def get_reports(self, report_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all reports or by type"""
        ...

    async def generate_report(self, report_id: UUID, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate report with parameters"""
        ...

    async def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI"""
        ...

    async def get_kpis(self, kpi_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all KPIs or by type"""
        ...

    async def calculate_kpi(self, kpi_id: UUID) -> Dict[str, Any]:
        """Calculate KPI value"""
        ...

    async def create_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chart"""
        ...

    async def get_charts(self, chart_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all charts or by type"""
        ...

    async def get_analytics_data(self, data_source: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get analytics data from various sources"""
        ...

class WorkflowInterfaceProtocol(Protocol):
    """Workflow service interface protocol"""

    async def create_workflow_definition(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow definition"""
        ...

    async def get_workflow_definitions(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all workflow definitions or by type"""
        ...

    async def start_workflow(self, workflow_definition_id: UUID, initial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new workflow instance"""
        ...

    async def get_active_workflows(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get active workflow instances"""
        ...

    async def execute_workflow_step(self, workflow_instance_id: UUID, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow step"""
        ...

    async def create_approval_request(self, approval_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an approval request"""
        ...

    async def get_approval_requests(self, status: Optional[str] = None, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get approval requests"""
        ...

    async def respond_to_approval(self, approval_id: UUID, response: str, comments: str = '') -> Dict[str, Any]:
        """Respond to an approval request"""
        ...

    async def get_workflow_analytics(self, workflow_type: Optional[str] = None) -> Dict[str, Any]:
        """Get workflow analytics and metrics"""
        ...

class ComplianceInterfaceProtocol(Protocol):
    """Compliance service interface protocol"""

    async def create_compliance_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new compliance rule"""
        ...

    async def get_compliance_rules(self, compliance_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all compliance rules or by type"""
        ...

    async def check_compliance(self, rule_id: UUID, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance against a rule"""
        ...

    async def get_compliance_status(self, compliance_type: Optional[str] = None) -> Dict[str, Any]:
        """Get overall compliance status"""
        ...

    async def create_audit_trail(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an audit trail entry"""
        ...

    async def get_audit_trails(self, entity_type: Optional[str] = None, entity_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get audit trails"""
        ...

    async def generate_compliance_report(self, report_type: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate compliance report"""
        ...

    async def get_compliance_deadlines(self, compliance_type: Optional[str] = None) -> Dict[str, Any]:
        """Get compliance deadlines"""
        ...

    async def update_compliance_status(self, rule_id: UUID, status: str, notes: str = '') -> Dict[str, Any]:
        """Update compliance status"""
        ...

class SignalsInterfaceProtocol(Protocol):
    """Signals service interface protocol - PRESERVED from Django"""

    async def register_custom_signal(self, signal_name: str, handler: Callable) -> Dict[str, Any]:
        """Register a custom signal handler"""
        ...

    async def send_custom_signal(self, signal_name: str, **kwargs) -> Dict[str, Any]:
        """Send a custom signal"""
        ...

    async def get_signal_stats(self) -> Dict[str, Any]:
        """Get statistics about registered signals"""
        ...

    async def trigger_model_signal(self, model_name: str, operation: str, instance, **kwargs) -> Dict[str, Any]:
        """Trigger a signal for a specific model operation"""
        ...

class OdooInterfaceProtocol(Protocol):
    """Odoo integration interface protocol"""

    async def discover_models(self) -> Dict[str, Any]:
        """Discover available Odoo models"""
        ...

    async def discover_fields(self, model_name: str) -> Dict[str, Any]:
        """Discover fields for a specific model"""
        ...

    async def get_records(self, model_name: str, domain: List, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get records from Odoo model"""
        ...

    async def create_record(self, model_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new record in Odoo"""
        ...

    async def update_record(self, model_name: str, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record in Odoo"""
        ...

    async def delete_record(self, model_name: str, record_id: int) -> Dict[str, Any]:
        """Delete a record in Odoo"""
        ...

    async def execute_workflow(self, model_name: str, record_id: int, action: str) -> Dict[str, Any]:
        """Execute a workflow action on a record"""
        ...

class AccountingInterfaceProtocol(Protocol):
    """Accounting service interface protocol - PRESERVED from Django"""

    async def create_cash_entry(self, entry_type: str, amount: float, description: str,
                               category: str = '', date: Optional[str] = None) -> Dict[str, Any]:
        """Create cash basis accounting entry"""
        ...

    async def get_basic_ledger(self, start_date: Optional[str] = None,
                              end_date: Optional[str] = None,
                              account_type: Optional[str] = None) -> Dict[str, Any]:
        """Get simple general ledger"""
        ...

    async def track_income_expense(self, transaction_type: str, amount: float,
                                  description: str, category: str = '',
                                  date: Optional[str] = None) -> Dict[str, Any]:
        """Track simple income and expense"""
        ...

    async def get_income_expense_summary(self, period: str = 'month') -> Dict[str, Any]:
        """Get income and expense summary"""
        ...

    async def get_financial_health_indicators(self) -> Dict[str, Any]:
        """Get basic financial health indicators"""
        ...

    async def calculate_tax(self, amount: float, tax_type: str = 'vat',
                           tax_rate: Optional[float] = None) -> Dict[str, Any]:
        """Calculate tax amounts"""
        ...

    async def get_cash_position(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get current cash position"""
        ...

class AuthInterfaceProtocol(Protocol):
    """Authentication service interface protocol - PRESERVED from Django"""

    async def create_handshake(self, secret_key: Optional[str] = None,
                              expiry_hours: Optional[int] = None) -> Dict[str, Any]:
        """Create a new handshake for system authentication"""
        ...

    async def validate_handshake(self, handshake_id: str, secret_key: str) -> Dict[str, Any]:
        """Validate a handshake ID and secret key"""
        ...

    async def revoke_handshake(self, handshake_id: str) -> Dict[str, Any]:
        """Revoke a handshake"""
        ...

    async def get_active_handshakes(self, solution_name: Optional[str] = None) -> Dict[str, Any]:
        """Get active handshakes for a solution"""
        ...

    async def cleanup_expired_handshakes(self) -> Dict[str, Any]:
        """Clean up expired handshakes"""
        ...

    async def create_token_mapping(self, user_id: str, database_name: str,
                                  odoo_token: str, odoo_user_id: int,
                                  expiry_hours: Optional[int] = None) -> Dict[str, Any]:
        """Create token mapping for Odoo integration"""
        ...

    async def validate_token_mapping(self, token: str, database_name: str) -> Dict[str, Any]:
        """Validate token mapping"""
        ...

    async def revoke_token_mapping(self, token_mapping_id: str) -> Dict[str, Any]:
        """Revoke token mapping"""
        ...

    async def get_user_token_mappings(self, user_id: str) -> Dict[str, Any]:
        """Get all token mappings for a user"""
        ...

class OnboardingInterfaceProtocol(Protocol):
    """Onboarding service interface protocol - PRESERVED from Django"""

    async def start_onboarding(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start client onboarding process"""
        ...

    async def get_onboarding_status(self, client_id: UUID) -> Dict[str, Any]:
        """Get onboarding status"""
        ...

    async def update_onboarding_step(self, client_id: UUID, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update onboarding step"""
        ...

    async def complete_onboarding(self, client_id: UUID) -> Dict[str, Any]:
        """Complete onboarding process"""
        ...

    async def get_onboarding_templates(self, business_type: Optional[str] = None) -> Dict[str, Any]:
        """Get onboarding templates"""
        ...

    async def apply_onboarding_template(self, client_id: UUID, template_name: str) -> Dict[str, Any]:
        """Apply onboarding template"""
        ...

    async def import_demo_data(self, client_id: UUID, demo_type: str) -> Dict[str, Any]:
        """Import demo data for client"""
        ...

    async def get_onboarding_timeline(self, client_id: UUID) -> Dict[str, Any]:
        """Get onboarding timeline"""
        ...

class DiscoveryInterfaceProtocol(Protocol):
    """Discovery service interface protocol - PRESERVED from Django"""

    async def discover_models(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover all models in an Odoo database"""
        ...

    async def discover_modules(self, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover installed modules in an Odoo database"""
        ...

    async def discover_fields(self, model_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover fields for a specific Odoo model"""
        ...

    async def install_module(self, module_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Install a module in Odoo database"""
        ...

    async def uninstall_module(self, module_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Uninstall a module from Odoo database"""
        ...

    async def get_model_relationships(self, model_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get relationships between models"""
        ...

    async def discover_workflows(self, model_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
        """Discover workflows for a model"""
        ...

class VirtualFieldsInterfaceProtocol(Protocol):
    """Virtual Fields service interface protocol - PRESERVED from Django"""

    async def set_custom_field(self, model_name: str, record_id: int, field_name: str,
                             field_value: Any, field_type: str = 'char',
                             database_name: Optional[str] = None) -> Dict[str, Any]:
        """Set custom field value"""
        ...

    async def get_custom_field(self, model_name: str, record_id: int, field_name: str,
                             database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get custom field value"""
        ...

    async def get_custom_fields(self, model_name: str, record_id: int,
                              database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get all custom fields for a record"""
        ...

    async def delete_custom_field(self, model_name: str, record_id: int, field_name: str,
                                database_name: Optional[str] = None) -> Dict[str, Any]:
        """Delete custom field"""
        ...

    async def merge_odoo_with_custom(self, model_name: str, record_id: int,
                                   odoo_fields: Optional[List[str]] = None,
                                   database_name: Optional[str] = None) -> Dict[str, Any]:
        """Merge Odoo data with custom fields"""
        ...

    async def get_virtual_model_schema(self, model_name: str,
                                     database_name: Optional[str] = None) -> Dict[str, Any]:
        """Get virtual model schema including custom fields"""
        ...

class NotificationInterfaceProtocol(Protocol):
    """Notification service interface protocol"""

    async def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new notification"""
        ...

    async def get_notifications(self, notification_type: Optional[str] = None, is_read: Optional[bool] = None) -> Dict[str, Any]:
        """Get notifications"""
        ...

    async def mark_notification_read(self, notification_id: UUID) -> Dict[str, Any]:
        """Mark notification as read"""
        ...

    async def mark_all_notifications_read(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Mark all notifications as read"""
        ...

    async def delete_notification(self, notification_id: UUID) -> Dict[str, Any]:
        """Delete notification"""
        ...

    async def get_notification_settings(self, user_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Get notification settings"""
        ...

    async def update_notification_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update notification settings"""
        ...

    async def send_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an alert notification"""
        ...

# ============================================================================
# MAIN FBS INTERFACE (PRESERVES DJANGO PATTERN)
# ============================================================================

class FBSInterface:
    """
    Main FBS Interface - Preserves Django interface pattern in FastAPI

    This is the core architectural pattern that provides unified access
    to all FBS functionality with clean service interfaces.
    """

    def __init__(self, solution_name: str, license_key: str = None):
        """
        Initialize FBS interface for a specific solution.

        PRESERVED from Django: Conditional service loading based on licensing.

        Args:
            solution_name: Name of the solution to interface with
            license_key: Optional license key for feature control
        """
        self.solution_name = solution_name
        self.license_key = license_key

        # Auto-generate database names (PRESERVED from Django)
        self.fastapi_db_name = f"fpi_{solution_name}_db"
        self.odoo_db_name = f"fbs_{solution_name}_db"

        # Initialize licensing system (PRESERVED from Django)
        if license_key is None:
            # No license key provided - use unlimited access mode
            self.license_manager = None
            self.feature_flags = None
            self._licensing_available = False
        else:
            try:
                from .license_manager import LicenseManager, FeatureFlags
                self.license_manager = LicenseManager(solution_name, license_key)
                self.feature_flags = FeatureFlags(solution_name, self.license_manager)
                self._licensing_available = True
            except ImportError:
                # Fallback to unlimited access
                self.license_manager = None
                self.feature_flags = None
                self._licensing_available = False

        # Initialize core interfaces (always available)
        # Initialize service interfaces (lazy loading for performance)
        self._msme: Optional[MSMEInterfaceProtocol] = None
        self._bi: Optional[BusinessIntelligenceInterfaceProtocol] = None
        self._workflows: Optional[WorkflowInterfaceProtocol] = None
        self._compliance: Optional[ComplianceInterfaceProtocol] = None
        self._auth: Optional[AuthInterfaceProtocol] = None
        self._onboarding: Optional[OnboardingInterfaceProtocol] = None
        self._discovery: Optional[DiscoveryInterfaceProtocol] = None
        self._signals: Optional[SignalsInterfaceProtocol] = None
        self._accounting: Optional[AccountingInterfaceProtocol] = None
        self._virtual_fields: Optional[VirtualFieldsInterfaceProtocol] = None
        self._odoo: Optional[OdooInterfaceProtocol] = None
        self._notifications: Optional[NotificationInterfaceProtocol] = None
        self._module_gen = None  # NEW: Module Generation Service
        self._cache = None

    @property
    def msme(self) -> MSMEInterfaceProtocol:
        """Get MSME service interface - PRESERVED from Django conditional loading"""
        if self._msme is None:
            # Check licensing (PRESERVED from Django)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('msme'):
                    raise ValueError("MSME feature not enabled in license")

            from .msme_service import MSMEService
            self._msme = MSMEService(self.solution_name)
        return self._msme

    @property
    def bi(self) -> BusinessIntelligenceInterfaceProtocol:
        """Get Business Intelligence service interface"""
        if self._bi is None:
            from .bi_service import BIService
            self._bi = BIService(self.solution_name)
        return self._bi

    @property
    def workflows(self) -> WorkflowInterfaceProtocol:
        """Get Workflow service interface"""
        if self._workflows is None:
            from .workflow_service import WorkflowService
            self._workflows = WorkflowService(self.solution_name)
        return self._workflows

    @property
    def compliance(self) -> ComplianceInterfaceProtocol:
        """Get Compliance service interface"""
        if self._compliance is None:
            from .compliance_service import ComplianceService
            self._compliance = ComplianceService(self.solution_name)
        return self._compliance

    @property
    def auth(self) -> AuthInterfaceProtocol:
        """Get Authentication service interface - PRESERVED from Django conditional loading"""
        if self._auth is None:
            # Check licensing (PRESERVED from Django)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('auth'):
                    raise ValueError("Authentication feature not enabled in license")

            from .auth_service import AuthService
            self._auth = AuthService(self.solution_name)
        return self._auth

    @property
    def onboarding(self) -> OnboardingInterfaceProtocol:
        """Get Onboarding service interface - PRESERVED from Django conditional loading"""
        if self._onboarding is None:
            # Check licensing (PRESERVED from Django)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('onboarding'):
                    raise ValueError("Onboarding feature not enabled in license")

            from .onboarding_service import OnboardingService
            self._onboarding = OnboardingService(self.solution_name)
        return self._onboarding

    @property
    def discovery(self) -> DiscoveryInterfaceProtocol:
        """Get Discovery service interface - PRESERVED from Django conditional loading"""
        if self._discovery is None:
            # Check licensing (PRESERVED from Django)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('discovery'):
                    raise ValueError("Discovery feature not enabled in license")

            from .discovery_service import DiscoveryService
            self._discovery = DiscoveryService(self.solution_name)
        return self._discovery

    @property
    def signals(self) -> SignalsInterfaceProtocol:
        """Get Signals service interface - PRESERVED from Django conditional loading"""
        if self._signals is None:
            from .signals_service import SignalsService
            self._signals = SignalsService(self.solution_name)
        return self._signals

    @property
    def accounting(self) -> AccountingInterfaceProtocol:
        """Get Accounting service interface - PRESERVED from Django conditional loading"""
        if self._accounting is None:
            # Check licensing (PRESERVED from Django)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('accounting'):
                    raise ValueError("Accounting feature not enabled in license")

            from .accounting_service import SimpleAccountingService
            self._accounting = SimpleAccountingService(self.solution_name)
        return self._accounting

    @property
    def fields(self) -> VirtualFieldsInterfaceProtocol:
        """Get Virtual Fields service interface - PRESERVED from Django conditional loading"""
        if self._virtual_fields is None:
            # Check licensing (PRESERVED from Django)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('fields'):
                    raise ValueError("Virtual fields feature not enabled in license")

            from .field_merger_service import FieldMergerService
            self._virtual_fields = FieldMergerService(self.solution_name)
        return self._virtual_fields

    @property
    def odoo(self) -> OdooInterfaceProtocol:
        """Get Odoo integration interface"""
        if self._odoo is None:
            from .odoo_service import OdooService
            self._odoo = OdooService(self.solution_name)
        return self._odoo

    @property
    def notifications(self) -> NotificationInterfaceProtocol:
        """Get Notification service interface"""
        if self._notifications is None:
            from .notification_service import NotificationService
            self._notifications = NotificationService(self.solution_name)
        return self._notifications

    @property
    def cache(self):
        """Get Cache service interface"""
        if self._cache is None:
            from .cache_service import CacheService
            self._cache = CacheService(self.solution_name)
        return self._cache

    @property
    def module_gen(self):
        """Get Module Generation service interface with Discovery integration"""
        if self._module_gen is None:
            from .module_generation_service import FBSModuleGeneratorEngine
            # Initialize with Discovery integration
            self._module_gen = FBSModuleGeneratorEngine(
                odoo_service=self.odoo,
                license_service=None,  # Can be added later
                dms_service=None,      # Can be added later
                discovery_service=self.discovery  # ← INTEGRATION!
            )
        return self._module_gen

    async def get_solution_info(self) -> Dict[str, Any]:
        """Get solution information - PRESERVED from Django"""
        info = {
            'solution_name': self.solution_name,
            'timestamp': datetime.now().isoformat(),
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
                'discovery': 'Odoo model discovery',
                'module_gen': 'Automated module generation',
                'integrated_workflows': 'Discovery + Generation workflows',
                'cache': 'Cache management'
            }
        }

        # Add license information (PRESERVED from Django)
        if self._licensing_available and self.license_manager:
            info['license'] = await self.get_license_info()

        return info

    async def get_license_info(self) -> Dict[str, Any]:
        """Get comprehensive license information - PRESERVED from Django"""
        if self._licensing_available and self.license_manager:
            return self.license_manager.get_license_info()
        else:
            return {
                'license_type': 'unlimited',
                'status': 'active',
                'features': ['all_features'],
                'limits': {'unlimited': True},
                'source': 'unlimited'
            }

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status - PRESERVED from Django"""
        return {
            'solution_name': self.solution_name,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
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
                'module_gen': 'operational',  # NEW
                'discovery': 'operational',   # NEW
                'cache': 'operational'
            }
        }

    # ============================================================================
    # INTEGRATED WORKFLOWS: Discovery + Module Generation
    # ============================================================================

    async def discover_and_extend(self, user_id: str, tenant_id: str = None) -> Dict[str, Any]:
        """
        INTEGRATED WORKFLOW: Discover existing structures and generate extensions

        This combines Discovery and Module Generation into a unified workflow:
        1. Discover existing Odoo models and fields
        2. Generate extension modules based on findings
        3. Install extensions in the solution database

        Args:
            user_id: User performing the operation
            tenant_id: Target tenant (defaults to solution_name)

        Returns:
            Complete workflow result
        """
        tenant_id = tenant_id or self.solution_name

        workflow_result = {
            'workflow_type': 'discover_and_extend',
            'tenant_id': tenant_id,
            'phases': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Phase 1: Discovery
            workflow_result['phases']['discovery'] = {
                'status': 'running',
                'message': 'Discovering existing Odoo structures'
            }

            discovery_result = await self.discovery.discover_models(self.odoo_db_name)
            workflow_result['phases']['discovery'] = {
                'status': 'completed',
                'result': discovery_result
            }

            # Phase 2: Module Generation from Discovery
            workflow_result['phases']['generation'] = {
                'status': 'running',
                'message': 'Generating extension modules from discovery findings'
            }

            generation_result = await self.module_gen.generate_from_discovery(
                discovery_result, user_id, tenant_id
            )
            workflow_result['phases']['generation'] = {
                'status': 'completed',
                'result': generation_result
            }

            # Phase 3: Installation
            workflow_result['phases']['installation'] = {
                'status': 'running',
                'message': 'Installing generated modules'
            }

            install_results = []
            for module in generation_result.get('modules', []):
                if 'zip_content' in module:
                    install_result = await self.module_gen.generate_and_install(
                        ModuleSpec(name=module['module_name']), user_id, tenant_id
                    )
                    install_results.append(install_result)

            workflow_result['phases']['installation'] = {
                'status': 'completed',
                'results': install_results
            }

            workflow_result['overall_status'] = 'success'
            workflow_result['message'] = f'Successfully completed integrated workflow for {tenant_id}'

        except Exception as e:
            workflow_result['overall_status'] = 'failed'
            workflow_result['error'] = str(e)
            workflow_result['message'] = f'Integrated workflow failed: {str(e)}'

        return workflow_result

    async def hybrid_extension_workflow(self, base_model: str, custom_fields: List[Dict], user_id: str, tenant_id: str = None) -> Dict[str, Any]:
        """
        HYBRID WORKFLOW: Combine virtual fields (immediate) + module generation (structured)

        This provides both approaches in one workflow:
        1. Immediate virtual field extensions for rapid development
        2. Structured module generation for production-ready extensions

        Args:
            base_model: Odoo model to extend (e.g., 'res.partner')
            custom_fields: List of custom fields to add
            user_id: User performing the operation
            tenant_id: Target tenant

        Returns:
            Hybrid workflow result
        """
        tenant_id = tenant_id or self.solution_name

        result = {
            'workflow_type': 'hybrid_extension',
            'base_model': base_model,
            'tenant_id': tenant_id,
            'phases': {},
            'timestamp': datetime.now().isoformat()
        }

        try:
            # Phase 1: Virtual Fields (Immediate)
            result['phases']['virtual_fields'] = {
                'status': 'running',
                'message': f'Adding virtual fields to {base_model}'
            }

            virtual_results = []
            for field in custom_fields:
                field_result = await self.fields.set_custom_field(
                    base_model, 0, field['name'], field.get('default', ''),
                    field.get('type', 'char'), self.fastapi_db_name
                )
                virtual_results.append(field_result)

            result['phases']['virtual_fields'] = {
                'status': 'completed',
                'results': virtual_results
            }

            # Phase 2: Module Generation (Structured)
            result['phases']['module_generation'] = {
                'status': 'running',
                'message': f'Generating structured module for {base_model}'
            }

            module_spec = ModuleSpec(
                name=f"{base_model.replace('.', '_')}_structured_extension",
                description=f"Structured extension for {base_model}",
                author="FBS Hybrid Workflow",
                models=[{
                    'name': f"{base_model}.structured",
                    'inherit_from': base_model,
                    'description': f"Structured extension of {base_model}",
                    'fields': custom_fields
                }],
                security={
                    'rules': [{
                        'name': f'{base_model} Extension Access',
                        'model': f"{base_model}.structured",
                        'permissions': ['read', 'write', 'create']
                    }]
                },
                tenant_id=tenant_id
            )

            generation_result = await self.module_gen.generate_module(
                module_spec, user_id, tenant_id
            )

            result['phases']['module_generation'] = {
                'status': 'completed',
                'result': generation_result
            }

            result['overall_status'] = 'success'
            result['message'] = f'Hybrid extension completed for {base_model}'

        except Exception as e:
            result['overall_status'] = 'failed'
            result['error'] = str(e)
            result['message'] = f'Hybrid workflow failed: {str(e)}'

        return result

# ============================================================================
# SERVICE IMPLEMENTATION BASE CLASSES
# ============================================================================

class BaseService(ABC):
    """Base service class with common functionality"""

    def __init__(self, solution_name: str):
        self.solution_name = solution_name

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        pass

class AsyncServiceMixin:
    """Mixin for async service operations"""

    async def _safe_execute(self, operation, *args, **kwargs) -> Dict[str, Any]:
        """Safely execute service operations with error handling"""
        try:
            return await operation(*args, **kwargs)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Operation failed: {operation.__name__}'
            }

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Protocols
    'MSMEInterfaceProtocol',
    'BusinessIntelligenceInterfaceProtocol',
    'WorkflowInterfaceProtocol',
    'ComplianceInterfaceProtocol',
    'AuthInterfaceProtocol',
    'OnboardingInterfaceProtocol',
    'DiscoveryInterfaceProtocol',
    'SignalsInterfaceProtocol',
    'AccountingInterfaceProtocol',
    'VirtualFieldsInterfaceProtocol',
    'OdooInterfaceProtocol',
    'NotificationInterfaceProtocol',

    # Main Interface
    'FBSInterface',

    # Base Classes
    'BaseService',
    'AsyncServiceMixin'
]
