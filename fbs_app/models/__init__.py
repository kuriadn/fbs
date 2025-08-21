"""
FBS App Models Package

Central import for all models within the fbs_app.models package.
Organizes models into logical sub-modules for better maintainability.
"""

# Core models
from .core import (
    OdooDatabase,
    TokenMapping,
    RequestLog,
    BusinessRule,
    CacheEntry,
    Handshake,
    Notification,
    ApprovalRequest,
    ApprovalResponse,
    CustomField,
)

# MSME-specific models
from .msme import (
    MSMESetupWizard,
    MSMEKPI,
    MSMECompliance,
    MSMEMarketing,
    MSMETemplate,
    MSMEAnalytics,
)

# Odoo discovery models
from .discovery import (
    OdooModel,
    OdooField,
    OdooModule,
    DiscoverySession,
)

# Workflow models
from .workflows import (
    WorkflowDefinition,
    WorkflowInstance,
    WorkflowStep,
    WorkflowTransition,
)

# Business Intelligence models
from .bi import (
    Dashboard,
    Report,
    KPI,
    Chart,
)

# Compliance models
from .compliance import (
    ComplianceRule,
    AuditTrail,
    ReportSchedule,
    RecurringTransaction,
    UserActivityLog,
)

# Basic accounting models
from .accounting import (
    CashEntry,
    IncomeExpense,
    BasicLedger,
    TaxCalculation,
)

# Export all models
__all__ = [
    # Core
    'OdooDatabase',
    'TokenMapping',
    'RequestLog',
    'BusinessRule',
    'CacheEntry',
    'Handshake',
    'Notification',
    'ApprovalRequest',
    'ApprovalResponse',
    'CustomField',
    
    # MSME
    'MSMESetupWizard',
    'MSMEKPI',
    'MSMECompliance',
    'MSMEMarketing',
    'MSMETemplate',
    'MSMEAnalytics',
    
    # Discovery
    'OdooModel',
    'OdooField',
    'OdooModule',
    'DiscoverySession',
    
    # Workflows
    'WorkflowDefinition',
    'WorkflowInstance',
    'WorkflowStep',
    'WorkflowTransition',
    
    # BI
    'Dashboard',
    'Report',
    'KPI',
    'Chart',
    
    # Compliance
    'ComplianceRule',
    'AuditTrail',
    'ReportSchedule',
    'RecurringTransaction',
    'UserActivityLog',
    
    # Accounting
    'CashEntry',
    'IncomeExpense',
    'BasicLedger',
    'TaxCalculation',
]
