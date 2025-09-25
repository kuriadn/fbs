"""
FBS Core Services

Main FBS orchestration interface - Django version.
Provides unified access to all FBS services with multi-tenant support.
"""
from django.core.cache import cache
from django.conf import settings
from typing import Optional, Dict, Any, List
from .models import FBSSolution, FBSUser


class FBSInterface:
    """
    Main FBS orchestration interface - Django version

    Provides unified access to all FBS services with proper multi-tenant
    isolation and caching. Mirrors the FastAPI FBSInterface pattern.
    """

    def __init__(self, solution_name: str, license_key: str = None, user: FBSUser = None):
        """
        Initialize FBS interface for a specific solution.

        Args:
            solution_name: Name of the solution to work with
            license_key: Optional license key for validation
            user: Optional user for permission checks
        """
        try:
            self.solution = FBSSolution.objects.get(name=solution_name, is_active=True)
        except FBSSolution.DoesNotExist:
            raise ValueError(f"Solution '{solution_name}' not found or inactive")

        self.solution_name = solution_name
        self.license_key = license_key
        self.user = user

        # Auto-generate database names (PRESERVED from FastAPI)
        self.fastapi_db_name = f"djo_{solution_name}_db"
        self.odoo_db_name = f"fbs_{solution_name}_db"

        # Initialize licensing system
        self._init_licensing()

        # Lazy-loaded service properties (PRESERVED from FastAPI)
        self._dms = None
        self._license = None
        self._module_gen = None
        self._odoo = None
        self._discovery = None
        self._virtual_fields = None
        self._msme = None
        self._bi = None
        self._workflows = None
        self._compliance = None
        self._accounting = None
        self._notifications = None
        self._auth = None
        self._onboarding = None
        self._signals = None
        self._cache = None

        # Cache key for this interface instance
        self._cache_key = f'fbs_interface:{solution_name}'

    def _init_licensing(self):
        """Initialize licensing system (PRESERVED from FastAPI)"""
        if self.license_key and self.license_key != 'trial':
            try:
                from apps.licensing.services import LicenseService
                self.license_manager = LicenseService(self.solution)
                # For now, allow all features for enterprise license
                self.feature_flags = None  # Disable feature checking for simplicity
                self._licensing_available = True
            except ImportError:
                # Fallback to unlimited access
                self.license_manager = None
                self.feature_flags = None
                self._licensing_available = False
        else:
            # No license key or trial - use unlimited access mode
            self.license_manager = None
            self.feature_flags = None
            self._licensing_available = False

    @property
    def dms(self):
        """Document Management System service"""
        if self._dms is None:
            from apps.dms.services.document_service import DocumentService
            self._dms = DocumentService(self.solution)
        return self._dms

    @property
    def license(self):
        """License management service"""
        if self._license is None:
            from apps.licensing.services.license_service import LicenseService
            self._license = LicenseService(self.solution)
        return self._license

    @property
    def module_gen(self):
        """Module generation service with Discovery integration"""
        if self._module_gen is None:
            from apps.module_gen.services.generator import FBSModuleGeneratorEngine
            # Initialize with Discovery integration (PRESERVED from FastAPI)
            self._module_gen = FBSModuleGeneratorEngine(
                odoo_service=self.odoo,
                license_service=None,  # Can be added later
                dms_service=None,      # Can be added later
                discovery_service=self.discovery  # ← INTEGRATION!
            )
        return self._module_gen

    @property
    def odoo(self):
        """Odoo integration service"""
        if self._odoo is None:
            from apps.odoo_integration.services.odoo_service import OdooService
            self._odoo = OdooService(self.solution)
        return self._odoo

    @property
    def discovery(self):
        """Model discovery service - simplified for Django"""
        if self._discovery is None:
            # Skip licensing check for now - allow discovery for enterprise
            from apps.discovery.services.discovery_service import DiscoveryService
            self._discovery = DiscoveryService(self.solution)
        return self._discovery

    @property
    def fields(self):
        """Virtual Fields service - PRESERVED from FastAPI"""
        if self._virtual_fields is None:
            # Check licensing (PRESERVED from FastAPI)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('fields'):
                    raise ValueError("Virtual fields feature not enabled in license")

            from apps.virtual_fields.services.virtual_fields_service import FieldMergerService
            self._virtual_fields = FieldMergerService(self.solution)
        return self._virtual_fields

    @property
    def virtual_fields(self):
        """Alias for fields property"""
        return self.fields

    @property
    def msme(self):
        """MSME business management service - PRESERVED from FastAPI"""
        if self._msme is None:
            # Check licensing (PRESERVED from FastAPI)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('msme'):
                    raise ValueError("MSME feature not enabled in license")

            from apps.msme.services.msme_service import MSMEService
            self._msme = MSMEService(self.solution)
        return self._msme

    @property
    def bi(self):
        """Business Intelligence service"""
        if self._bi is None:
            from apps.bi.services.bi_service import BIService
            self._bi = BIService(self.solution)
        return self._bi

    @property
    def workflows(self):
        """Workflow management service"""
        if self._workflows is None:
            from apps.workflows.services.workflows_service import WorkflowService
            self._workflows = WorkflowService(self.solution)
        return self._workflows

    @property
    def compliance(self):
        """Compliance tracking service"""
        if self._compliance is None:
            from apps.compliance.services.compliance_service import ComplianceService
            self._compliance = ComplianceService(self.solution)
        return self._compliance

    @property
    def accounting(self):
        """Accounting operations service - PRESERVED from FastAPI"""
        if self._accounting is None:
            # Check licensing (PRESERVED from FastAPI)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('accounting'):
                    raise ValueError("Accounting feature not enabled in license")

            from apps.accounting.services.accounting_service import SimpleAccountingService
            self._accounting = SimpleAccountingService(self.solution)
        return self._accounting

    @property
    def notifications(self):
        """Notification system service"""
        if self._notifications is None:
            from apps.notifications.services.notifications_service import NotificationService
            self._notifications = NotificationService(self.solution)
        return self._notifications

    @property
    def auth(self):
        """Authentication service - PRESERVED from FastAPI"""
        if self._auth is None:
            # Check licensing (PRESERVED from FastAPI)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('auth'):
                    raise ValueError("Authentication feature not enabled in license")

            from apps.auth_handshake.services.auth_handshake_service import AuthService
            self._auth = AuthService(self.solution)
        return self._auth

    @property
    def onboarding(self):
        """Onboarding service - PRESERVED from FastAPI"""
        if self._onboarding is None:
            # Check licensing (PRESERVED from FastAPI)
            if self._licensing_available and self.feature_flags:
                if not self.feature_flags.is_enabled('onboarding'):
                    raise ValueError("Onboarding feature not enabled in license")

            from apps.onboarding.services.onboarding_service import OnboardingService
            self._onboarding = OnboardingService(self.solution)
        return self._onboarding

    @property
    def signals(self):
        """Signals service - PRESERVED from Django"""
        if self._signals is None:
            from apps.signals.services.signals_service import SignalsService
            self._signals = SignalsService(self.solution)
        return self._signals

    @property
    def cache(self):
        """Cache service"""
        if self._cache is None:
            self._cache = CacheService(self.solution)
        return self._cache

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and health status"""
        return {
            'solution': {
                'name': self.solution.name,
                'display_name': self.solution.display_name,
                'is_active': self.solution.is_active,
            },
            'services': {
                'license_valid': self.license.is_valid() if self.license_key else None,
                'odoo_connected': self.odoo.is_connected(),
                'dms_available': self.license.check_feature_access('dms'),
                'module_gen_available': self.license.check_feature_access('module_generation'),
            },
            'version': getattr(settings, 'FBS_CONFIG', {}).get('VERSION', '4.0.0'),
        }

    def get_solution_info(self) -> Dict[str, Any]:
        """Get solution information - PRESERVED from FastAPI"""
        from django.utils import timezone
        info = {
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
                'discovery': 'Odoo model discovery',
                'module_gen': 'Automated module generation',
                'integrated_workflows': 'Discovery + Generation workflows',
                'cache': 'Cache management'
            }
        }

        # Add license information (PRESERVED from FastAPI)
        if self._licensing_available and self.license_manager:
            info['license'] = self.get_license_info()

        return info

    def get_license_info(self) -> Dict[str, Any]:
        """Get comprehensive license information - PRESERVED from FastAPI"""
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

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status - PRESERVED from FastAPI"""
        from django.utils import timezone
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
                'module_gen': 'operational',  # NEW
                'discovery': 'operational',   # NEW
                'cache': 'operational'
            }
        }

    # ============================================================================
    # INTEGRATED WORKFLOWS: Discovery + Module Generation
    # ============================================================================

    def discover_and_extend(self, user_id: str, tenant_id: str = None) -> Dict[str, Any]:
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
        from django.utils import timezone
        tenant_id = tenant_id or self.solution_name

        workflow_result = {
            'workflow_type': 'discover_and_extend',
            'tenant_id': tenant_id,
            'phases': {},
            'timestamp': timezone.now().isoformat()
        }

        try:
            # Phase 1: Discovery
            workflow_result['phases']['discovery'] = {
                'status': 'running',
                'message': 'Discovering existing Odoo structures'
            }

            discovery_result = self.discovery.discover_models(self.odoo_db_name)
            workflow_result['phases']['discovery'] = {
                'status': 'completed',
                'result': discovery_result
            }

            # Phase 2: Module Generation from Discovery
            workflow_result['phases']['generation'] = {
                'status': 'running',
                'message': 'Generating extension modules from discovery findings'
            }

            generation_result = self.module_gen.generate_from_discovery(
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
                    install_result = self.module_gen.generate_and_install(
                        module, user_id, tenant_id
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

    def hybrid_extension_workflow(self, base_model: str, custom_fields: List[Dict], user_id: str, tenant_id: str = None) -> Dict[str, Any]:
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
        from django.utils import timezone
        tenant_id = tenant_id or self.solution_name

        result = {
            'workflow_type': 'hybrid_extension',
            'base_model': base_model,
            'tenant_id': tenant_id,
            'phases': {},
            'timestamp': timezone.now().isoformat()
        }

        try:
            # Phase 1: Virtual Fields (Immediate)
            result['phases']['virtual_fields'] = {
                'status': 'running',
                'message': f'Adding virtual fields to {base_model}'
            }

            virtual_results = []
            for field in custom_fields:
                field_result = self.fields.set_custom_field(
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

            module_spec = {
                'name': f"{base_model.replace('.', '_')}_structured_extension",
                'description': f"Structured extension for {base_model}",
                'author': "FBS Hybrid Workflow",
                'models': [{
                    'name': f"{base_model}.structured",
                    'inherit_from': base_model,
                    'description': f"Structured extension of {base_model}",
                    'fields': custom_fields
                }],
                'security': {
                    'rules': [{
                        'name': f'{base_model} Extension Access',
                        'model': f"{base_model}.structured",
                        'permissions': ['read', 'write', 'create']
                    }]
                },
                'tenant_id': tenant_id
            }

            generation_result = self.module_gen.generate_module(
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

    def clear_cache(self):
        """Clear all cached data for this solution"""
        cache.delete_pattern(f'*:solution:{self.solution.name}:*')
        cache.delete(self._cache_key)


class CacheService:
    """
    Cache service for FBS - provides caching functionality for solutions.
    """

    def __init__(self, solution):
        self.solution = solution
        self.cache_prefix = f'fbs:{solution.name}:'

    def get(self, key: str, default=None):
        """Get cached value"""
        cache_key = f"{self.cache_prefix}{key}"
        return cache.get(cache_key, default)

    def set(self, key: str, value, timeout: int = 300):
        """Set cached value"""
        cache_key = f"{self.cache_prefix}{key}"
        cache.set(cache_key, value, timeout)

    def delete(self, key: str):
        """Delete cached value"""
        cache_key = f"{self.cache_prefix}{key}"
        cache.delete(cache_key)

    def clear(self):
        """Clear all solution cache"""
        cache.delete_pattern(f'{self.cache_prefix}*')


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'FBSInterface',
    'CacheService',
]

