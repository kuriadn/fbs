"""
FBS License Manager

A standalone, embeddable licensing solution that can be used
with or without the core FBS app.
"""

from .services import EmbeddedLicenseEngine, FeatureFlags, UpgradePrompts

# Main interface - start with embedded engine
LicenseManager = EmbeddedLicenseEngine

__version__ = '1.0.0'
__author__ = 'FBS Team'
__description__ = 'Enterprise-grade licensing system for Django applications'

__all__ = [
    'LicenseManager',
    'EmbeddedLicenseEngine',
    'FeatureFlags',
    'UpgradePrompts'
]
