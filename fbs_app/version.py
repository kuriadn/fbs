"""
FBS Version Information

This module provides version information for the FBS application.
"""

__version__ = '2.0.6'
__version_info__ = (2, 0, 6)
__release_date__ = '2025-01-06'
__release_type__ = 'Critical Hotfix - Rental Integration Issues'

# Version history
VERSION_HISTORY = {
    '2.0.4': {
        'date': '2025-08-29',
        'type': 'Major Update & Bug Fixes',
        'changes': [
            'Consistent model naming convention implemented',
            'DMS models prefixed with DMS_',
            'License models prefixed with LIC_',
            'Simplified database architecture',
            'All services updated for consistency'
        ]
    },
    '2.0.3': {
        'date': '2025-08-28',
        'type': 'Major Update & Bug Fixes',
        'changes': [
            'Complete MSME backend implementation',
            'All 7 migration files created',
            'Signal safety improvements',
            'Comprehensive testing suite',
            'Professional-grade services'
        ]
    },
    '2.0.2': {
        'date': '2025-08-19',
        'type': 'Initial Release',
        'changes': [
            'Basic FBS functionality',
            'Core models and services',
            'Odoo integration framework'
        ]
    }
}

def get_version():
    """Get the current version string"""
    return __version__

def get_version_info():
    """Get the current version tuple"""
    return __version_info__

def get_release_info():
    """Get release information"""
    return {
        'version': __version__,
        'version_info': __version_info__,
        'release_date': __release_date__,
        'release_type': __release_type__
    }

def is_compatible_with(required_version):
    """Check if current version is compatible with required version"""
    current = __version_info__
    required = tuple(map(int, required_version.split('.')))
    
    # Major version must match
    if current[0] != required[0]:
        return False
    
    # Minor version must be >= required
    if current[1] < required[1]:
        return False
    
    # Patch version must be >= required
    if current[1] == required[1] and current[2] < required[2]:
        return False
    
    return True
