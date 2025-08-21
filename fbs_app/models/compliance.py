"""
FBS App Compliance Models

Models for compliance management including rules, deadlines, and audit trails.
"""

from django.db import models
from django.utils import timezone


class ComplianceRule(models.Model):
    """Compliance rules for business operations"""
    
    COMPLIANCE_TYPES = [
        ('tax', 'Tax Compliance'),
        ('regulatory', 'Regulatory Compliance'),
        ('audit', 'Audit Compliance'),
        ('financial', 'Financial Compliance'),
        ('operational', 'Operational Compliance'),
    ]
    
    CHECK_FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    solution_name = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    compliance_type = models.CharField(max_length=20, choices=COMPLIANCE_TYPES)
    requirements = models.JSONField(default=list)
    check_frequency = models.CharField(max_length=20, choices=CHECK_FREQUENCIES, default='monthly')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_compliance_rules'
        unique_together = ['solution_name', 'name']
    
    def __str__(self):
        return f"{self.solution_name} - {self.name}"


class AuditTrail(models.Model):
    """Audit trail for business operations"""
    
    RECORD_TYPES = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('payment', 'Payment'),
        ('inventory', 'Inventory'),
        ('user', 'User'),
        ('system', 'System'),
    ]
    
    ACTIONS = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
    ]
    
    solution_name = models.CharField(max_length=100)
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    record_id = models.CharField(max_length=100)
    action = models.CharField(max_length=20, choices=ACTIONS)
    user_id = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_audit_trails'
        indexes = [
            models.Index(fields=['solution_name', 'record_type', 'timestamp']),
            models.Index(fields=['solution_name', 'user_id', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.solution_name} - {self.record_type} {self.record_id} {self.action}"


class ReportSchedule(models.Model):
    """Scheduled reports for compliance and business intelligence"""
    
    FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    solution_name = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50)
    frequency = models.CharField(max_length=20, choices=FREQUENCIES)
    next_run = models.DateTimeField()
    active = models.BooleanField(default=True)
    configuration = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_report_schedules'
        unique_together = ['solution_name', 'name']
    
    def __str__(self):
        return f"{self.solution_name} - {self.name}"


class RecurringTransaction(models.Model):
    """Recurring transactions for accounting"""
    
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('payment', 'Payment'),
        ('receipt', 'Receipt'),
    ]
    
    FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    solution_name = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCIES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_recurring_transactions'
    
    def __str__(self):
        return f"{self.solution_name} - {self.name}"


class UserActivityLog(models.Model):
    """User activity logging for analytics and security"""
    
    solution_name = models.CharField(max_length=100)
    user_id = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    details = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_user_activity_logs'
        indexes = [
            models.Index(fields=['solution_name', 'user_id', 'timestamp']),
            models.Index(fields=['solution_name', 'action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.solution_name} - {self.user_id} {self.action}"
