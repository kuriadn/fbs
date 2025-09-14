"""
FBS FastAPI License Manager

PRESERVED from Django fbs_license_manager/services.py
Core business logic for license management, feature flags, and upgrade prompts.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger('fbs_license_manager')


class EmbeddedLicenseEngine:
    """Local, embedded license management engine - PRESERVED from Django"""

    def __init__(self, solution_name: str, license_key: str = None):
        self.solution_name = solution_name
        self.license_key = license_key or self._get_default_license()
        self._license_data = None
        self._features = None

        # Load license data
        self._load_license_data()

    def _get_default_license(self) -> str:
        """Get default license from environment or generate trial - PRESERVED from Django"""
        # Get from FastAPI config
        from ..core.config import config
        return getattr(config, 'fbs_license_type', 'trial')

    def _load_license_data(self):
        """Load license data from multiple sources - PRESERVED from Django"""
        try:
            # Priority 1: Environment variables
            env_license = self._load_from_environment()
            if env_license:
                self._license_data = env_license
                return

            # Priority 2: Default trial
            self._license_data = self._generate_license_data(self.license_key)

        except Exception as e:
            logger.error(f"Failed to load license data: {e}")
            # Fallback to trial license
            self._license_data = self._generate_license_data('trial')

    def _load_from_environment(self) -> Optional[Dict[str, Any]]:
        """Load license data from environment variables - PRESERVED from Django"""
        # Get from FastAPI config
        from ..core.config import config

        license_type = getattr(config, 'fbs_license_type', None)
        if not license_type:
            return None

        features = []
        limits = {}

        # Load features from FastAPI config
        if getattr(config, 'fbs_enable_msme_features', False):
            features.append('msme')
        if getattr(config, 'fbs_enable_bi_features', False):
            features.append('bi')
        if getattr(config, 'fbs_enable_workflow_features', False):
            features.append('workflows')
        if getattr(config, 'fbs_enable_compliance_features', False):
            features.append('compliance')
        if getattr(config, 'fbs_enable_notifications', True):
            features.append('notifications')

        # Load limits from FastAPI config
        limits['msme_businesses'] = getattr(config, 'fbs_msme_businesses_limit', 5)
        limits['workflows'] = getattr(config, 'fbs_workflows_limit', 10)
        limits['reports'] = getattr(config, 'fbs_reports_limit', 100)
        limits['users'] = getattr(config, 'fbs_users_limit', 5)

        return {
            'type': license_type,
            'features': features,
            'limits': limits,
            'status': 'active',
            'source': 'environment'
        }

    def _generate_license_data(self, license_type: str) -> Dict[str, Any]:
        """Generate license data based on type - PRESERVED from Django"""
        base_features = ['msme', 'odoo']
        base_limits = {
            'users': 5,
            'reports': 50,
            'workflows': 5
        }

        if license_type == 'trial':
            return {
                'type': 'trial',
                'features': base_features,
                'limits': base_limits,
                'status': 'active',
                'source': 'generated'
            }
        elif license_type == 'basic':
            return {
                'type': 'basic',
                'features': base_features + ['bi', 'workflows'],
                'limits': {k: v * 2 for k, v in base_limits.items()},
                'status': 'active',
                'source': 'generated'
            }
        elif license_type == 'premium':
            return {
                'type': 'premium',
                'features': base_features + ['bi', 'workflows', 'compliance', 'notifications'],
                'limits': {k: v * 5 for k, v in base_limits.items()},
                'status': 'active',
                'source': 'generated'
            }
        else:  # enterprise or unlimited
            return {
                'type': 'enterprise',
                'features': ['all'],
                'limits': {'unlimited': True},
                'status': 'active',
                'source': 'generated'
            }

    def get_license_info(self) -> Dict[str, Any]:
        """Get license information - PRESERVED from Django"""
        return self._license_data or {}

    def has_feature(self, feature_name: str) -> bool:
        """Check if feature is available - PRESERVED from Django"""
        if not self._license_data:
            return False

        features = self._license_data.get('features', [])
        return feature_name in features or 'all' in features

    def get_feature_limit(self, feature_name: str) -> int:
        """Get limit for a feature - PRESERVED from Django"""
        if not self._license_data:
            return 0

        limits = self._license_data.get('limits', {})
        if limits.get('unlimited'):
            return -1

        return limits.get(feature_name, 0)

    def get_available_features(self) -> List[str]:
        """Get list of available features - PRESERVED from Django"""
        if not self._license_data:
            return []

        return self._license_data.get('features', [])

    def is_license_valid(self) -> bool:
        """Check if license is valid - PRESERVED from Django"""
        if not self._license_data:
            return False

        return self._license_data.get('status') == 'active'

    def get_license_type(self) -> str:
        """Get license type - PRESERVED from Django"""
        if not self._license_data:
            return 'none'

        return self._license_data.get('type', 'none')


class FeatureFlags:
    """Feature availability management based on license - PRESERVED from Django"""

    def __init__(self, solution_name: str, license_manager):
        self.solution_name = solution_name
        self.license_manager = license_manager

    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled - PRESERVED from Django"""
        if not self.license_manager:
            return True  # No license manager means unlimited access

        return self.license_manager.has_feature(feature_name)

    def get_enabled_features(self) -> List[str]:
        """Get list of enabled features - PRESERVED from Django"""
        if not self.license_manager:
            return []  # No license manager means no specific features

        return self.license_manager.get_available_features()

    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """Get configuration for a specific feature - PRESERVED from Django"""
        if not self.license_manager:
            return {'enabled': True, 'unlimited': True}

        limit = self.license_manager.get_feature_limit(feature_name)
        return {
            'enabled': self.license_manager.has_feature(feature_name),
            'limit': limit,
            'unlimited': limit == -1
        }

    async def check_feature_access(self, feature_name: str, **kwargs) -> Dict[str, Any]:
        """Check if user can access a feature with current usage - PRESERVED from Django"""
        if not self.is_enabled(feature_name):
            return {
                'access': False,
                'reason': 'feature_disabled',
                'upgrade_required': True,
                'feature_name': feature_name
            }

        if not self.license_manager:
            # No license manager means unlimited access
            return {
                'access': True,
                'remaining': -1,
                'limit': -1,
                'feature_name': feature_name
            }

        limit = self.license_manager.get_feature_limit(feature_name)
        if limit == -1:  # Unlimited
            return {
                'access': True,
                'remaining': -1,
                'limit': -1,
                'feature_name': feature_name
            }

        # Implement usage tracking with database storage
        try:
            from ..models.models import FeatureUsage
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Record usage in database
                usage_record = FeatureUsage(
                    solution_name=self.solution_name,
                    feature_name=feature_name,
                    usage_count=kwargs.get('current_usage', 0),
                    timestamp=datetime.now()
                )
                db.add(usage_record)
                await db.commit()

        except Exception as e:
            logger.warning(f"Failed to track usage for {feature_name}: {e}")

        current_usage = kwargs.get('current_usage', 0)

        if current_usage >= limit:
            return {
                'access': False,
                'reason': 'limit_exceeded',
                'upgrade_required': True,
                'current_usage': current_usage,
                'limit': limit,
                'remaining': 0,
                'feature_name': feature_name
            }

        return {
            'access': True,
            'remaining': limit - current_usage,
            'limit': limit,
            'current_usage': current_usage,
            'feature_name': feature_name
        }

    def track_usage(self, feature_name: str, usage_count: int = 1) -> Dict[str, Any]:
        """Track feature usage for billing/analytics"""
        try:
            # In a real implementation, this would store usage data
            # For now, we'll just log the usage
            logger.info(f"Feature '{feature_name}' used {usage_count} times")

            return {
                'success': True,
                'feature_name': feature_name,
                'usage_count': usage_count,
                'message': 'Usage tracked successfully'
            }
        except Exception as e:
            logger.error(f"Error tracking usage for {feature_name}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to track usage'
            }


