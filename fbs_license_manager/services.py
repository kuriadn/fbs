"""
License Manager Services

Core business logic for license management, feature flags, and upgrade prompts.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('fbs_license_manager')


class EmbeddedLicenseEngine:
    """Local, embedded license management engine"""
    
    def __init__(self, solution_name: str, license_key: str = None):
        self.solution_name = solution_name
        self.license_key = license_key or self._get_default_license()
        self._license_data = None
        self._features = None
        
        # Load license data
        self._load_license_data()
    
    def _get_default_license(self) -> str:
        """Get default license from environment or generate trial"""
        return getattr(settings, 'FBS_LICENSE_TYPE', 'trial')
    
    def _load_license_data(self):
        """Load license data from multiple sources"""
        try:
            # Priority 1: Database storage
            from .models import LICSolutionLicense
            db_license = LICSolutionLicense.get_license_for_solution(self.solution_name)
            if db_license:
                self._license_data = {
                    'type': db_license.license_type,
                    'license_key': db_license.license_key,
                    'expiry_date': db_license.expiry_date.isoformat() if db_license.expiry_date else None,
                    'features': db_license.get_features_list(),
                    'limits': db_license.get_limits_dict(),
                    'status': db_license.status,
                    'source': db_license.source
                }
                return
            
            # Priority 2: Environment variables
            env_license = self._load_from_environment()
            if env_license:
                self._license_data = env_license
                return
            
            # Priority 3: Default trial
            self._license_data = self._generate_license_data(self.license_key)
            
        except Exception as e:
            logger.error(f"Failed to load license data: {e}")
            # Fallback to trial license
            self._license_data = self._generate_license_data('trial')
    
    def _load_from_environment(self) -> Optional[Dict[str, Any]]:
        """Load license data from environment variables"""
        license_type = getattr(settings, 'FBS_LICENSE_TYPE', None)
        if not license_type:
            return None
        
        features = []
        limits = {}
        
        # Load features from environment
        if getattr(settings, 'FBS_ENABLE_MSME_FEATURES', False):
            features.append('msme')
        if getattr(settings, 'FBS_ENABLE_BI_FEATURES', False):
            features.append('bi')
        if getattr(settings, 'FBS_ENABLE_WORKFLOW_FEATURES', False):
            features.append('workflows')
        if getattr(settings, 'FBS_ENABLE_COMPLIANCE_FEATURES', False):
            features.append('compliance')
        
        # Load limits from environment
        limits['msme_businesses'] = getattr(settings, 'FBS_MSME_BUSINESSES_LIMIT', 5)
        limits['workflows'] = getattr(settings, 'FBS_WORKFLOWS_LIMIT', 10)
        limits['reports'] = getattr(settings, 'FBS_REPORTS_LIMIT', 100)
        limits['users'] = getattr(settings, 'FBS_USERS_LIMIT', 5)
        
        return {
            'type': license_type,
            'features': features,
            'limits': limits,
            'status': 'active',
            'source': 'environment'
        }
    
    def _generate_license_data(self, license_type: str) -> Dict[str, Any]:
        """Generate license data based on type"""
        trial_days = getattr(settings, 'FBS_TRIAL_DAYS', 30)
        
        if license_type == 'trial':
            return {
                'type': 'trial',
                'features': ['core', 'basic_msme', 'basic_odoo'],
                'limits': {
                    'msme_businesses': 1,
                    'workflows': 2,
                    'reports': 100,
                    'users': 2
                },
                'expiry_date': (timezone.now() + timedelta(days=trial_days)).isoformat(),
                'status': 'active',
                'source': 'generated'
            }
        elif license_type == 'basic':
            return {
                'type': 'basic',
                'features': ['core', 'msme', 'basic_odoo', 'basic_workflows'],
                'limits': {
                    'msme_businesses': 5,
                    'workflows': 10,
                    'reports': 1000,
                    'users': 5
                },
                'status': 'active',
                'source': 'generated'
            }
        elif license_type == 'professional':
            return {
                'type': 'professional',
                'features': ['core', 'msme', 'odoo', 'workflows', 'bi', 'compliance'],
                'limits': {
                    'msme_businesses': 25,
                    'workflows': 100,
                    'reports': 10000,
                    'users': 25
                },
                'status': 'active',
                'source': 'generated'
            }
        elif license_type == 'enterprise':
            return {
                'type': 'enterprise',
                'features': ['core', 'msme', 'odoo', 'workflows', 'bi', 'compliance', 'accounting', 'advanced_analytics'],
                'limits': {
                    'msme_businesses': -1,  # Unlimited
                    'workflows': -1,
                    'reports': -1,
                    'users': -1
                },
                'status': 'active',
                'source': 'generated'
            }
        else:
            # Default to trial
            return self._generate_license_data('trial')
    
    def get_license_info(self) -> Dict[str, Any]:
        """Get comprehensive license information"""
        return {
            'license_type': self._license_data.get('type', 'trial'),
            'solution_name': self.solution_name,
            'expiry_date': self._license_data.get('expiry_date'),
            'features': self.get_available_features(),
            'limits': self._license_data.get('limits', {}),
            'status': self.get_license_status(),
            'upgrade_available': self._check_upgrade_availability(),
            'trial_days_remaining': self._get_trial_days_remaining(),
            'source': self._license_data.get('source', 'embedded'),
            'license_key': self.license_key,
            'storage_type': 'database',
            'odoo_available': self._check_odoo_availability()
        }
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if a feature is available"""
        if not self._features:
            self._features = self._license_data.get('features', [])
        return feature_name in self._features
    
    def get_available_features(self) -> List[str]:
        """Get list of available features"""
        if not self._features:
            self._features = self._license_data.get('features', [])
        return self._features.copy()
    
    def get_feature_limit(self, feature_name: str) -> int:
        """Get limit for a specific feature"""
        limits = self._license_data.get('limits', {})
        feature_limit = limits.get(feature_name, {})
        
        # Handle nested structure like {'feature1': {'count': 100}}
        if isinstance(feature_limit, dict):
            return feature_limit.get('count', -1)
        elif isinstance(feature_limit, int):
            return feature_limit
        else:
            return -1  # -1 means unlimited
    
    def check_feature_usage(self, feature_name: str, current_usage: int) -> Dict[str, Any]:
        """Check if feature usage is within limits"""
        limit = self.get_feature_limit(feature_name)
        
        if limit == -1:  # Unlimited
            return {'available': True, 'remaining': -1, 'limit': -1}
        
        remaining = max(0, limit - current_usage)
        available = remaining > 0
        
        return {
            'available': available,
            'remaining': remaining,
            'limit': limit,
            'current_usage': current_usage
        }
    
    def get_license_status(self) -> str:
        """Get current license status"""
        if self._license_data.get('type') == 'trial':
            expiry_date = self._license_data.get('expiry_date')
            if expiry_date:
                try:
                    expiry = datetime.fromisoformat(expiry_date)
                    if timezone.now() > expiry:
                        return 'trial_expired'
                except (ValueError, TypeError):
                    pass
            return 'active'
        
        return self._license_data.get('status', 'active')
    
    def _check_odoo_availability(self) -> bool:
        """Check if Odoo is available through FBS app"""
        try:
            # Try to import FBS app
            from fbs_app.interfaces import FBSInterface
            
            # Check if FBS app is available
            if not hasattr(settings, 'FBS_ODOO_CONFIG'):
                return False
            
            # Try to create FBS interface
            fbs_interface = FBSInterface(self.solution_name)
            
            # Check Odoo availability
            return fbs_interface.odoo.is_available()
            
        except ImportError:
            logger.warning("FBS app not available, Odoo integration disabled")
            return False
        except Exception as e:
            logger.error(f"Failed to check Odoo availability: {e}")
            return False
    
    def _check_upgrade_availability(self) -> bool:
        """Check if upgrade is available"""
        current_type = self._license_data.get('type', 'trial')
        return current_type in ['trial', 'basic', 'professional']
    
    def _get_trial_days_remaining(self) -> Optional[int]:
        """Get trial days remaining"""
        if self._license_data.get('type') != 'trial':
            return None
        
        expiry_date = self._license_data.get('expiry_date')
        if not expiry_date:
            return None
        
        try:
            expiry = datetime.fromisoformat(expiry_date)
            remaining = (expiry - timezone.now()).days
            return max(0, remaining)
        except (ValueError, TypeError):
            return None
    
    def get_upgrade_options(self) -> List[Dict[str, Any]]:
        """Get available upgrade options"""
        current_type = self._license_data.get('type', 'trial')
        
        if current_type == 'trial':
            return [
                {'type': 'basic', 'price': '$29/month', 'features': ['MSME', 'Basic Workflows']},
                {'type': 'professional', 'price': '$99/month', 'features': ['BI', 'Compliance']},
                {'type': 'enterprise', 'price': '$299/month', 'features': ['All Features']}
            ]
        elif current_type == 'basic':
            return [
                {'type': 'professional', 'price': '$99/month', 'features': ['BI', 'Compliance']},
                {'type': 'enterprise', 'price': '$299/month', 'features': ['All Features']}
            ]
        elif current_type == 'professional':
            return [
                {'type': 'enterprise', 'price': '$299/month', 'features': ['All Features']}
            ]
        else:
            return []  # Enterprise is max tier
    
    def refresh_license(self):
        """Refresh license data"""
        self._license_data = None
        self._features = None
        self._load_license_data()


