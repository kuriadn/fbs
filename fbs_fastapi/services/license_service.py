"""
FBS License Manager Service - FastAPI

License management service migrated from Django to FastAPI.
Provides enterprise-grade licensing, feature flags, and upgrade management.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .service_interfaces import BaseService, AsyncServiceMixin
from ..models.license_models import (
    SolutionLicense, FeatureUsage, LicenseAuditLog, UpgradeRecommendation,
    LicenseType, LicenseStatus, FeatureUsageStatus
)

logger = logging.getLogger('fbs_license_manager')


class LicenseService(BaseService, AsyncServiceMixin):
    """License management service - migrated from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)
        self._license_data = None
        self._features = None
        self._encryption_key = None

        # Initialize with default trial license
        self._license_data = self._generate_license_data('trial')

    def _get_default_license(self) -> str:
        """Get default license from environment or generate trial"""
        # Get from FastAPI config
        from ..core.config import config
        return getattr(config, 'fbs_license_type', 'trial')

    def _load_license_data(self):
        """Load license data from multiple sources - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            # Try to load from database first
            import asyncio
            asyncio.create_task(self._load_from_database())

        except Exception as e:
            logger.error(f"Error loading license data: {str(e)}")
            # Fallback to generated trial license
            self._license_data = self._generate_license_data('trial')

    async def _load_from_database(self):
        """Load license data from database - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                license_record = await db.query(SolutionLicense).filter(
                    SolutionLicense.solution_name == self.solution_name
                ).first()

                if license_record:
                    self._license_data = {
                        'type': license_record.license_type.value,
                        'license_key': license_record.license_key,
                        'expiry_date': license_record.expiry_date.isoformat() if license_record.expiry_date else None,
                        'features': license_record.get_features_list(),
                        'limits': license_record.get_limits_dict(),
                        'status': license_record.status.value,
                        'source': license_record.source
                    }
                else:
                    # Create default trial license
                    self._license_data = self._generate_license_data('trial')

        except Exception as e:
            logger.error(f"Error loading license from database: {str(e)}")
            self._license_data = self._generate_license_data('trial')

    def _generate_license_data(self, license_type: str) -> Dict[str, Any]:
        """Generate license data based on type - migrated from Django"""
        base_features = ['msme']
        base_limits = {
            'msme_businesses': 5,
            'workflows': 10,
            'reports': 100,
            'users': 5,
            'storage_gb': 1.0
        }

        if license_type == 'basic':
            features = ['msme', 'bi', 'workflows']
            limits = {
                'msme_businesses': 25,
                'workflows': 50,
                'reports': 1000,
                'users': 10,
                'storage_gb': 5.0
            }
        elif license_type == 'professional':
            features = ['msme', 'bi', 'workflows', 'compliance', 'accounting']
            limits = {
                'msme_businesses': 100,
                'workflows': 200,
                'reports': 10000,
                'users': 50,
                'storage_gb': 25.0
            }
        elif license_type == 'enterprise':
            features = ['msme', 'bi', 'workflows', 'compliance', 'accounting', 'dms', 'licensing', 'discovery']
            limits = {
                'msme_businesses': -1,  # Unlimited
                'workflows': -1,
                'reports': -1,
                'users': -1,
                'storage_gb': 100.0
            }
        else:  # trial
            features = ['msme']
            limits = {
                'msme_businesses': 1,
                'workflows': 2,
                'reports': 10,
                'users': 1,
                'storage_gb': 0.5
            }

        return {
            'type': license_type,
            'features': features,
            'limits': limits,
            'status': 'active',
            'source': 'generated'
        }

    async def get_license_info(self) -> Dict[str, Any]:
        """Get license information - migrated from Django"""
        try:
            if not self._license_data:
                await self._load_from_database()

            return {
                'success': True,
                'license': self._license_data,
                'solution_name': self.solution_name,
                'features_enabled': self._license_data.get('features', []),
                'limits': self._license_data.get('limits', {}),
                'is_trial': self._license_data.get('type') == 'trial',
                'is_expired': self._is_license_expired()
            }

        except Exception as e:
            logger.error(f"Error getting license info: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def check_feature_access(
        self,
        feature_name: str,
        current_usage: int = 0,
        **kwargs
    ) -> Dict[str, Any]:
        """Check feature access and usage limits - migrated from Django"""
        try:
            if not self._license_data:
                await self._load_from_database()

            # Check if feature is enabled
            features = self._license_data.get('features', [])
            if feature_name not in features:
                return {
                    'access': False,
                    'reason': 'feature_not_enabled',
                    'upgrade_required': True,
                    'current_usage': current_usage,
                    'limit': 0,
                    'remaining': 0,
                    'feature_name': feature_name
                }

            # Check usage limits
            limits = self._license_data.get('limits', {})
            limit = limits.get(feature_name, limits.get(f'{feature_name}s', 0))

            # Handle unlimited (-1)
            if limit == -1:
                return {
                    'access': True,
                    'remaining': -1,
                    'limit': -1,
                    'current_usage': current_usage,
                    'feature_name': feature_name
                }

            # Check if limit exceeded
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

            # Track usage
            await self._track_usage(feature_name, current_usage)

            return {
                'access': True,
                'remaining': limit - current_usage,
                'limit': limit,
                'current_usage': current_usage,
                'feature_name': feature_name
            }

        except Exception as e:
            logger.error(f"Error checking feature access: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def _track_usage(self, feature_name: str, usage_count: int):
        """Track feature usage - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Create or update usage record
                usage_record = await db.query(FeatureUsage).filter(
                    FeatureUsage.solution_name == self.solution_name,
                    FeatureUsage.feature_name == feature_name
                ).first()

                if usage_record:
                    usage_record.usage_count = max(usage_record.usage_count, usage_count)
                    usage_record.updated_at = datetime.utcnow()
                else:
                    usage_record = FeatureUsage(
                        solution_name=self.solution_name,
                        feature_name=feature_name,
                        usage_count=usage_count
                    )
                    db.add(usage_record)

                await db.commit()

        except Exception as e:
            logger.warning(f"Failed to track usage for {feature_name}: {str(e)}")

    async def get_upgrade_recommendations(self) -> Dict[str, Any]:
        """Get upgrade recommendations based on usage - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get current usage
                usage_records = await db.query(FeatureUsage).filter(
                    FeatureUsage.solution_name == self.solution_name
                ).all()

                recommendations = []
                limits = self._license_data.get('limits', {})

                for usage in usage_records:
                    limit = limits.get(usage.feature_name, limits.get(f'{usage.feature_name}s', 0))
                    if limit > 0 and usage.usage_count >= limit * 0.8:  # 80% usage threshold
                        recommendations.append({
                            'feature': usage.feature_name,
                            'current_usage': usage.usage_count,
                            'limit': limit,
                            'percentage': round((usage.usage_count / limit) * 100, 1),
                            'recommended_tier': self._get_recommended_tier(usage.feature_name)
                        })

                return {
                    'success': True,
                    'recommendations': recommendations,
                    'current_tier': self._license_data.get('type'),
                    'upgrade_available': len(recommendations) > 0
                }

        except Exception as e:
            logger.error(f"Error getting upgrade recommendations: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    def _get_recommended_tier(self, feature_name: str) -> str:
        """Get recommended tier for feature"""
        current_tier = self._license_data.get('type', 'trial')

        tier_progression = {
            'trial': 'basic',
            'basic': 'professional',
            'professional': 'enterprise',
            'enterprise': 'enterprise'
        }

        return tier_progression.get(current_tier, 'professional')

    def _is_license_expired(self) -> bool:
        """Check if license is expired"""
        expiry_date = self._license_data.get('expiry_date')
        if not expiry_date:
            return False

        try:
            expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
            return datetime.utcnow() > expiry
        except:
            return False

    async def create_license(
        self,
        license_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new license - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Create license record
                license_record = SolutionLicense(
                    solution_name=self.solution_name,
                    license_type=LicenseType(license_data.get('license_type', 'trial')),
                    license_key=license_data.get('license_key', self._generate_license_key()),
                    expiry_date=license_data.get('expiry_date'),
                    source=license_data.get('source', 'api')
                )

                # Set limits based on license type
                limits = self._generate_license_data(license_data.get('license_type', 'trial'))['limits']
                for key, value in limits.items():
                    if key == 'msme_businesses':
                        license_record.msme_businesses_limit = value
                    elif key == 'workflows':
                        license_record.workflows_limit = value
                    elif key == 'reports':
                        license_record.reports_limit = value
                    elif key == 'users':
                        license_record.users_limit = value
                    elif key == 'storage_gb':
                        license_record.storage_limit_gb = value

                # Set features based on license type
                features = self._generate_license_data(license_data.get('license_type', 'trial'))['features']
                for feature in features:
                    if feature == 'msme':
                        license_record.enable_msme = True
                    elif feature == 'bi':
                        license_record.enable_bi = True
                    elif feature == 'workflows':
                        license_record.enable_workflows = True
                    elif feature == 'compliance':
                        license_record.enable_compliance = True
                    elif feature == 'accounting':
                        license_record.enable_accounting = True
                    elif feature == 'dms':
                        license_record.enable_dms = True
                    elif feature == 'licensing':
                        license_record.enable_licensing = True

                db.add(license_record)
                await db.commit()
                await db.refresh(license_record)

                # Reload license data
                await self._load_from_database()

                # Log audit event
                await self._log_audit_event('create', license_data, {'license_id': license_record.id})

                return {
                    'success': True,
                    'license_id': license_record.id,
                    'license_key': license_record.license_key,
                    'message': 'License created successfully'
                }

        except Exception as e:
            logger.error(f"Error creating license: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    def _generate_license_key(self) -> str:
        """Generate license key"""
        import secrets
        return secrets.token_urlsafe(32)

    async def _log_audit_event(
        self,
        action: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        performed_by: Optional[str] = None
    ):
        """Log license audit event"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                audit_log = LicenseAuditLog(
                    solution_name=self.solution_name,
                    action=action,
                    old_value=old_value,
                    new_value=new_value,
                    performed_by=performed_by or 'system'
                )

                db.add(audit_log)
                await db.commit()

        except Exception as e:
            logger.warning(f"Failed to log audit event: {str(e)}")

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'license_manager',
            'status': 'healthy',
            'license_loaded': self._license_data is not None,
            'solution_name': self.solution_name,
            'timestamp': datetime.utcnow().isoformat()
        }

