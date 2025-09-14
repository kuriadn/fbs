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
    'DatabaseService'
]
