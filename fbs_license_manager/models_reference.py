"""
FBS License Manager Reference Models

These models serve as UI references for licenses stored in Odoo + FBS virtual fields.
They provide Django ORM access for UI operations while keeping data in the proper systems.
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class LicenseReference(models.Model):
    """Reference model for licenses - actual data in Odoo + FBS virtual fields"""
    
    # Core reference fields
    odoo_id = models.IntegerField(unique=True, help_text='Odoo res.partner ID')
    company_id = models.CharField(max_length=100, help_text='Solution/company identifier')
    
    # UI-only fields (not stored in Odoo)
    ui_status = models.CharField(
        max_length=20, 
        default='active',
        choices=[
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled')
        ],
        help_text='UI status for display purposes'
    )
    ui_notes = models.TextField(blank=True, help_text='Internal notes for UI management')
    ui_tags = models.CharField(max_length=500, blank=True, help_text='Comma-separated tags for UI organization')
    
    # Django metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_licenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_licenses', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fbs_license_reference'
        verbose_name = 'License Reference'
        verbose_name_plural = 'License References'
        indexes = [
            models.Index(fields=['company_id']),
            models.Index(fields=['ui_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"License {self.odoo_id} - {self.company_id}"
    
    @property
    def is_active(self):
        """Check if license is active based on UI status"""
        return self.ui_status == 'active'
    
    @property
    def needs_renewal(self):
        """Check if license needs renewal (placeholder for Odoo data)"""
        # This would check the expiry_date from Odoo + FBS virtual fields
        return False


class FeatureUsageLog(models.Model):
    """Log of feature usage for analytics and debugging"""
    
    license_reference = models.ForeignKey(LicenseReference, on_delete=models.CASCADE, related_name='usage_logs')
    feature_name = models.CharField(max_length=100, help_text='Name of the feature being used')
    usage_amount = models.IntegerField(default=1, help_text='Amount of usage consumed')
    usage_type = models.CharField(
        max_length=20,
        choices=[
            ('increment', 'Increment'),
            ('decrement', 'Decrement'),
            ('reset', 'Reset'),
            ('set', 'Set Value')
        ],
        default='increment'
    )
    
    # Context information
    user_id = models.IntegerField(null=True, blank=True, help_text='User ID who triggered the usage')
    session_id = models.CharField(max_length=100, blank=True, help_text='Session identifier')
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text='IP address of the request')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text='Additional context about this usage')
    
    class Meta:
        db_table = 'fbs_license_feature_usage_log'
        verbose_name = 'Feature Usage Log'
        verbose_name_plural = 'Feature Usage Logs'
        indexes = [
            models.Index(fields=['license_reference', 'feature_name']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"{self.feature_name} usage by {self.license_reference} at {self.created_at}"


class LicenseAuditLog(models.Model):
    """Audit log for license changes and access attempts"""
    
    license_reference = models.ForeignKey(LicenseReference, on_delete=models.CASCADE, related_name='audit_logs')
    
    # Action details
    action = models.CharField(
        max_length=50,
        choices=[
            ('created', 'License Created'),
            ('updated', 'License Updated'),
            ('deleted', 'License Deleted'),
            ('feature_access', 'Feature Access Attempt'),
            ('usage_update', 'Usage Updated'),
            ('status_change', 'Status Changed'),
            ('renewal', 'License Renewed'),
            ('suspension', 'License Suspended')
        ],
        help_text='Type of action performed'
    )
    
    # Result information
    success = models.BooleanField(help_text='Whether the action was successful')
    error_message = models.TextField(blank=True, help_text='Error message if action failed')
    
    # Context information
    user_id = models.IntegerField(null=True, blank=True, help_text='User ID who performed the action')
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text='IP address of the request')
    user_agent = models.TextField(blank=True, help_text='User agent string')
    
    # Additional data
    old_values = models.JSONField(null=True, blank=True, help_text='Previous values before change')
    new_values = models.JSONField(null=True, blank=True, help_text='New values after change')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fbs_license_audit_log'
        verbose_name = 'License Audit Log'
        verbose_name_plural = 'License Audit Logs'
        indexes = [
            models.Index(fields=['license_reference', 'action']),
            models.Index(fields=['created_at']),
            models.Index(fields=['success']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"{self.action} on {self.license_reference} at {self.created_at}"


class LicenseTemplate(models.Model):
    """Template for creating new licenses with predefined settings"""
    
    name = models.CharField(max_length=100, unique=True, help_text='Template name')
    description = models.TextField(blank=True, help_text='Template description')
    
    # Default license settings
    default_license_type = models.CharField(max_length=50, default='standard', help_text='Default license type')
    default_features = models.JSONField(default=dict, help_text='Default feature flags')
    default_limits = models.JSONField(default=dict, help_text='Default usage limits')
    
    # Billing defaults
    default_billing_cycle = models.CharField(max_length=20, default='monthly', help_text='Default billing cycle')
    default_billing_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text='Default billing amount'
    )
    
    # Template metadata
    is_active = models.BooleanField(default=True, help_text='Whether this template is active')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fbs_license_template'
        verbose_name = 'License Template'
        verbose_name_plural = 'License Templates'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['default_license_type']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_default_features(self):
        """Get default features as a dictionary"""
        return self.default_features or {}
    
    def get_default_limits(self):
        """Get default limits as a dictionary"""
        return self.default_limits or {}


class LicenseFeature(models.Model):
    """Definition of available license features"""
    
    name = models.CharField(max_length=100, unique=True, help_text='Feature name')
    code = models.CharField(max_length=50, unique=True, help_text='Feature code for programmatic access')
    description = models.TextField(help_text='Feature description')
    
    # Feature characteristics
    feature_type = models.CharField(
        max_length=20,
        choices=[
            ('boolean', 'Boolean (enabled/disabled)'),
            ('numeric', 'Numeric (with limits)'),
            ('time_based', 'Time-based (duration)'),
            ('storage', 'Storage (capacity)'),
            ('api', 'API (rate limits)')
        ],
        default='boolean',
        help_text='Type of feature'
    )
    
    # Default values
    default_enabled = models.BooleanField(default=False, help_text='Default enabled state')
    default_limit = models.IntegerField(null=True, blank=True, help_text='Default numeric limit')
    default_unit = models.CharField(max_length=20, blank=True, help_text='Unit for numeric features (e.g., users, GB)')
    
    # Feature metadata
    is_active = models.BooleanField(default=True, help_text='Whether this feature is active')
    requires_approval = models.BooleanField(default=False, help_text='Whether feature requires approval to enable')
    category = models.CharField(max_length=50, blank=True, help_text='Feature category for organization')
    
    # Django metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fbs_license_feature'
        verbose_name = 'License Feature'
        verbose_name_plural = 'License Features'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['feature_type']),
            models.Index(fields=['category']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def is_numeric(self):
        """Check if feature is numeric type"""
        return self.feature_type in ['numeric', 'storage', 'api']
    
    def is_boolean(self):
        """Check if feature is boolean type"""
        return self.feature_type == 'boolean'
