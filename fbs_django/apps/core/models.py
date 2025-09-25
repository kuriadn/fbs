"""
Core FBS Django models

Multi-tenant architecture with FBS-specific user model and solution management.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError


class FBSSolution(models.Model):
    """Multi-tenant solution configuration"""

    name = models.CharField(max_length=100, unique=True, help_text="Unique solution identifier")
    display_name = models.CharField(max_length=200, help_text="Human-readable solution name")
    database_name = models.CharField(max_length=100, help_text="Solution-specific database name")
    odoo_database_name = models.CharField(max_length=100, help_text="Odoo database for this solution")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether this solution is active")

    class Meta:
        db_table = 'fbs_solutions'
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.name})"

    def clean(self):
        """Validate solution data"""
        if not self.name.islower():
            raise ValidationError("Solution name must be lowercase")
        if ' ' in self.name:
            raise ValidationError("Solution name cannot contain spaces")


class FBSUser(AbstractUser):
    """Extended user model for FBS with multi-tenant support"""

    solution = models.ForeignKey(
        FBSSolution,
        on_delete=models.CASCADE,
        related_name='users',
        help_text="The solution this user belongs to"
    )
    odoo_user_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="Corresponding Odoo user ID"
    )
    is_solution_admin = models.BooleanField(
        default=False,
        help_text="Whether this user is an admin for their solution"
    )

    # Profile fields
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="User profile picture"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="User's department"
    )

    class Meta:
        db_table = 'fbs_users'
        unique_together = ['username', 'solution']
        indexes = [
            models.Index(fields=['solution', 'username']),
            models.Index(fields=['solution', 'email']),
            models.Index(fields=['odoo_user_id']),
        ]

    def __str__(self):
        return f"{self.username} ({self.solution.name})"

    @property
    def full_solution_name(self):
        """Get the full solution display name"""
        return self.solution.display_name


class FBSAuditLog(models.Model):
    """Comprehensive audit trail for all FBS operations"""

    ACTION_TYPES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('access', 'Access'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]

    RESOURCE_TYPES = [
        ('user', 'User'),
        ('document', 'Document'),
        ('workflow', 'Workflow'),
        ('license', 'License'),
        ('module', 'Module'),
        ('solution', 'Solution'),
        ('odoo_record', 'Odoo Record'),
    ]

    user = models.ForeignKey(
        FBSUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    solution = models.ForeignKey(
        FBSSolution,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        help_text="Solution where the action occurred"
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        help_text="Type of action performed"
    )
    resource_type = models.CharField(
        max_length=20,
        choices=RESOURCE_TYPES,
        help_text="Type of resource affected"
    )
    resource_id = models.CharField(
        max_length=100,
        help_text="ID of the affected resource"
    )

    # Action details
    details = models.JSONField(
        default=dict,
        help_text="Additional details about the action"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        blank=True,
        help_text="User agent string"
    )

    # Timestamps
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the action occurred"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fbs_audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['solution', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.action} {self.resource_type} by {self.user or 'System'} at {self.timestamp}"


class FBSAPIToken(models.Model):
    """API tokens for FBS authentication"""

    user = models.ForeignKey(
        FBSUser,
        on_delete=models.CASCADE,
        related_name='api_tokens',
        help_text="User this token belongs to"
    )
    name = models.CharField(
        max_length=100,
        help_text="Human-readable token name"
    )
    token = models.CharField(
        max_length=256,
        unique=True,
        help_text="The actual token string"
    )

    # Permissions and scope
    scopes = models.JSONField(
        default=list,
        help_text="API scopes this token has access to"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this token is active"
    )

    # Expiration
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this token expires"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this token was used"
    )
    created_by_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address that created this token"
    )

    class Meta:
        db_table = 'fbs_api_tokens'
        unique_together = ['user', 'name']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.name} for {self.user.username}"

    def is_expired(self):
        """Check if the token is expired"""
        if self.expires_at and timezone.now() > self.expires_at:
            return True
        return False

    def can_access_scope(self, scope):
        """Check if token can access a specific scope"""
        return scope in self.scopes or 'all' in self.scopes


class FBSSystemSettings(models.Model):
    """Global system settings for FBS"""

    SETTING_TYPES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('file', 'File'),
    ]

    key = models.CharField(
        max_length=100,
        unique=True,
        help_text="Setting key"
    )
    value = models.TextField(
        help_text="Setting value"
    )
    setting_type = models.CharField(
        max_length=20,
        choices=SETTING_TYPES,
        default='string',
        help_text="Type of the setting value"
    )

    description = models.TextField(
        blank=True,
        help_text="Description of what this setting does"
    )
    is_system_setting = models.BooleanField(
        default=False,
        help_text="Whether this is a core system setting"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fbs_system_settings'
        ordering = ['key']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['setting_type']),
        ]

    def __str__(self):
        return f"{self.key}: {self.value[:50]}..."

    def get_typed_value(self):
        """Get the value cast to the appropriate type"""
        if self.setting_type == 'integer':
            return int(self.value)
        elif self.setting_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.setting_type == 'json':
            import json
            return json.loads(self.value)
        else:
            return self.value