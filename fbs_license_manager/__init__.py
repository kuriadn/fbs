"""
FBS License Manager

A standalone, embeddable licensing solution that can be used
with or without the core FBS app.
"""

# Import services conditionally to avoid circular imports during Django startup
try:
    from .services import EmbeddedLicenseEngine, FeatureFlags, UpgradePrompts, OdooLicenseService
    
    # Main interface - start with embedded engine
    LicenseManager = EmbeddedLicenseEngine
    
    __all__ = [
        'LicenseManager',
        'EmbeddedLicenseEngine',
        'FeatureFlags',
        'UpgradePrompts',
        'OdooLicenseService'
    ]
except ImportError:
    # Django not ready yet, provide placeholder
    LicenseManager = None
    EmbeddedLicenseEngine = None
    FeatureFlags = None
    UpgradePrompts = None
    OdooLicenseService = None
    
    __all__ = [
        'LicenseManager',
        'EmbeddedLicenseEngine',
        'FeatureFlags',
        'UpgradePrompts',
        'OdooLicenseService'
    ]

__version__ = '2.0.4'
__author__ = 'FBS Team'
__description__ = 'Enterprise-grade licensing system for Django applications'
