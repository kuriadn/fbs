"""
FBS FastAPI Models Package

Centralized import for all SQLAlchemy models.
"""

# Core FBS models - import only when needed to avoid conflicts
# from .models import *

# DMS models - import only when needed to avoid conflicts
# from .dms_models import *

# License Manager models - import only when needed to avoid conflicts
# from .license_models import *

# Export all models for easy importing
__all__ = [
    # Core models
    "Base",
    "BusinessEntity",
    "BusinessEntityCreate",
    "BusinessEntityResponse",
    "User",
    "Role",
    "Permission",
    "AuditLog",
    "SystemConfig",
    "Notification",
    "CacheEntry",
    "TokenMapping",
    "Handshake",
    "RequestLog",
    "BusinessRule",
    "ApprovalRequest",
    "ApprovalResponse",
    "CustomField",

    # MSME models
    "MSMESetupWizard",
    "MSMEKPI",
    "MSMECompliance",
    "MSMEMarketing",
    "MSMETemplate",
    "MSMEAnalytics",

    # BI models
    "Dashboard",
    "Report",
    "KPI",
    "Chart",
    "BusinessMetric",

    # Workflow models
    "WorkflowDefinition",
    "WorkflowInstance",
    "WorkflowStep",
    "WorkflowTransition",
    "WorkflowExecutionLog",

    # Odoo models
    "OdooDatabase",
    "OdooModel",
    "OdooField",
    "OdooModule",
    "DiscoverySession",

    # DMS models
    "DMSDocumentType",
    "DMSDocumentCategory",
    "DMSDocumentTag",
    "DMSFileAttachment",
    "DMSDocument",
    "DMSDocumentWorkflow",
    "DMSDocumentApproval",

    # License Manager models
    "SolutionLicense",
    "FeatureUsage",
    "LicenseAuditLog",
    "UpgradeRecommendation",
    "LicenseType",
    "LicenseStatus",
    "FeatureUsageStatus"
]
