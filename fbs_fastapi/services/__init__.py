"""
FBS FastAPI Services Package

Core business services implementing the service interface architecture pattern.
Preserves the clean service-based architecture from Django while modernizing with FastAPI.
"""

from .business_service import BusinessService
from .msme_service import MSMEService
from .odoo_service import OdooService
from .bi_service import BIService
from .workflow_service import WorkflowService
from .compliance_service import ComplianceService
from .accounting_service import SimpleAccountingService
from .notification_service import NotificationService
from .cache_service import CacheService
from .onboarding_service import OnboardingService
from .database_service import DatabaseService
from .auth_service import AuthService
from .discovery_service import DiscoveryService
from .dms_service import DocumentService as DMSService
from .field_merger_service import FieldMergerService
from .license_manager import LicenseManager
from .license_service import LicenseService
from .module_generation_service import FBSModuleGeneratorEngine, ModuleSpec
from .signals_service import SignalsService

# Import service interfaces
from .service_interfaces import FBSInterface

__all__ = [
    # Core Services (PRESERVED from Django)
    'BusinessService',
    'MSMEService',
    'OdooService',
    'BIService',
    'WorkflowService',
    'ComplianceService',
    'SimpleAccountingService',
    'NotificationService',
    'CacheService',
    'OnboardingService',
    'DatabaseService',

    # Additional Services
    'AuthService',
    'DiscoveryService',
    'DMSService',
    'FieldMergerService',
    'LicenseManager',
    'LicenseService',
    'SignalsService',

    # Module Generation
    'FBSModuleGeneratorEngine',
    'ModuleSpec',

    # Main Interface
    'FBSInterface'
]
