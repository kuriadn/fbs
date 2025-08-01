"""
Workflow Data Models

Defines the data structures for workflow definitions, instances, and transitions
that align with Odoo v17 CE workflow patterns.
"""

from django.db import models
from django.contrib.auth.models import User
from typing import Dict, Any, List, Optional
import uuid


class WorkflowDefinition(models.Model):
    """
    Workflow definition - similar to Odoo's ir.actions.server but more flexible
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Odoo model this workflow applies to
    model_name = models.CharField(max_length=255)
    database = models.ForeignKey('fayvad_core.OdooDatabase', on_delete=models.CASCADE)
    
    # Workflow configuration
    trigger_type = models.CharField(max_length=50, choices=[
        ('on_create', 'On Record Creation'),
        ('on_update', 'On Record Update'),
        ('on_delete', 'On Record Deletion'),
        ('on_state_change', 'On State Change'),
        ('manual', 'Manual Trigger'),
        ('scheduled', 'Scheduled'),
        ('webhook', 'Webhook'),
    ])
    
    # Trigger conditions (JSON)
    trigger_conditions = models.JSONField(default=dict, blank=True)
    
    # Workflow steps (JSON array of actions)
    workflow_steps = models.JSONField(default=list)
    
    # State machine definition
    states = models.JSONField(default=dict)  # {state_name: {transitions: [], actions: []}}
    initial_state = models.CharField(max_length=100, default='draft')
    
    # Approval workflow settings
    requires_approval = models.BooleanField(default=False)
    approval_roles = models.JSONField(default=list, blank=True)  # List of role names
    
    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=255, blank=True)  # Cron expression
    schedule_interval = models.IntegerField(default=0)  # Minutes
    
    # Status
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'fbs_workflow_definitions'
        unique_together = ['name', 'model_name', 'database']
        indexes = [
            models.Index(fields=['model_name', 'database', 'active']),
            models.Index(fields=['trigger_type', 'active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.model_name})"


class WorkflowInstance(models.Model):
    """
    Active workflow instance for a specific record
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_definition = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE)
    
    # Odoo record reference
    odoo_record_id = models.IntegerField()
    odoo_model_name = models.CharField(max_length=255)
    database = models.ForeignKey('fayvad_core.OdooDatabase', on_delete=models.CASCADE)
    
    # Current state
    current_state = models.CharField(max_length=100)
    
    # Workflow data
    workflow_data = models.JSONField(default=dict)  # Data passed between steps
    context_data = models.JSONField(default=dict)   # Original trigger context
    
    # Execution tracking
    current_step = models.IntegerField(default=0)
    completed_steps = models.JSONField(default=list)
    failed_steps = models.JSONField(default=list)
    
    # Approval tracking
    approval_status = models.CharField(max_length=50, default='pending', choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ])
    approval_history = models.JSONField(default=list)
    
    # Status
    status = models.CharField(max_length=50, default='running', choices=[
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ])
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_executed_at = models.DateTimeField(auto_now=True)
    
    # User tracking
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='initiated_workflows')
    current_assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_workflows')
    
    class Meta:
        db_table = 'fbs_workflow_instances'
        unique_together = ['workflow_definition', 'odoo_record_id', 'odoo_model_name', 'database']
        indexes = [
            models.Index(fields=['odoo_model_name', 'odoo_record_id', 'database']),
            models.Index(fields=['status', 'current_state']),
            models.Index(fields=['current_assignee', 'status']),
        ]
    
    def __str__(self):
        return f"{self.workflow_definition.name} - {self.odoo_model_name}:{self.odoo_record_id}"


class WorkflowTransition(models.Model):
    """
    Workflow state transitions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_definition = models.ForeignKey(WorkflowDefinition, on_delete=models.CASCADE)
    
    from_state = models.CharField(max_length=100)
    to_state = models.CharField(max_length=100)
    
    # Transition conditions
    conditions = models.JSONField(default=dict, blank=True)
    
    # Actions to execute on transition
    actions = models.JSONField(default=list, blank=True)
    
    # Transition metadata
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Permissions
    required_roles = models.JSONField(default=list, blank=True)
    requires_approval = models.BooleanField(default=False)
    
    # UI/UX
    button_text = models.CharField(max_length=100, blank=True)
    button_style = models.CharField(max_length=50, default='primary', choices=[
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('success', 'Success'),
        ('danger', 'Danger'),
        ('warning', 'Warning'),
        ('info', 'Info'),
    ])
    
    # Ordering
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'fbs_workflow_transitions'
        unique_together = ['workflow_definition', 'from_state', 'to_state']
        ordering = ['order']
    
    def __str__(self):
        return f"{self.from_state} → {self.to_state} ({self.workflow_definition.name})"


class WorkflowExecutionLog(models.Model):
    """
    Audit log for workflow executions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE)
    
    # Execution details
    step_name = models.CharField(max_length=255)
    step_type = models.CharField(max_length=50)  # action, transition, approval, etc.
    
    # Execution result
    status = models.CharField(max_length=50, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ])
    
    # Data
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Metadata
    execution_time_ms = models.IntegerField(default=0)
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'fbs_workflow_execution_logs'
        indexes = [
            models.Index(fields=['workflow_instance', 'executed_at']),
            models.Index(fields=['status', 'executed_at']),
        ]
    
    def __str__(self):
        return f"{self.step_name} - {self.status} ({self.executed_at})" 