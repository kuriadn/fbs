from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class OdooDatabase(models.Model):
    """Model to store Odoo database configurations"""
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    odoo_db_name = models.CharField(max_length=100)
    base_url = models.URLField(default='http://localhost:8069')
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Odoo Database'
        verbose_name_plural = 'Odoo Databases'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.display_name} ({self.name})"


class ApiTokenMapping(models.Model):
    """Model to map Django users to Odoo tokens and databases"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    database = models.ForeignKey(OdooDatabase, on_delete=models.CASCADE)
    odoo_token = models.CharField(max_length=255)
    odoo_user_id = models.IntegerField()
    active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'API Token Mapping'
        verbose_name_plural = 'API Token Mappings'
        unique_together = ['user', 'database']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} -> {self.database.name}"
    
    def is_expired(self):
        """Check if token is expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def update_last_used(self):
        """Update last used timestamp"""
        self.last_used = timezone.now()
        self.save(update_fields=['last_used'])


class RequestLog(models.Model):
    """Model to log API requests for monitoring"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    database = models.ForeignKey(OdooDatabase, on_delete=models.SET_NULL, null=True, blank=True)
    method = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100, blank=True)
    record_id = models.IntegerField(null=True, blank=True)
    request_data = models.JSONField(default=dict)
    response_status = models.IntegerField(null=True, blank=True)
    response_time = models.FloatField(null=True, blank=True)  # in seconds
    error_message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Request Log'
        verbose_name_plural = 'Request Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['database', 'created_at']),
            models.Index(fields=['method', 'endpoint']),
            models.Index(fields=['model_name', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.created_at}"


class BusinessRule(models.Model):
    """Model to store business rules for API operations"""
    name = models.CharField(max_length=200)
    database = models.ForeignKey(OdooDatabase, on_delete=models.CASCADE)
    model_name = models.CharField(max_length=100)
    operation = models.CharField(max_length=20, choices=[
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ])
    conditions = models.JSONField(default=dict)
    actions = models.JSONField(default=dict)
    active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Business Rule'
        verbose_name_plural = 'Business Rules'
        ordering = ['priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.model_name})"


class CacheEntry(models.Model):
    """Model to cache frequently accessed data"""
    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField()
    database = models.ForeignKey(OdooDatabase, on_delete=models.CASCADE, null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cache Entry'
        verbose_name_plural = 'Cache Entries'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cache: {self.key}"
    
    def is_expired(self):
        """Check if cache entry is expired"""
        return timezone.now() > self.expires_at


# FBS Discovery & Schema Management Models
class FBSDiscovery(models.Model):
    """Model to cache discovered models, workflows, and BI features"""
    
    DISCOVERY_TYPES = [
        ('model', 'Model'),
        ('workflow', 'Workflow'),
        ('bi_feature', 'BI Feature'),
    ]
    
    discovery_type = models.CharField(max_length=50, choices=DISCOVERY_TYPES)
    domain = models.CharField(max_length=100)  # 'rental', 'inventory', 'sales'
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20, default='1.0')
    metadata = models.JSONField(default=dict)
    schema_definition = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fbs_discoveries'
        unique_together = ['discovery_type', 'domain', 'name', 'version']
        indexes = [
            models.Index(fields=['domain', 'discovery_type', 'is_active']),
            models.Index(fields=['discovery_type', 'is_active']),
            models.Index(fields=['discovered_at']),
        ]
    
    def __str__(self):
        return f"{self.discovery_type}:{self.domain}:{self.name}"


class FBSSolutionSchema(models.Model):
    """Model to store solution-specific database configurations"""
    
    solution_name = models.CharField(max_length=100)
    domain = models.CharField(max_length=100, blank=True)  # 'rental', 'ecommerce', 'hr'
    database_name = models.CharField(max_length=100)
    database_user = models.CharField(max_length=100)
    database_password = models.CharField(max_length=255)  # Should be encrypted
    table_prefix = models.CharField(max_length=50, default='fbs_')
    business_prefix = models.CharField(max_length=50, blank=True)
    schema_definition = models.JSONField(null=True, blank=True)
    schema_version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'fbs_solution_schemas'
        unique_together = ['solution_name', 'database_name']
        indexes = [
            models.Index(fields=['solution_name', 'is_active']),
            models.Index(fields=['database_name']),
        ]
    
    def __str__(self):
        return f"{self.solution_name}:{self.database_name}"


class FBSSchemaMigration(models.Model):
    """Model to track schema migrations and changes"""
    
    MIGRATION_TYPES = [
        ('create', 'Create'),
        ('alter', 'Alter'),
        ('drop', 'Drop'),
    ]
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    solution_name = models.CharField(max_length=100)
    table_name = models.CharField(max_length=100)
    migration_type = models.CharField(max_length=50, choices=MIGRATION_TYPES)
    old_schema = models.JSONField(null=True, blank=True)
    new_schema = models.JSONField(null=True, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    executed_by = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'fbs_schema_migrations'
        indexes = [
            models.Index(fields=['solution_name', 'table_name']),
            models.Index(fields=['migration_type', 'status']),
            models.Index(fields=['executed_at']),
        ]
    
    def __str__(self):
        return f"{self.solution_name}:{self.table_name}:{self.migration_type}"
