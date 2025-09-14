"""
FBS License Manager Models - SQLAlchemy

License management models migrated from Django to FastAPI.
Preserves all functionality while adapting to async SQLAlchemy patterns.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
import uuid

# Import Base from core database module to avoid conflicts
from ..core.database import Base

class LicenseType(PyEnum):
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class LicenseStatus(PyEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

class FeatureUsageStatus(PyEnum):
    ACTIVE = "active"
    EXCEEDED = "exceeded"
    BLOCKED = "blocked"

class SolutionLicense(Base):
    """Solution License Information stored in database - migrated from Django"""

    __tablename__ = 'solution_licenses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_name = Column(String(255), unique=True, nullable=False)
    solution_db = Column(String(100), nullable=True)
    license_type = Column(Enum(LicenseType), default=LicenseType.TRIAL, nullable=False)
    license_key = Column(String(255), nullable=False)
    status = Column(Enum(LicenseStatus), default=LicenseStatus.ACTIVE, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    activation_date = Column(DateTime, nullable=True)
    source = Column(String(50), default='database', nullable=False)  # database, environment, generated

    # License limits
    msme_businesses_limit = Column(Integer, default=5, nullable=False)
    workflows_limit = Column(Integer, default=10, nullable=False)
    reports_limit = Column(Integer, default=1000, nullable=False)
    users_limit = Column(Integer, default=5, nullable=False)
    storage_limit_gb = Column(Float, default=1.0, nullable=False)

    # Feature flags
    enable_msme = Column(Boolean, default=True, nullable=False)
    enable_bi = Column(Boolean, default=False, nullable=False)
    enable_workflows = Column(Boolean, default=False, nullable=False)
    enable_compliance = Column(Boolean, default=False, nullable=False)
    enable_accounting = Column(Boolean, default=False, nullable=False)
    enable_dms = Column(Boolean, default=False, nullable=False)
    enable_licensing = Column(Boolean, default=True, nullable=False)

    # Metadata
    metadata = Column(JSON, default=dict, nullable=False)
    notes = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)

    def get_features_list(self):
        """Get list of enabled features"""
        features = []
        if self.enable_msme:
            features.append('msme')
        if self.enable_bi:
            features.append('bi')
        if self.enable_workflows:
            features.append('workflows')
        if self.enable_compliance:
            features.append('compliance')
        if self.enable_accounting:
            features.append('accounting')
        if self.enable_dms:
            features.append('dms')
        if self.enable_licensing:
            features.append('licensing')
        return features

    def get_limits_dict(self):
        """Get license limits as dictionary"""
        return {
            'msme_businesses': self.msme_businesses_limit,
            'workflows': self.workflows_limit,
            'reports': self.reports_limit,
            'users': self.users_limit,
            'storage_gb': self.storage_limit_gb
        }

    def is_expired(self):
        """Check if license is expired"""
        if not self.expiry_date:
            return False
        return self.expiry_date < func.now()

    def is_trial(self):
        """Check if this is a trial license"""
        return self.license_type == LicenseType.TRIAL

    def can_use_feature(self, feature_name):
        """Check if feature can be used with this license"""
        feature_map = {
            'msme': self.enable_msme,
            'bi': self.enable_bi,
            'workflows': self.enable_workflows,
            'compliance': self.enable_compliance,
            'accounting': self.enable_accounting,
            'dms': self.enable_dms,
            'licensing': self.enable_licensing
        }
        return feature_map.get(feature_name, False)

    def get_feature_limit(self, feature_name):
        """Get limit for a specific feature"""
        limit_map = {
            'msme_businesses': self.msme_businesses_limit,
            'workflows': self.workflows_limit,
            'reports': self.reports_limit,
            'users': self.users_limit,
            'storage_gb': self.storage_limit_gb
        }
        return limit_map.get(feature_name, 0)

    def __repr__(self):
        return f"<SolutionLicense(solution='{self.solution_name}', type='{self.license_type.value}')>"


class FeatureUsage(Base):
    """Feature usage tracking - migrated from Django"""

    __tablename__ = 'feature_usage'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_name = Column(String(255), nullable=False)
    feature_name = Column(String(100), nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    period_start = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(FeatureUsageStatus), default=FeatureUsageStatus.ACTIVE, nullable=False)

    # Metadata
    metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def increment_usage(self, count=1):
        """Increment usage count"""
        self.usage_count += count
        if hasattr(self, 'updated_at'):
            self.updated_at = func.now()

    def is_exceeded(self, limit):
        """Check if usage exceeds limit"""
        return self.usage_count >= limit

    def get_usage_percentage(self, limit):
        """Get usage as percentage of limit"""
        if limit <= 0:
            return 0
        return (self.usage_count / limit) * 100

    def __repr__(self):
        return f"<FeatureUsage(feature='{self.feature_name}', count={self.usage_count})>"


class LicenseAuditLog(Base):
    """License audit log for tracking license operations"""

    __tablename__ = 'license_audit_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_name = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)  # create, update, check, expire, etc.
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    performed_by = Column(String(100), nullable=True)  # user ID or system
    ip_address = Column(String(45), nullable=True)  # IPv4/IPv6
    user_agent = Column(String(500), nullable=True)
    metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<LicenseAuditLog(solution='{self.solution_name}', action='{self.action}')>"


class UpgradeRecommendation(Base):
    """Upgrade recommendations for licenses"""

    __tablename__ = 'upgrade_recommendations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_name = Column(String(255), nullable=False)
    current_tier = Column(Enum(LicenseType), nullable=False)
    recommended_tier = Column(Enum(LicenseType), nullable=False)
    reason = Column(String(500), nullable=False)
    feature_usage = Column(JSON, default=dict, nullable=False)
    potential_savings = Column(Float, default=0.0, nullable=False)  # monetary value
    priority = Column(String(20), default='medium', nullable=False)  # low, medium, high
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    def is_expired(self):
        """Check if recommendation is expired"""
        if not self.expires_at:
            return False
        return self.expires_at < func.now()

    def __repr__(self):
        return f"<UpgradeRecommendation(solution='{self.solution_name}', {self.current_tier.value}->{self.recommended_tier.value})>"


# Export all models
__all__ = [
    'SolutionLicense',
    'FeatureUsage',
    'LicenseAuditLog',
    'UpgradeRecommendation',
    'LicenseType',
    'LicenseStatus',
    'FeatureUsageStatus'
]
