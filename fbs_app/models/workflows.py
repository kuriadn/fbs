"""
FBS App Workflow Models

Models for managing business workflows and process automation.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class WorkflowDefinition(models.Model):
    """Model to store workflow definitions and templates"""
    
    WORKFLOW_TYPES = [
        ('approval', 'Approval Workflow'),
        ('onboarding', 'Onboarding Workflow'),
        ('order_processing', 'Order Processing'),
        ('payment_collection', 'Payment Collection'),
        ('inventory_management', 'Inventory Management'),
        ('compliance', 'Compliance Workflow'),
        ('custom', 'Custom Workflow'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    workflow_type = models.CharField(max_length=50, choices=WORKFLOW_TYPES)
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)
    is_template = models.BooleanField(default=False)
    trigger_conditions = models.JSONField(default=dict)  # When to start workflow
    workflow_data = models.JSONField(default=dict)  # Workflow configuration
    estimated_duration = models.IntegerField(help_text='Estimated duration in hours', null=True, blank=True)
    solution_name = models.CharField(max_length=100, help_text='Solution this workflow belongs to')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_workflow_definitions'
        unique_together = ['name', 'version', 'solution_name']
        ordering = ['workflow_type', 'name']
        indexes = [
            models.Index(fields=['solution_name', 'workflow_type']),
            models.Index(fields=['solution_name', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} v{self.version} ({self.workflow_type})"


class WorkflowInstance(models.Model):
    """Model to store active workflow instances"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    workflow_definition = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE)
    business_id = models.CharField(max_length=100)  # Reference to business
    current_step = models.ForeignKey('WorkflowStep', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    workflow_data = models.JSONField(default=dict)  # Instance-specific data
    notes = models.TextField(blank=True)
    solution_name = models.CharField(max_length=100, help_text='Solution this workflow instance belongs to')
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_workflow_instances'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['business_id', 'status']),
            models.Index(fields=['current_user', 'status']),
            models.Index(fields=['solution_name', 'status']),
            models.Index(fields=['solution_name', 'business_id']),
        ]
    
    def __str__(self):
        return f"{self.workflow_definition.name} - {self.business_id} ({self.status})"


class WorkflowStep(models.Model):
    """Model to store workflow steps"""
    
    STEP_TYPES = [
        ('task', 'Task'),
        ('approval', 'Approval'),
        ('notification', 'Notification'),
        ('decision', 'Decision'),
        ('integration', 'Integration'),
        ('manual', 'Manual Step'),
    ]
    
    workflow_definition = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(max_length=200)
    step_type = models.CharField(max_length=50, choices=STEP_TYPES)
    order = models.IntegerField()
    is_required = models.BooleanField(default=True)
    estimated_duration = models.IntegerField(help_text='Estimated duration in hours', null=True, blank=True)
    assigned_role = models.CharField(max_length=100, blank=True)
    assigned_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    step_data = models.JSONField(default=dict)  # Step-specific configuration
    conditions = models.JSONField(default=dict)  # Step execution conditions
    actions = models.JSONField(default=list)  # Actions to perform
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_workflow_steps'
        unique_together = ['workflow_definition', 'order']
        ordering = ['workflow_definition', 'order']
    
    def __str__(self):
        return f"{self.workflow_definition.name} - Step {self.order}: {self.name}"


class WorkflowTransition(models.Model):
    """Model to store workflow transitions between steps"""
    
    TRANSITION_TYPES = [
        ('automatic', 'Automatic'),
        ('conditional', 'Conditional'),
        ('manual', 'Manual'),
        ('timeout', 'Timeout'),
    ]
    
    workflow_definition = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE, related_name='transitions')
    from_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE, related_name='outgoing_transitions')
    to_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE, related_name='incoming_transitions')
    transition_type = models.CharField(max_length=50, choices=TRANSITION_TYPES, default='automatic')
    conditions = models.JSONField(default=dict)  # Transition conditions
    actions = models.JSONField(default=list)  # Actions on transition
    is_default = models.BooleanField(default=False)  # Default transition
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_workflow_transitions'
        unique_together = ['workflow_definition', 'from_step', 'to_step']
        ordering = ['workflow_definition', 'from_step__order']
    
    def __str__(self):
        return f"{self.from_step.name} → {self.to_step.name}"
