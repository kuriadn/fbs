"""
FBS App Services Package

Core services for business logic and external integrations.
"""

from .odoo_client import OdooClient, OdooClientError
from .auth_service import AuthService
from .cache_service import CacheService
from .discovery_service import DiscoveryService
from .workflow_service import WorkflowService
from .onboarding_service import OnboardingService
from .msme_service import MSMEService
from .business_logic_service import BusinessLogicService
from .bi_service import BusinessIntelligenceService
from .compliance_service import ComplianceService
from .notification_service import NotificationService
from .simple_accounting_service import SimpleAccountingService
from .service_generator import FBSServiceGenerator
from .database_service import DatabaseService
from .field_merger_service import FieldMergerService

__all__ = [
    'OdooClient',
    'OdooClientError', 
    'AuthService',
    'CacheService',
    'DiscoveryService',
    'WorkflowService',
    'OnboardingService',
    'MSMEService',
    'BusinessLogicService',
    'BusinessIntelligenceService',
    'ComplianceService',
    'NotificationService',
    'SimpleAccountingService',
    'FBSServiceGenerator',
    'DatabaseService',
    'FieldMergerService',
]
