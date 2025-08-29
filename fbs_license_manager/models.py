"""
License Manager Models

Provides persistent storage for license data and feature usage tracking.
"""

from django.db import models
from django.core.cache import cache
from django.conf import settings
import json
import logging
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger('fbs_license_manager')


class LICSolutionLicense(models.Model):
    """Solution License Information stored in database"""
    
    solution_name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Name of the solution this license applies to'
    )
    
    solution_db = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Solution-specific database for isolation (optional)'
    )
    
    license_type = models.CharField(
        max_length=50,
        choices=[
            ('trial', 'Trial'),
            ('basic', 'Basic'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise')
        ],
        default='trial',
        help_text='Type of license'
    )
    
    license_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='External license key if applicable'
    )
    
    expiry_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text='License expiry date (None for perpetual licenses)'
    )
    
    features = models.TextField(
        default='[]',
        help_text='JSON array of enabled features'
    )
    
    limits = models.TextField(
        default='{}',
        help_text='JSON object of feature limits'
    )
    
    status = models.CharField(
        max_length=50,
        choices=[
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('suspended', 'Suspended'),
            ('trial_expired', 'Trial Expired')
        ],
        default='active',
        help_text='Current license status'
    )
    
    source = models.CharField(
        max_length=50,
        choices=[
            ('embedded', 'Embedded'),
            ('external', 'External Service'),
            ('file', 'License File'),
            ('environment', 'Environment Variable')
        ],
        default='embedded',
        help_text='Source of the license'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lic_solution_license'
        verbose_name = 'Solution License'
        verbose_name_plural = 'Solution Licenses'
        ordering = ['solution_name']
    
    def __str__(self):
        return f"{self.solution_name} - {self.license_type}"
    
    def save(self, *args, **kwargs):
        """Override save to validate JSON, encrypt license key, and update cache"""
        # Validate JSON fields
        if self.features:
            try:
                json.loads(self.features)
            except (json.JSONDecodeError, TypeError):
                self.features = '[]'
        
        if self.limits:
            try:
                json.loads(self.limits)
            except (json.JSONDecodeError, TypeError):
                self.limits = '{}'
        
        # Encrypt license key if provided
        if self.license_key and not self._is_encrypted(self.license_key):
            self.license_key = self._encrypt_license_key(self.license_key)
        
        super().save(*args, **kwargs)
        
        # Update cache
        self._update_cache()
    
    def delete(self, *args, **kwargs):
        """Override delete to clear cache"""
        cache_key = f"license_{self.solution_name}"
        cache.delete(cache_key)
        super().delete(*args, **kwargs)
    
    def get_features_list(self):
        """Get features as Python list"""
        try:
            return json.loads(self.features or '[]')
        except (json.JSONDecodeError, TypeError):
            return []
    
    def get_limits_dict(self):
        """Get limits as Python dict"""
        try:
            return json.loads(self.limits or '{}')
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def has_feature(self, feature_name):
        """Check if feature is enabled"""
        return feature_name in self.get_features_list()
    
    def get_feature_limit(self, feature_name, limit_type='count'):
        """Get limit for a specific feature"""
        limits = self.get_limits_dict()
        feature_limits = limits.get(feature_name, {})
        return feature_limits.get(limit_type, -1)  # -1 means unlimited
    
    def check_feature_usage(self, feature_name, current_usage=0):
        """Check if feature usage is within limits"""
        limit = self.get_feature_limit(feature_name, 'count')
        
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
    
    def is_expired(self):
        """Check if license is expired"""
        if not self.expiry_date:
            return False
        
        from django.utils import timezone
        return timezone.now() > self.expiry_date
    
    def update_status(self):
        """Update license status based on current conditions"""
        if self.license_type == 'trial':
            if self.is_expired():
                self.status = 'trial_expired'
            else:
                self.status = 'active'
        elif self.expiry_date and self.is_expired():
            self.status = 'expired'
        else:
            self.status = 'active'
        
        self.save()
    
    def _update_cache(self):
        """Update cache with current license data"""
        cache_key = f"license_{self.solution_name}"
        cache_data = {
            'type': self.license_type,
            'license_key': self.license_key,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'features': self.get_features_list(),
            'limits': self.get_limits_dict(),
            'status': self.status,
            'source': self.source,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        cache.set(cache_key, cache_data, 3600)  # 1 hour TTL
    
    def _get_encryption_key(self):
        """Get or generate encryption key for license keys"""
        key = getattr(settings, 'FBS_LICENSE_ENCRYPTION_KEY', None)
        if not key:
            # Generate a key from Django secret key
            secret = settings.SECRET_KEY.encode()
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'fbs_license_salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret))
        return key
    
    def _encrypt_license_key(self, license_key):
        """Encrypt license key"""
        try:
            if not license_key:
                return None
            cipher = Fernet(self._get_encryption_key())
            return cipher.encrypt(license_key.encode()).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt license key: {e}")
            return license_key  # Fallback to plain text
    
    def _decrypt_license_key(self, encrypted_key):
        """Decrypt license key"""
        try:
            if not encrypted_key:
                return None
            cipher = Fernet(self._get_encryption_key())
            return cipher.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            logger.error(f"Failed to decrypt license key: {e}")
            return encrypted_key  # Fallback to encrypted text
    
    def _is_encrypted(self, text):
        """Check if text is encrypted (base64 + Fernet format)"""
        try:
            if not text:
                return False
            # Try to decode as base64
            decoded = base64.urlsafe_b64decode(text + '==')
            # Check if it's Fernet format (should be at least 44 bytes: 32 key + 12 nonce + encrypted data)
            return len(decoded) >= 44
        except Exception:
            return False
    
    def get_decrypted_license_key(self):
        """Get decrypted license key"""
        if not self.license_key:
            return None
        return self._decrypt_license_key(self.license_key)
    
    @classmethod
    def get_license_for_solution(cls, solution_name):
        """Get license record for a specific solution"""
        return cls.objects.filter(solution_name=solution_name).first()
    
    @classmethod
    def create_or_update_license(cls, solution_name, license_data):
        """Create or update license for a solution"""
        existing = cls.get_license_for_solution(solution_name)
        
        # Prepare data for model
        model_data = {
            'solution_name': solution_name,
            'license_type': license_data.get('type', 'trial'),
            'license_key': license_data.get('license_key'),
            'expiry_date': license_data.get('expiry_date'),
            'features': json.dumps(license_data.get('features', [])),
            'limits': json.dumps(license_data.get('limits', {})),
            'status': license_data.get('status', 'active'),
            'source': license_data.get('source', 'embedded')
        }
        
        if existing:
            for key, value in model_data.items():
                setattr(existing, key, value)
            existing.save()
            return existing
        else:
            return cls.objects.create(**model_data)


class LICFeatureUsage(models.Model):
    """Feature usage tracking for solutions"""
    
    solution_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text='Name of the solution'
    )
    
    feature_name = models.CharField(
        max_length=255,
        db_index=True,
        help_text='Name of the feature being tracked'
    )
    
    usage_count = models.IntegerField(
        default=0,
        help_text='Current usage count for this feature'
    )
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lic_feature_usage'
        verbose_name = 'Feature Usage'
        verbose_name_plural = 'Feature Usage'
        ordering = ['solution_name', 'feature_name']
        unique_together = ['solution_name', 'feature_name']
    
    def __str__(self):
        return f"{self.solution_name} - {self.feature_name}: {self.usage_count}"
    
    @classmethod
    def get_usage_for_solution(cls, solution_name, feature_name):
        """Get usage record for a specific solution and feature"""
        return cls.objects.filter(
            solution_name=solution_name,
            feature_name=feature_name
        ).first()
    
    @classmethod
    def increment_usage(cls, solution_name, feature_name, count=1):
        """Increment usage counter for a feature"""
        usage, created = cls.objects.get_or_create(
            solution_name=solution_name,
            feature_name=feature_name,
            defaults={'usage_count': count}
        )
        
        if not created:
            usage.usage_count += count
            usage.save()
        
        return usage
    
    @classmethod
    def get_current_usage(cls, solution_name, feature_name):
        """Get current usage count for a feature"""
        usage = cls.get_usage_for_solution(solution_name, feature_name)
        return usage.usage_count if usage else 0


class LICLicenseManager(models.Model):
    """License management operations utility model"""
    
    class Meta:
        db_table = 'lic_license_manager'
        verbose_name = 'License Manager'
        verbose_name_plural = 'License Managers'
    
    def __str__(self):
        return f"License Manager {self.id}"
    
    @classmethod
    def get_license_manager(cls, solution_name):
        """Get license manager for a specific solution"""
        if not solution_name:
            from django.core.exceptions import ValidationError
            raise ValidationError("Solution name is required")
        
        return LICSolutionLicense.get_license_for_solution(solution_name)
    
    @classmethod
    def check_feature_access(cls, solution_name, feature_name, current_usage=0):
        """Check if a feature is accessible for a solution"""
        license_record = cls.get_license_manager(solution_name)
        
        if not license_record:
            return {
                'access': False,
                'reason': 'no_license',
                'message': 'No license found for solution'
            }
        
        # Check if feature is enabled
        if not license_record.has_feature(feature_name):
            return {
                'access': False,
                'reason': 'feature_not_licensed',
                'message': f'Feature {feature_name} is not licensed'
            }
        
        # Check usage limits
        usage_check = license_record.check_feature_usage(feature_name, current_usage)
        
        if not usage_check['available']:
            return {
                'access': False,
                'reason': 'limit_exceeded',
                'message': f'Usage limit exceeded for {feature_name}',
                'current_usage': current_usage,
                'limit': usage_check['limit']
            }
        
        return {
            'access': True,
            'remaining': usage_check['remaining'],
            'limit': usage_check['limit'],
            'current_usage': current_usage
        }
    
    @classmethod
    def increment_feature_usage(cls, solution_name, feature_name, count=1):
        """Increment usage counter for a feature"""
        LICFeatureUsage.increment_usage(solution_name, feature_name, count)
    
    @classmethod
    def get_feature_usage(cls, solution_name, feature_name):
        """Get current usage for a feature"""
        return LICFeatureUsage.get_current_usage(solution_name, feature_name)
    
    @classmethod
    def validate_license(cls, solution_name):
        """Validate license for a solution"""
        license_record = cls.get_license_manager(solution_name)
        
        if not license_record:
            return {'valid': False, 'reason': 'no_license'}
        
        # Update status
        license_record.update_status()
        
        if license_record.status in ['active', 'trial_expired']:
            return {'valid': True, 'status': license_record.status}
        else:
            return {'valid': False, 'reason': license_record.status}