class LicenseManager:
    """Manages license information and feature access for a solution - PRESERVED from Django"""

    def __init__(self, solution_name: str, license_key: str = None, solution_db: str = None):
        self.solution_name = solution_name
        self.license_key = license_key
        self.solution_db = solution_db or f"fpi_{solution_name}_db"

        # Get license information
        self.license_info = self._get_license_info()
        self.feature_flags = FeatureFlags(solution_name, self)

    def _get_license_info(self) -> Dict[str, Any]:
        """Get license information for the solution - PRESERVED from Django"""
        try:
            # Use embedded license engine
            engine = EmbeddedLicenseEngine(self.solution_name, self.license_key)
            return engine.get_license_info()

        except Exception as e:
            logger.error(f"Failed to get license info: {e}")
            # Return basic trial license
            return {
                'type': 'trial',
                'features': ['msme', 'odoo'],
                'limits': {'users': 5, 'reports': 50},
                'status': 'active',
                'source': 'fallback'
            }

    def has_feature(self, feature_name: str) -> bool:
        """Check if feature is available - PRESERVED from Django"""
        return self.license_info and feature_name in self.license_info.get('features', [])

    def get_feature_limit(self, feature_name: str) -> int:
        """Get limit for a feature - PRESERVED from Django"""
        if not self.license_info:
            return 0

        limits = self.license_info.get('limits', {})
        if limits.get('unlimited'):
            return -1

        return limits.get(feature_name, 0)

    def get_available_features(self) -> List[str]:
        """Get list of available features - PRESERVED from Django"""
        if not self.license_info:
            return []

        return self.license_info.get('features', [])

    def is_license_valid(self) -> bool:
        """Check if license is valid - PRESERVED from Django"""
        if not self.license_info:
            return False

        return self.license_info.get('status') == 'active'

    def get_license_info(self) -> Dict[str, Any]:
        """Get comprehensive license information - PRESERVED from Django"""
        return {
            'solution_name': self.solution_name,
            'license_type': self.license_info.get('type', 'none'),
            'status': self.license_info.get('status', 'inactive'),
            'features': self.get_available_features(),
            'limits': self.license_info.get('limits', {}),
            'source': self.license_info.get('source', 'unknown'),
            'valid': self.is_license_valid()
        }
