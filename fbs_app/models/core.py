"""
FBS App Core Models

Core models for the FBS application including databases, tokens, logs, and business rules.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import json
import uuid
from datetime import timedelta
import secrets
import logging

logger = logging.getLogger(__name__)


class OdooDatabase(models.Model):
    """Model to store Odoo database configurations"""
    
    name = models.CharField(max_length=100, unique=True)
    host = models.CharField(max_length=255)
    port = models.IntegerField(default=8069)
    protocol = models.CharField(max_length=10, default='http')
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_odoo_databases'
        verbose_name = 'Odoo Database'
        verbose_name_plural = 'Odoo Databases'
    
    def __str__(self):
        return f"{self.name} ({self.host}:{self.port})"


class TokenMapping(models.Model):
    """Model to store token mappings for users and databases"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    database = models.ForeignKey(OdooDatabase, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_token_mappings'
        unique_together = ['user', 'database']
    
    def __str__(self):
        return f"{self.user.username} - {self.database.name}"


class RequestLog(models.Model):
    """Model to store request logs"""
    
    REQUEST_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    database = models.ForeignKey(OdooDatabase, on_delete=models.SET_NULL, null=True, blank=True)
    method = models.CharField(max_length=10, choices=REQUEST_METHODS)
    path = models.CharField(max_length=500)
    status_code = models.IntegerField()
    response_time = models.FloatField(help_text='Response time in milliseconds')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_request_logs'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['database', 'timestamp']),
            models.Index(fields=['status_code', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code} ({self.timestamp})"


class BusinessRule(models.Model):
    """Model to store business rules for validation"""
    
    RULE_TYPES = [
        ('validation', 'Validation Rule'),
        ('calculation', 'Calculation Rule'),
        ('workflow', 'Workflow Rule'),
        ('compliance', 'Compliance Rule'),
    ]
    
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    description = models.TextField()
    model_name = models.CharField(max_length=100)
    rule_definition = models.JSONField()
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_business_rules'
        ordering = ['priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.rule_type})"


class CacheEntry(models.Model):
    """Model to store cache entries"""
    
    key = models.CharField(max_length=500, unique=True)
    value = models.JSONField()
    database_name = models.CharField(max_length=100, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_cache_entries'
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['database_name', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.key} (expires: {self.expires_at})"


class Handshake(models.Model):
    """Model to store handshake authentication sessions"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ]
    
    handshake_id = models.CharField(max_length=100, unique=True)
    solution_name = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_handshakes'
        indexes = [
            models.Index(fields=['handshake_id']),
            models.Index(fields=['solution_name', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.solution_name} - {self.handshake_id} ({self.status})"


class Notification(models.Model):
    """Model to store system notifications"""
    
    NOTIFICATION_TYPES = [
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('alert', 'Alert'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info')
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    solution_name = models.CharField(max_length=100, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['solution_name', 'is_read']),
            models.Index(fields=['notification_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.notification_type})"


class ApprovalRequest(models.Model):
    """Model to store approval requests"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    APPROVAL_TYPES = [
        ('workflow', 'Workflow Approval'),
        ('document', 'Document Approval'),
        ('purchase', 'Purchase Approval'),
        ('expense', 'Expense Approval'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    approval_type = models.CharField(max_length=20, choices=APPROVAL_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_requests')
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approvals_to_review', null=True, blank=True)
    solution_name = models.CharField(max_length=100, blank=True)
    request_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_approval_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['requester', 'status']),
            models.Index(fields=['approver', 'status']),
            models.Index(fields=['solution_name', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.requester.username} ({self.status})"


class ApprovalResponse(models.Model):
    """Model to store approval responses"""
    
    approval_request = models.ForeignKey(ApprovalRequest, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    response = models.CharField(max_length=20, choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('request_changes', 'Request Changes'),
    ])
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_approval_responses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.approval_request.title} - {self.responder.username} ({self.response})"


class CustomField(models.Model):
    """Model to store custom fields for dynamic data extension"""
    
    FIELD_TYPES = [
        ('char', 'Character'),
        ('text', 'Text'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('date', 'Date'),
        ('datetime', 'DateTime'),
        ('json', 'JSON'),
        ('choice', 'Choice'),
    ]
    
    model_name = models.CharField(max_length=100)
    record_id = models.IntegerField()
    field_name = models.CharField(max_length=100)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default='char')
    field_value = models.TextField()
    database_name = models.CharField(max_length=100, blank=True)
    solution_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_custom_fields'
        unique_together = ['model_name', 'record_id', 'field_name', 'database_name']
        indexes = [
            models.Index(fields=['model_name', 'record_id']),
            models.Index(fields=['database_name', 'model_name']),
            models.Index(fields=['solution_name', 'model_name']),
        ]
    
    def __str__(self):
        return f"{self.model_name}.{self.field_name} (ID: {self.record_id})"
    
    @classmethod
    def set_custom_field(cls, model_name: str, record_id: int, field_name: str, field_value: any, 
                        field_type: str = 'char', database_name: str = None, solution_name: str = None) -> 'CustomField':
        """Set or update a custom field value"""
        try:
            # Convert value to string for storage
            if isinstance(field_value, (dict, list)):
                import json
                field_value = json.dumps(field_value)
            else:
                field_value = str(field_value)
            
            custom_field, created = cls.objects.get_or_create(
                model_name=model_name,
                record_id=record_id,
                field_name=field_name,
                database_name=database_name or '',
                solution_name=solution_name or '',
                defaults={
                    'field_type': field_type,
                    'field_value': field_value,
                }
            )
            
            if not created:
                custom_field.field_value = field_value
                custom_field.field_type = field_type
                custom_field.save()
            
            return custom_field
            
        except Exception as e:
            logger.error(f"Error setting custom field: {str(e)}")
            raise
    
    @classmethod
    def get_custom_field(cls, model_name: str, record_id: int, field_name: str, 
                        database_name: str = None, solution_name: str = None) -> any:
        """Get a custom field value"""
        try:
            custom_field = cls.objects.get(
                model_name=model_name,
                record_id=record_id,
                field_name=field_name,
                database_name=database_name or '',
                solution_name=solution_name or '',
                is_active=True
            )
            
            # Convert value back to appropriate type
            if custom_field.field_type == 'json':
                import json
                return json.loads(custom_field.field_value)
            elif custom_field.field_type == 'integer':
                return int(custom_field.field_value)
            elif custom_field.field_type == 'float':
                return float(custom_field.field_value)
            elif custom_field.field_type == 'boolean':
                return custom_field.field_value.lower() in ('true', '1', 'yes')
            else:
                return custom_field.field_value
                
        except cls.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting custom field: {str(e)}")
            return None
