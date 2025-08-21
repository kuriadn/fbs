"""
FBS App MSME Models

Models for MSME-specific business features including setup wizard, KPIs, compliance, marketing, templates, and analytics.
"""

from django.db import models
from django.utils import timezone


class MSMESetupWizard(models.Model):
    """MSME setup wizard for business configuration"""
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    solution_name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    current_step = models.CharField(max_length=100, blank=True)
    total_steps = models.IntegerField(default=0)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    business_type = models.CharField(max_length=100, blank=True)
    configuration = models.JSONField(default=dict)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_msme_setup_wizard'
    
    def __str__(self):
        return f"{self.solution_name} - {self.status}"


class MSMEKPI(models.Model):
    """MSME Key Performance Indicators"""
    
    KPI_TYPES = [
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('customer', 'Customer'),
        ('growth', 'Growth'),
        ('compliance', 'Compliance'),
    ]
    
    solution_name = models.CharField(max_length=100)
    kpi_name = models.CharField(max_length=200)
    kpi_type = models.CharField(max_length=20, choices=KPI_TYPES)
    current_value = models.DecimalField(max_digits=15, decimal_places=2)
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    period = models.CharField(max_length=20, default='monthly')
    trend = models.CharField(max_length=20, blank=True)  # 'up', 'down', 'stable'
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_msme_kpis'
        unique_together = ['solution_name', 'kpi_name', 'period']
    
    def __str__(self):
        return f"{self.solution_name} - {self.kpi_name}"


class MSMECompliance(models.Model):
    """MSME compliance tracking"""
    
    COMPLIANCE_TYPES = [
        ('tax', 'Tax Compliance'),
        ('regulatory', 'Regulatory Compliance'),
        ('financial', 'Financial Compliance'),
        ('operational', 'Operational Compliance'),
    ]
    
    STATUS_CHOICES = [
        ('compliant', 'Compliant'),
        ('non_compliant', 'Non-Compliant'),
        ('at_risk', 'At Risk'),
        ('pending', 'Pending'),
    ]
    
    solution_name = models.CharField(max_length=100)
    compliance_type = models.CharField(max_length=20, choices=COMPLIANCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateField()
    actual_completion_date = models.DateField(null=True, blank=True)
    requirements = models.JSONField(default=list)
    documents = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    last_checked = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_msme_compliance'
        unique_together = ['solution_name', 'compliance_type']
    
    def __str__(self):
        return f"{self.solution_name} - {self.compliance_type}"


class MSMEMarketing(models.Model):
    """MSME marketing data and campaigns"""
    
    CAMPAIGN_TYPES = [
        ('digital', 'Digital Marketing'),
        ('traditional', 'Traditional Marketing'),
        ('social_media', 'Social Media'),
        ('email', 'Email Marketing'),
        ('content', 'Content Marketing'),
    ]
    
    solution_name = models.CharField(max_length=100)
    campaign_name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    target_audience = models.JSONField(default=dict)
    metrics = models.JSONField(default=dict)
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_msme_marketing'
    
    def __str__(self):
        return f"{self.solution_name} - {self.campaign_name}"


class MSMETemplate(models.Model):
    """MSME business templates"""
    
    BUSINESS_TYPES = [
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('services', 'Services'),
        ('restaurant', 'Restaurant'),
        ('consulting', 'Consulting'),
        ('ecommerce', 'E-commerce'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES)
    description = models.TextField()
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_msme_templates'
        unique_together = ['name', 'business_type']
    
    def __str__(self):
        return f"{self.name} ({self.business_type})"


class MSMEAnalytics(models.Model):
    """MSME analytics data"""
    
    solution_name = models.CharField(max_length=100)
    metric_name = models.CharField(max_length=200)
    metric_value = models.DecimalField(max_digits=15, decimal_places=2)
    metric_type = models.CharField(max_length=50)
    period = models.CharField(max_length=20, default='monthly')
    date = models.DateField()
    context = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_msme_analytics'
        indexes = [
            models.Index(fields=['solution_name', 'metric_name', 'date']),
            models.Index(fields=['solution_name', 'period', 'date']),
        ]
    
    def __str__(self):
        return f"{self.solution_name} - {self.metric_name} ({self.date})"