class FeatureFlags:
    """Feature availability management based on license"""
    
    def __init__(self, solution_name: str, license_manager):
        self.solution_name = solution_name
        self.license_manager = license_manager
    
    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled"""
        if not self.license_manager:
            return True  # No license manager means unlimited access
        
        return self.license_manager.has_feature(feature_name)
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled features"""
        if not self.license_manager:
            return []  # No license manager means no specific features
        
        return self.license_manager.get_available_features()
    
    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """Get configuration for a specific feature"""
        if not self.license_manager:
            return {'enabled': True, 'unlimited': True}
        
        limit = self.license_manager.get_feature_limit(feature_name)
        return {
            'enabled': self.license_manager.has_feature(feature_name),
            'limit': limit,
            'unlimited': limit == -1
        }
    
    def check_feature_access(self, feature_name: str, **kwargs) -> Dict[str, Any]:
        """Check if user can access a feature with current usage"""
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
        
        # Get current usage from database if available
        current_usage = kwargs.get('current_usage', 0)
        if current_usage == 0:
            try:
                from .models import LICFeatureUsage
                current_usage = LICFeatureUsage.get_current_usage(self.solution_name, feature_name)
            except Exception as e:
                logger.warning(f"Failed to get usage from database for {feature_name}: {e}")
        
        # Map feature names to limit names for consistency
        limit_mapping = {
            'msme': 'msme_businesses',
            'workflows': 'workflows',
            'reports': 'reports',
            'users': 'users',
            'dashboards': 'dashboards',
            'kpis': 'kpis'
        }
        
        limit_feature = limit_mapping.get(feature_name, feature_name)
        usage_check = self.license_manager.check_feature_usage(limit_feature, current_usage)
        
        if not usage_check['available']:
            return {
                'access': False,
                'reason': 'limit_exceeded',
                'current_usage': current_usage,
                'limit': usage_check['limit'],
                'upgrade_required': True,
                'feature_name': feature_name
            }
        
        return {
            'access': True,
            'remaining': usage_check['remaining'],
            'limit': usage_check['limit'],
            'feature_name': feature_name
        }
    
    def get_feature_limits(self) -> Dict[str, int]:
        """Get all feature limits"""
        if not self.license_manager:
            return {}
        
        return self.license_manager._license_data.get('limits', {})
    
    def get_feature_usage_summary(self) -> Dict[str, int]:
        """Get current usage for all features"""
        try:
            from .models import LICFeatureUsage
            usage_records = LICFeatureUsage.objects.filter(solution_name=self.solution_name)
            return {
                record.feature_name: record.usage_count 
                for record in usage_records
            }
        except Exception as e:
            logger.warning(f"Failed to get usage summary: {e}")
            return {}
    
    def get_upgrade_recommendations(self) -> List[Dict[str, Any]]:
        """Get upgrade recommendations based on current usage"""
        if not self.license_manager:
            return []
        
        recommendations = []
        limits = self.get_feature_limits()
        usage = self.get_feature_usage_summary()
        
        for feature, limit in limits.items():
            if limit == -1:  # Unlimited
                continue
            
            current = usage.get(feature, 0)
            if current >= limit * 0.8:  # 80% of limit
                recommendations.append({
                    'feature': feature,
                    'current_usage': current,
                    'limit': limit,
                    'percentage': (current / limit) * 100,
                    'recommendation': 'upgrade'
                })
        
        return recommendations
    
    def validate_feature_usage(self, feature_name: str, requested_usage: int) -> Dict[str, Any]:
        """Validate if requested usage is within limits"""
        access = self.check_feature_access(feature_name)
        if not access['access']:
            return access
        
        if access['limit'] == -1:  # Unlimited
            return {'valid': True, 'remaining': -1}
        
        remaining = access['remaining']
        if requested_usage <= remaining:
            return {'valid': True, 'remaining': remaining - requested_usage}
        else:
            return {
                'valid': False,
                'reason': 'insufficient_quota',
                'requested': requested_usage,
                'available': remaining
            }
    
    def get_feature_dependencies(self, feature_name: str) -> List[str]:
        """Get dependencies for a feature"""
        dependencies = {
            'bi': ['core', 'odoo'],
            'compliance': ['core', 'workflows'],
            'accounting': ['core', 'msme'],
            'advanced_analytics': ['core', 'bi', 'compliance']
        }
        return dependencies.get(feature_name, [])
    
    def check_feature_dependencies(self, feature_name: str) -> Dict[str, Any]:
        """Check if all dependencies for a feature are met"""
        dependencies = self.get_feature_dependencies(feature_name)
        missing = []
        
        for dep in dependencies:
            if not self.is_enabled(dep):
                missing.append(dep)
        
        return {
            'met': len(missing) == 0,
            'missing': missing,
            'feature': feature_name
        }
    
    def get_feature_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Get complete feature availability matrix"""
        features = self.get_enabled_features()
        matrix = {}
        
        for feature in features:
            config = self.get_feature_config(feature)
            dependencies = self.check_feature_dependencies(feature)
            
            matrix[feature] = {
                'enabled': config['enabled'],
                'limit': config['limit'],
                'unlimited': config['unlimited'],
                'dependencies_met': dependencies['met'],
                'missing_dependencies': dependencies['missing']
            }
        
        return matrix


class UpgradePrompts:
    """Generate upgrade prompts and recommendations"""
    
    def __init__(self, license_manager):
        self.license_manager = license_manager
    
    def get_upgrade_prompt(self, feature_name: str) -> Dict[str, Any]:
        """Get upgrade prompt for a specific feature"""
        if not self.license_manager:
            return {'upgrade_required': False}
        
        if self.license_manager.has_feature(feature_name):
            return {'upgrade_required': False, 'message': 'Feature already available'}
        
        current_type = self.license_manager._license_data.get('type', 'trial')
        upgrade_paths = self._get_upgrade_paths()
        
        for path in upgrade_paths:
            if feature_name in path.get('features', []):
                return {
                    'upgrade_required': True,
                    'current_tier': current_type,
                    'recommended_tier': path['type'],
                    'price': path['price'],
                    'features': path['features'],
                    'message': f'Upgrade to {path["type"].title()} to access {feature_name}'
                }
        
        return {'upgrade_required': False, 'message': 'Feature not available in any tier'}
    
    def get_feature_upgrade_prompt(self, feature_name: str) -> Dict[str, Any]:
        """Get feature-specific upgrade prompt"""
        return self.get_upgrade_prompt(feature_name)
    
    def get_comprehensive_upgrade_analysis(self) -> Dict[str, Any]:
        """Get comprehensive upgrade analysis"""
        if not self.license_manager:
            return {'analysis': 'No license manager available'}
        
        current_type = self.license_manager._license_data.get('type', 'trial')
        upgrade_options = self.license_manager.get_upgrade_options()
        
        analysis = {
            'current_tier': current_type,
            'upgrade_available': self.license_manager._check_upgrade_availability(),
            'options': upgrade_options,
            'recommendations': self._get_upgrade_recommendations()
        }
        
        return analysis
    
    def get_upgrade_contact_info(self) -> Dict[str, str]:
        """Get contact information for upgrades"""
        return {
            'email': 'upgrades@fbs.com',
            'phone': '+1-555-0123',
            'website': 'https://fbs.com/upgrade',
            'support_hours': '24/7'
        }
    
    def get_upgrade_process_info(self) -> Dict[str, Any]:
        """Get information about the upgrade process"""
        return {
            'process': 'Contact sales team for upgrade',
            'timeline': 'Same day activation',
            'data_migration': 'Automatic, no downtime',
            'support': 'Dedicated upgrade support'
        }
    
    def _get_upgrade_paths(self) -> List[Dict[str, Any]]:
        """Get available upgrade paths"""
        return [
            {
                'type': 'basic',
                'price': '$29/month',
                'features': ['msme', 'basic_workflows', 'basic_odoo']
            },
            {
                'type': 'professional',
                'price': '$99/month',
                'features': ['msme', 'workflows', 'odoo', 'bi', 'compliance']
            },
            {
                'type': 'enterprise',
                'price': '$299/month',
                'features': ['all_features', 'accounting', 'advanced_analytics']
            }
        ]
    
    def _get_upgrade_recommendations(self) -> List[Dict[str, Any]]:
        """Get upgrade recommendations based on current usage"""
        if not self.license_manager:
            return []
        
        recommendations = []
        current_type = self.license_manager._license_data.get('type', 'trial')
        
        if current_type == 'trial':
            recommendations.append({
                'reason': 'trial_expiring',
                'recommendation': 'basic',
                'benefits': ['Unlimited trial features', 'Priority support']
            })
        
        return recommendations


class LicenseManager:
    """Manages license information and feature access for a solution"""
    
    def __init__(self, solution_name: str, license_key: str = None, solution_db: str = None):
        self.solution_name = solution_name
        self.license_key = license_key
        self.solution_db = solution_db or f"djo_{solution_name}_db"
        
        # Get license information
        self.license_info = self._get_license_info()
        self.feature_flags = FeatureFlags(solution_name, self)
    
    def _get_license_info(self) -> Dict[str, Any]:
        """Get license information for the solution"""
        try:
            # Import LICSolutionLicense here to avoid circular imports
            from .models import LICSolutionLicense
            
            # Try to get from solution-specific database first
            if self.solution_db and self.solution_db in self._get_solution_databases():
                db_license = LICSolutionLicense.objects.using(self.solution_db).filter(
                    solution_name=self.solution_name
                ).first()
                if db_license:
                    return self._format_license_info(db_license)
            
            # Fall back to system database
            db_license = LICSolutionLicense.objects.filter(
                solution_name=self.solution_name
            ).first()
            
            if db_license:
                return self._format_license_info(db_license)
            
            # Return default trial license
            return {
                'solution_name': self.solution_name,
                'license_type': 'trial',
                'status': 'active',
                'features': ['basic_features'],
                'limits': {'documents': 100, 'users': 5},
                'expiry_date': None,
                'source': 'embedded',
                'odoo_available': self._check_odoo_availability()
            }
            
        except Exception as e:
            logger.error(f"Failed to get license info: {e}")
            return self._get_default_license_info()
    
    def _get_default_license_info(self) -> Dict[str, Any]:
        """Get default license information when database lookup fails"""
        return {
            'solution_name': self.solution_name,
            'license_type': 'trial',
            'status': 'active',
            'features': ['basic_features'],
            'limits': {'documents': 100, 'users': 5},
            'expiry_date': None,
            'source': 'embedded',
            'odoo_available': self._check_odoo_availability()
        }
    
    def _format_license_info(self, db_license) -> Dict[str, Any]:
        """Format database license object into dictionary"""
        return {
            'solution_name': db_license.solution_name,
            'license_type': db_license.license_type,
            'status': db_license.status,
            'features': db_license.get_features_list() if hasattr(db_license, 'get_features_list') else ['basic_features'],
            'limits': db_license.get_limits_dict() if hasattr(db_license, 'get_limits_dict') else {'documents': 100, 'users': 5},
            'expiry_date': db_license.expiry_date.isoformat() if db_license.expiry_date else None,
            'source': db_license.source,
            'odoo_available': self._check_odoo_availability()
        }
    
    def _check_odoo_availability(self) -> bool:
        """Check if Odoo is available through FBS app"""
        try:
            from fbs_app.interfaces import FBSInterface
            fbs_interface = FBSInterface(self.solution_name)
            return fbs_interface.is_odoo_available()
        except Exception as e:
            logger.warning(f"Could not check Odoo availability: {e}")
            return False
    
    def has_feature(self, feature_name: str) -> bool:
        """Check if a feature is available"""
        features = self.license_info.get('features', [])
        return feature_name in features
    
    def get_available_features(self) -> List[str]:
        """Get list of available features"""
        return self.license_info.get('features', [])
    
    def get_feature_limit(self, feature_name: str) -> int:
        """Get limit for a specific feature"""
        limits = self.license_info.get('limits', {})
        feature_limit = limits.get(feature_name, -1)
        
        # Handle nested structure like {'feature1': {'count': 100}}
        if isinstance(feature_limit, dict):
            return feature_limit.get('count', -1)
        elif isinstance(feature_limit, int):
            return feature_limit
        else:
            return -1  # -1 means unlimited
    
    def check_feature_usage(self, feature_name: str, current_usage: int) -> Dict[str, Any]:
        """Check if feature usage is within limits"""
        limit = self.get_feature_limit(feature_name)
        
        if limit == -1:  # Unlimited
            return {'available': True, 'remaining': -1, 'limit': -1}
        
        remaining = max(0, limit - current_usage)
        available = remaining > 0
        
        return {
            'available': available,
            'remaining': remaining,
            'limit': limit,
            'current_usage': current_usage
        }

    def _get_solution_databases(self):
        """Get list of available solution databases"""
        from django.conf import settings
        solution_dbs = []
        for db_name in settings.DATABASES.keys():
            if db_name.startswith('djo_') or db_name.startswith('fbs_'):
                solution_dbs.append(db_name)
        return solution_dbs


class OdooLicenseService:
    """Odoo-driven license service using FBS virtual fields for extensions"""
    
    def __init__(self, company_id: str, fbs_interface=None):
        self.company_id = company_id
        self.fbs = fbs_interface
        self.odoo_licenses = fbs_interface.odoo if fbs_interface else None
        self.virtual_fields = fbs_interface.fields if fbs_interface else None
        
        if not self.odoo_licenses:
            logger.warning("Odoo integration not available - License Manager will work in limited mode")
    
    def create_license(self, license_data: Dict[str, Any], user=None) -> Dict[str, Any]:
        """Create license with Odoo storage + FBS virtual fields"""
        if not self.odoo_licenses:
            return {
                'success': False,
                'error': 'Odoo integration required for license creation'
            }
        
        try:
            # 1. Prepare base company data for Odoo (res.partner)
            odoo_data = {
                'name': license_data['company_name'],
                'email': license_data.get('email', ''),
                'phone': license_data.get('phone', ''),
                'street': license_data.get('address', {}).get('street', ''),
                'city': license_data.get('address', {}).get('city', ''),
                'state_id': license_data.get('address', {}).get('state_id', False),
                'country_id': license_data.get('address', {}).get('country_id', False),
                'zip': license_data.get('address', {}).get('zip', ''),
                'is_company': True,
                'customer_rank': 1,
                'company_id': self.company_id,
                'create_uid': user.id if user else 1,
                'write_uid': user.id if user else 1,
                'create_date': timezone.now().isoformat(),
                'write_date': timezone.now().isoformat()
            }
            
            # 2. Create company in Odoo
            odoo_result = self.odoo_licenses.create_record('res.partner', odoo_data)
            
            if not odoo_result.get('success'):
                raise Exception(f"Odoo company creation failed: {odoo_result.get('error')}")
            
            odoo_id = odoo_result['data']['id']
            
            # 3. Add FBS virtual fields for license-specific data
            if self.virtual_fields:
                self._add_license_virtual_fields(odoo_id, license_data)
            
            return {
                'success': True,
                'odoo_id': odoo_id,
                'message': 'License created successfully in Odoo with virtual fields'
            }
            
        except Exception as e:
            logger.error(f"License creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _add_license_virtual_fields(self, odoo_id: int, license_data: Dict[str, Any]):
        """Add license-specific virtual fields to the Odoo company"""
        try:
            # License key (encrypted)
            if license_data.get('license_key'):
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'license_key', 
                    license_data['license_key'], 'char', self.company_id
                )
            
            # License type
            self.virtual_fields.set_custom_field(
                'res.partner', odoo_id, 'license_type', 
                license_data.get('license_type', 'standard'), 'char', self.company_id
            )
            
            # License status
            self.virtual_fields.set_custom_field(
                'res.partner', odoo_id, 'license_status', 
                license_data.get('status', 'active'), 'char', self.company_id
            )
            
            # Expiry date
            if license_data.get('expiry_date'):
                expiry_date = license_data['expiry_date']
                if hasattr(expiry_date, 'isoformat'):
                    expiry_date = expiry_date.isoformat()
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'expiry_date', 
                    expiry_date, 'date', self.company_id
                )
            
            # Feature flags (JSON encoded)
            if license_data.get('features'):
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'feature_flags', 
                    json.dumps(license_data['features']), 'text', self.company_id
                )
            
            # Usage limits
            if license_data.get('max_users'):
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'max_users', 
                    license_data['max_users'], 'integer', self.company_id
                )
            
            if license_data.get('max_storage_gb'):
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'max_storage_gb', 
                    license_data['max_storage_gb'], 'integer', self.company_id
                )
            
            # Additional fields from test data
            if license_data.get('api_rate_limit'):
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'api_rate_limit', 
                    license_data['api_rate_limit'], 'integer', self.company_id
                )
            
            if license_data.get('billing_cycle'):
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'billing_cycle', 
                    license_data['billing_cycle'], 'char', self.company_id
                )
            
            if license_data.get('billing_amount'):
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'billing_amount', 
                    license_data['billing_amount'], 'float', self.company_id
                )
            
            if license_data.get('contact_person'):
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'contact_person', 
                    license_data['contact_person'], 'char', self.company_id
                )
            
            logger.info(f"Added license virtual fields to Odoo company {odoo_id}")
            
        except Exception as e:
            logger.error(f"Failed to add license virtual fields: {str(e)}")
            # Don't fail the main operation if virtual fields fail
    
    def get_license(self, odoo_id: int) -> Dict[str, Any]:
        """Get complete license data from Odoo + FBS virtual fields"""
        if not self.odoo_licenses:
            return {
                'success': False,
                'error': 'Odoo integration required'
            }
        
        try:
            # 1. Get base Odoo company data
            odoo_result = self.odoo_licenses.get_record('res.partner', odoo_id)
            
            if not odoo_result.get('success'):
                return {
                    'success': False,
                    'error': f"License not found: {odoo_result.get('error')}"
                }
            
            # 2. Get FBS virtual fields
            virtual_fields_data = {}
            if self.virtual_fields:
                virtual_result = self.virtual_fields.get_custom_fields(
                    'res.partner', odoo_id, self.company_id
                )
                
                if virtual_result.get('success'):
                    virtual_fields_data = virtual_result.get('data', {})
            
            # 3. Merge Odoo data with virtual fields
            complete_data = odoo_result['data']
            complete_data.update(virtual_fields_data)
            
            # 4. Parse JSON fields
            if 'feature_flags' in complete_data:
                try:
                    complete_data['features'] = json.loads(complete_data['feature_flags'])
                except (json.JSONDecodeError, TypeError):
                    complete_data['features'] = {}
            
            return {
                'success': True,
                'data': complete_data,
                'message': 'License retrieved successfully'
            }
            
        except Exception as e:
            logger.error(f"License retrieval failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_feature_access(self, odoo_id: int, feature_name: str) -> Dict[str, Any]:
        """Check if a license has access to a specific feature"""
        try:
            license_data = self.get_license(odoo_id)
            
            if not license_data.get('success'):
                return {
                    'success': False,
                    'error': 'License not found'
                }
            
            data = license_data['data']
            features = data.get('features', {})
            
            # Check if feature is enabled
            feature_enabled = features.get(feature_name, False)
            
            if not feature_enabled:
                return {
                    'success': True,
                    'access': False,
                    'message': f'Feature {feature_name} not enabled for this license'
                }
            
            # Check usage limits
            current_usage = data.get(f'current_{feature_name}', 0)
            max_limit = data.get(f'max_{feature_name}', -1)
            
            if max_limit > 0 and current_usage >= max_limit:
                return {
                    'success': True,
                    'access': False,
                    'message': f'Feature {feature_name} usage limit reached',
                    'current': current_usage,
                    'limit': max_limit
                }
            
            return {
                'success': True,
                'access': True,
                'message': f'Feature {feature_name} access granted',
                'current': current_usage,
                'limit': max_limit
            }
            
        except Exception as e:
            logger.error(f"Feature access check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_license(self, odoo_id: int, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update license data in Odoo + FBS virtual fields"""
        if not self.odoo_licenses:
            return {
                'success': False,
                'error': 'Odoo integration required for license updates'
            }
        
        try:
            # 1. Update base Odoo company data
            odoo_update = {}
            if 'name' in update_data:
                odoo_update['name'] = update_data['name']
            if 'company_name' in update_data:
                odoo_update['name'] = update_data['company_name']
            if 'email' in update_data:
                odoo_update['email'] = update_data['email']
            if 'phone' in update_data:
                odoo_update['phone'] = update_data['phone']
            if 'address' in update_data:
                address = update_data['address']
                if 'street' in address:
                    odoo_update['street'] = address['street']
                if 'city' in address:
                    odoo_update['city'] = address['city']
                if 'state_id' in address:
                    odoo_update['state_id'] = address['state_id']
                if 'country_id' in address:
                    odoo_update['country_id'] = address['country_id']
                if 'zip' in address:
                    odoo_update['zip'] = address['zip']
            
            if odoo_update:
                odoo_result = self.odoo_licenses.update_record('res.partner', odoo_id, odoo_update)
                if not odoo_result.get('success'):
                    raise Exception(f"Odoo company update failed: {odoo_result.get('error')}")
            
            # 2. Update FBS virtual fields
            if self.virtual_fields:
                self._update_license_virtual_fields(odoo_id, update_data)
            
            return {
                'success': True,
                'message': 'License updated successfully in Odoo with virtual fields'
            }
            
        except Exception as e:
            logger.error(f"License update failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _update_license_virtual_fields(self, odoo_id: int, update_data: Dict[str, Any]):
        """Update license-specific virtual fields in the Odoo company"""
        try:
            # License key (encrypted)
            if 'license_key' in update_data:
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'license_key', 
                    update_data['license_key'], 'char', self.company_id
                )
            
            # License type
            if 'license_type' in update_data:
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'license_type', 
                    update_data['license_type'], 'char', self.company_id
                )
            
            # License status
            if 'status' in update_data:
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'license_status', 
                    update_data['status'], 'char', self.company_id
                )
            
            # Expiry date
            if 'expiry_date' in update_data:
                expiry_date = update_data['expiry_date']
                if hasattr(expiry_date, 'isoformat'):
                    expiry_date = expiry_date.isoformat()
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'expiry_date', 
                    expiry_date, 'date', self.company_id
                )
            
            # Feature flags (JSON encoded)
            if 'features' in update_data:
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'feature_flags', 
                    json.dumps(update_data['features']), 'text', self.company_id
                )
            
            # Usage limits
            if 'max_users' in update_data:
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'max_users', 
                    update_data['max_users'], 'integer', self.company_id
                )
            
            if 'max_storage_gb' in update_data:
                self.virtual_fields.set_custom_field(
                    'res.partner', odoo_id, 'max_storage_gb', 
                    update_data['max_storage_gb'], 'integer', self.company_id
                )
            
            logger.info(f"Updated license virtual fields for Odoo company {odoo_id}")
            
        except Exception as e:
            logger.error(f"Failed to update license virtual fields: {str(e)}")
            # Don't fail the main operation if virtual fields fail
    
    def delete_license(self, odoo_id: int) -> Dict[str, Any]:
        """Delete license from Odoo"""
        if not self.odoo_licenses:
            return {
                'success': False,
                'error': 'Odoo integration required for license deletion'
            }
        
        try:
            # Delete from Odoo
            odoo_result = self.odoo_licenses.delete_record('res.partner', odoo_id)
            
            if not odoo_result.get('success'):
                return {
                    'success': False,
                    'error': f"Odoo deletion failed: {odoo_result.get('error')}"
                }
            
            return {
                'success': True,
                'message': 'License deleted successfully from Odoo'
            }
            
        except Exception as e:
            logger.error(f"License deletion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_licenses(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Search licenses using Odoo domain + FBS virtual fields"""
        if not self.odoo_licenses:
            return {
                'success': False,
                'error': 'Odoo integration required for license search'
            }
        
        try:
            # Build search domain
            domain = self._build_search_domain(filters)
            
            # Search in Odoo
            odoo_result = self.odoo_licenses.get_records('res.partner', domain)
            
            if not odoo_result.get('success'):
                return {
                    'success': False,
                    'error': f"Odoo search failed: {odoo_result.get('error')}"
                }
            
            # Enhance results with virtual fields
            enhanced_results = []
            for record in odoo_result.get('data', []):
                enhanced_record = record.copy()
                
                if self.virtual_fields:
                    virtual_result = self.virtual_fields.get_custom_fields(
                        'res.partner', record['id'], self.company_id
                    )
                    
                    if virtual_result.get('success'):
                        enhanced_record.update(virtual_result.get('data', {}))
                
                enhanced_results.append(enhanced_record)
            
            return {
                'success': True,
                'data': enhanced_results,
                'count': len(enhanced_results),
                'message': f'Found {len(enhanced_results)} licenses'
            }
            
        except Exception as e:
            logger.error(f"License search failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_search_domain(self, filters: Dict[str, Any]) -> List:
        """Build Odoo search domain from filters"""
        domain = [('is_company', '=', True)]
        
        if filters.get('company_name'):
            domain.append(('name', 'ilike', filters['company_name']))
        
        if filters.get('email'):
            domain.append(('email', 'ilike', filters['email']))
        
        if filters.get('city'):
            domain.append(('city', 'ilike', filters['city']))
        
        if filters.get('country_id'):
            domain.append(('country_id', '=', filters['country_id']))
        
        if filters.get('license_type') and self.virtual_fields:
            # For virtual fields, we'll need to search differently
            # This is a simplified approach
            pass
        
        return domain
    
    def update_feature_usage(self, odoo_id: int, feature_name: str, usage_count: int) -> Dict[str, Any]:
        """Update feature usage count for a license"""
        if not self.virtual_fields:
            return {
                'success': False,
                'error': 'Virtual fields not available for usage tracking'
            }
        
        try:
            # Update current usage count
            self.virtual_fields.set_custom_field(
                'res.partner', odoo_id, f'current_{feature_name}', 
                usage_count, 'integer', self.company_id
            )
            
            logger.info(f"Updated {feature_name} usage to {usage_count} for license {odoo_id}")
            
            return {
                'success': True,
                'message': f'Updated {feature_name} usage to {usage_count}',
                'current_usage': usage_count
            }
            
        except Exception as e:
            logger.error(f"Feature usage update failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

