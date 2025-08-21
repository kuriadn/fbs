"""
FBS App Discovery Models

Models for discovering and managing Odoo models, fields, and modules.
"""

from django.db import models
from django.utils import timezone
import json


class OdooModel(models.Model):
    """Model to store discovered Odoo models"""
    
    MODEL_TYPES = [
        ('base', 'Base Model'),
        ('business', 'Business Model'),
        ('system', 'System Model'),
        ('custom', 'Custom Model'),
    ]
    
    database_name = models.CharField(max_length=100)  # Odoo database name
    model_name = models.CharField(max_length=100)
    technical_name = models.CharField(max_length=100)  # Odoo technical name
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    module_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_installed = models.BooleanField(default=True)
    model_type = models.CharField(max_length=50, choices=MODEL_TYPES, default='business')
    capabilities = models.JSONField(default=list)  # Available operations
    constraints = models.JSONField(default=dict)  # Model constraints
    discovered_at = models.DateTimeField(auto_now_add=True)
    last_verified = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_odoo_models'
        unique_together = ['database_name', 'model_name']
        indexes = [
            models.Index(fields=['database_name', 'module_name']),
            models.Index(fields=['model_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.model_name} ({self.database_name})"


class OdooField(models.Model):
    """Model to store discovered Odoo model fields"""
    
    odoo_model = models.ForeignKey(OdooModel, on_delete=models.CASCADE, related_name='fields')
    field_name = models.CharField(max_length=100)
    technical_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=100)
    required = models.BooleanField(default=False)
    readonly = models.BooleanField(default=False)
    computed = models.BooleanField(default=False)
    stored = models.BooleanField(default=True)
    default_value = models.TextField(blank=True)
    help_text = models.TextField(blank=True)
    selection_options = models.JSONField(default=list)  # For selection fields
    relation_model = models.CharField(max_length=100, blank=True)  # For relational fields
    field_constraints = models.JSONField(default=dict)
    discovered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_odoo_fields'
        unique_together = ['odoo_model', 'field_name']
        indexes = [
            models.Index(fields=['field_type']),
            models.Index(fields=['required', 'readonly']),
        ]
    
    def __str__(self):
        return f"{self.field_name} ({self.odoo_model.model_name})"


class OdooModule(models.Model):
    """Model to store discovered Odoo modules"""
    
    database_name = models.CharField(max_length=100)  # Odoo database name
    module_name = models.CharField(max_length=100)
    technical_name = models.CharField(max_length=100)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50)
    author = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)
    category = models.CharField(max_length=100)
    is_installed = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    auto_install = models.BooleanField(default=False)
    depends = models.JSONField(default=list)  # Module dependencies
    data_files = models.JSONField(default=list)  # Data files
    demo_data = models.BooleanField(default=False)
    application = models.BooleanField(default=False)
    discovered_at = models.DateTimeField(auto_now_add=True)
    last_verified = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_odoo_modules'
        unique_together = ['database_name', 'module_name']
        indexes = [
            models.Index(fields=['database_name', 'is_installed']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.module_name} v{self.version} ({self.database_name})"


class DiscoverySession(models.Model):
    """Model to store discovery sessions and results"""
    
    SESSION_STATUS = [
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    session_id = models.CharField(max_length=100, unique=True)
    database_name = models.CharField(max_length=100)
    session_type = models.CharField(max_length=50)  # 'full', 'incremental', 'targeted'
    status = models.CharField(max_length=20, choices=SESSION_STATUS, default='running')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_models = models.IntegerField(default=0)
    total_fields = models.IntegerField(default=0)
    total_modules = models.IntegerField(default=0)
    errors = models.JSONField(default=list)
    configuration = models.JSONField(default=dict)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_discovery_sessions'
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['database_name', 'status']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"{self.session_id} - {self.database_name} ({self.status})"
