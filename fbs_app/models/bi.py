"""
FBS App Business Intelligence Models

Models for managing dashboards, reports, KPIs, and analytics.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Dashboard(models.Model):
    """Model to store dashboard configurations"""
    
    DASHBOARD_TYPES = [
        ('msme', 'MSME Dashboard'),
        ('financial', 'Financial Dashboard'),
        ('operational', 'Operational Dashboard'),
        ('compliance', 'Compliance Dashboard'),
        ('custom', 'Custom Dashboard'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    dashboard_type = models.CharField(max_length=50, choices=DASHBOARD_TYPES)
    layout = models.JSONField(default=dict)  # Dashboard layout configuration
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    refresh_interval = models.IntegerField(default=300, help_text='Refresh interval in seconds')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_dashboards'
        ordering = ['dashboard_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.dashboard_type})"


class Report(models.Model):
    """Model to store report configurations"""
    
    REPORT_TYPES = [
        ('sales', 'Sales Report'),
        ('financial', 'Financial Report'),
        ('inventory', 'Inventory Report'),
        ('compliance', 'Compliance Report'),
        ('operational', 'Operational Report'),
        ('custom', 'Custom Report'),
    ]
    
    OUTPUT_FORMATS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    data_source = models.CharField(max_length=100)
    query_parameters = models.JSONField(default=dict)  # Report parameters
    output_format = models.CharField(max_length=20, choices=OUTPUT_FORMATS, default='pdf')
    template = models.TextField(blank=True)  # Report template
    is_scheduled = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_reports'
        ordering = ['report_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.report_type})"


class KPI(models.Model):
    """Model to store Key Performance Indicators"""
    
    KPI_TYPES = [
        ('financial', 'Financial'),
        ('operational', 'Operational'),
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('compliance', 'Compliance'),
        ('growth', 'Growth'),
    ]
    
    FREQUENCIES = [
        ('real_time', 'Real-time'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    kpi_type = models.CharField(max_length=50, choices=KPI_TYPES)
    calculation_method = models.CharField(max_length=100)
    data_source = models.CharField(max_length=100)
    target_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    warning_threshold = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    critical_threshold = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCIES, default='daily')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_kpis'
        ordering = ['kpi_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.kpi_type})"


class Chart(models.Model):
    """Model to store chart configurations for dashboards"""
    
    CHART_TYPES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('area', 'Area Chart'),
        ('scatter', 'Scatter Plot'),
        ('table', 'Data Table'),
        ('gauge', 'Gauge'),
        ('metric', 'Metric'),
    ]
    
    name = models.CharField(max_length=200)
    chart_type = models.CharField(max_length=50, choices=CHART_TYPES)
    description = models.TextField(blank=True)
    data_source = models.CharField(max_length=100)
    configuration = models.JSONField(default=dict)  # Chart-specific configuration
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_app'
        db_table = 'fbs_charts'
        ordering = ['chart_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.chart_type})"
