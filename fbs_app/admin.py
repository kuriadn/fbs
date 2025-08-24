"""
FBS App Admin Configuration

Django admin interface configuration for the FBS app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

# Import models
from .models.core import (
    OdooDatabase, TokenMapping, RequestLog, BusinessRule,
    CacheEntry, Handshake, Notification, ApprovalRequest, ApprovalResponse
)
from .models.msme import (
    MSMESetupWizard, MSMEKPI, MSMECompliance, MSMEMarketing, 
    MSMETemplate, MSMEAnalytics
)

# Licensing Models - Now handled by fbs_license_manager app
from .models.core import CustomField
from .models.discovery import OdooModel, OdooField, OdooModule
from .models.workflows import (
    WorkflowDefinition, WorkflowInstance, WorkflowStep, WorkflowTransition
)
from .models.bi import (
    Dashboard, Report, KPI, Chart
)
from .models.compliance import (
    ComplianceRule, AuditTrail, ReportSchedule, RecurringTransaction, UserActivityLog
)
from .models.accounting import (
    CashEntry, IncomeExpense, BasicLedger, TaxCalculation
)


# Core Models Admin
@admin.register(OdooDatabase)
class OdooDatabaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'host', 'port', 'protocol', 'username', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'host', 'username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(TokenMapping)
class TokenMappingAdmin(admin.ModelAdmin):
    list_display = ['user', 'database', 'token', 'is_active', 'expires_at', 'created_at']
    list_filter = ['is_active', 'database', 'created_at']
    search_fields = ['user__username', 'database__name']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = ['method', 'path', 'user', 'database', 'status_code', 'response_time', 'timestamp']
    list_filter = ['method', 'status_code', 'timestamp', 'database']
    search_fields = ['path', 'user__username', 'database__name']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
    list_per_page = 100


@admin.register(BusinessRule)
class BusinessRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'is_active', 'priority', 'created_at']
    list_filter = ['rule_type', 'is_active', 'priority', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['priority', 'name']


@admin.register(CacheEntry)
class CacheEntryAdmin(admin.ModelAdmin):
    list_display = ['key', 'expires_at', 'created_at']
    list_filter = ['expires_at', 'created_at']
    search_fields = ['key']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Handshake)
class HandshakeAdmin(admin.ModelAdmin):
    list_display = ['handshake_id', 'solution_name', 'status', 'expires_at', 'created_at']
    list_filter = ['status', 'expires_at', 'created_at']
    search_fields = ['handshake_id', 'solution_name']
    readonly_fields = ['created_at', 'last_used']
    ordering = ['-created_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'requester', 'approver', 'approval_type', 'status', 'created_at']
    list_filter = ['approval_type', 'status', 'created_at']
    search_fields = ['title', 'requester__username', 'approver__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(ApprovalResponse)
class ApprovalResponseAdmin(admin.ModelAdmin):
    list_display = ['approval_request', 'responder', 'response', 'created_at']
    list_filter = ['response', 'created_at']
    search_fields = ['approval_request__title', 'responder__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


# Licensing Models Admin - Now handled by fbs_license_manager app


# MSME Models Admin
@admin.register(MSMESetupWizard)
class MSMESetupWizardAdmin(admin.ModelAdmin):
    list_display = ['solution_name', 'business_type', 'status', 'current_step', 'progress', 'started_at']
    list_filter = ['business_type', 'status', 'started_at']
    search_fields = ['solution_name', 'business_type']
    readonly_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']


@admin.register(MSMEKPI)
class MSMEKPIAdmin(admin.ModelAdmin):
    list_display = ['kpi_name', 'kpi_type', 'current_value', 'target_value', 'unit', 'period', 'last_updated']
    list_filter = ['kpi_type', 'period', 'last_updated']
    search_fields = ['kpi_name', 'solution_name']
    ordering = ['kpi_type', 'kpi_name']


@admin.register(MSMECompliance)
class MSMEComplianceAdmin(admin.ModelAdmin):
    list_display = ['solution_name', 'compliance_type', 'status', 'due_date', 'actual_completion_date', 'last_checked']
    list_filter = ['compliance_type', 'status', 'due_date', 'last_checked']
    search_fields = ['solution_name', 'compliance_type']
    ordering = ['due_date', 'status']


@admin.register(MSMEMarketing)
class MSMEMarketingAdmin(admin.ModelAdmin):
    list_display = ['campaign_name', 'campaign_type', 'start_date', 'end_date', 'status', 'budget', 'created_at']
    list_filter = ['campaign_type', 'status', 'start_date', 'created_at']
    search_fields = ['campaign_name', 'solution_name']
    ordering = ['-start_date', 'status']


@admin.register(MSMETemplate)
class MSMETemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'business_type', 'description', 'is_active', 'created_at']
    list_filter = ['business_type', 'is_active', 'created_at']
    search_fields = ['name', 'business_type', 'description']
    ordering = ['business_type', 'name']


@admin.register(MSMEAnalytics)
class MSMEAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['solution_name', 'metric_name', 'metric_value', 'metric_type', 'period', 'date', 'created_at']
    list_filter = ['metric_type', 'period', 'date', 'created_at']
    search_fields = ['solution_name', 'metric_name']
    ordering = ['-date', 'metric_type']


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    list_display = ['field_name', 'field_type', 'model_name', 'record_id', 'is_active', 'created_at']
    list_filter = ['field_type', 'model_name', 'is_active', 'created_at']
    search_fields = ['field_name', 'model_name', 'solution_name']
    ordering = ['model_name', 'field_name']


# Discovery Models Admin
@admin.register(OdooModel)
class OdooModelAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'database_name', 'module_name', 'model_type', 'is_active', 'discovered_at']
    list_filter = ['model_type', 'is_active', 'module_name', 'discovered_at']
    search_fields = ['model_name', 'database_name', 'module_name']
    ordering = ['module_name', 'model_name']


@admin.register(OdooField)
class OdooFieldAdmin(admin.ModelAdmin):
    list_display = ['field_name', 'odoo_model', 'field_type', 'required', 'readonly', 'computed']
    list_filter = ['field_type', 'required', 'readonly', 'computed']
    search_fields = ['field_name', 'odoo_model__model_name']
    ordering = ['odoo_model__model_name', 'field_name']


@admin.register(OdooModule)
class OdooModuleAdmin(admin.ModelAdmin):
    list_display = ['module_name', 'database_name', 'version', 'category', 'is_installed', 'is_active']
    list_filter = ['category', 'is_installed', 'is_active', 'discovered_at']
    search_fields = ['module_name', 'database_name', 'category']
    ordering = ['category', 'module_name']


# Workflow Models Admin
@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow_type', 'version', 'is_active', 'is_template', 'created_by', 'created_at']
    list_filter = ['workflow_type', 'is_active', 'is_template', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['workflow_type', 'name']


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ['workflow_definition', 'business_id', 'current_step', 'status', 'started_at', 'current_user']
    list_filter = ['status', 'started_at', 'workflow_definition__workflow_type']
    search_fields = ['business_id', 'workflow_definition__name']
    ordering = ['-started_at']


@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow_definition', 'step_type', 'order', 'is_required', 'assigned_role']
    list_filter = ['step_type', 'is_required', 'workflow_definition__workflow_type']
    search_fields = ['name', 'workflow_definition__name']
    ordering = ['workflow_definition__name', 'order']


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    list_display = ['workflow_definition', 'from_step', 'to_step', 'transition_type', 'is_default']
    list_filter = ['transition_type', 'is_default', 'workflow_definition__workflow_type']
    search_fields = ['workflow_definition__name', 'from_step__name', 'to_step__name']
    ordering = ['workflow_definition__name', 'from_step__order']


# Business Intelligence Models Admin
@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['name', 'dashboard_type', 'is_public', 'is_active', 'refresh_interval', 'created_by']
    list_filter = ['dashboard_type', 'is_public', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['dashboard_type', 'name']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'output_format', 'is_scheduled', 'is_active', 'created_by']
    list_filter = ['report_type', 'output_format', 'is_scheduled', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['report_type', 'name']


@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ['name', 'kpi_type', 'target_value', 'warning_threshold', 'critical_threshold', 'frequency', 'is_active']
    list_filter = ['kpi_type', 'frequency', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['kpi_type', 'name']


@admin.register(Chart)
class ChartAdmin(admin.ModelAdmin):
    list_display = ['name', 'chart_type', 'data_source', 'is_active', 'created_by']
    list_filter = ['chart_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['chart_type', 'name']


# Compliance Models Admin
@admin.register(ComplianceRule)
class ComplianceRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'compliance_type', 'check_frequency', 'active', 'created_at']
    list_filter = ['compliance_type', 'check_frequency', 'active', 'created_at']
    search_fields = ['name', 'description', 'solution_name']
    ordering = ['compliance_type', 'name']


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ['action', 'record_type', 'record_id', 'user_id', 'timestamp', 'solution_name']
    list_filter = ['action', 'record_type', 'timestamp', 'solution_name']
    search_fields = ['action', 'record_id', 'user_id']
    ordering = ['-timestamp']


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'frequency', 'next_run', 'active', 'solution_name']
    list_filter = ['report_type', 'frequency', 'active', 'created_at']
    search_fields = ['name', 'solution_name']
    ordering = ['frequency', 'next_run']


@admin.register(RecurringTransaction)
class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ['name', 'transaction_type', 'amount', 'frequency', 'start_date', 'active', 'solution_name']
    list_filter = ['transaction_type', 'frequency', 'active', 'start_date']
    search_fields = ['name', 'solution_name']
    ordering = ['frequency', 'start_date']


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'action', 'timestamp', 'ip_address', 'solution_name']
    list_filter = ['action', 'timestamp', 'solution_name']
    search_fields = ['user_id', 'action']
    ordering = ['-timestamp']


# Accounting Models Admin
@admin.register(CashEntry)
class CashEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_type', 'amount', 'category', 'entry_date', 'payment_method', 'business_id', 'created_by']
    list_filter = ['entry_type', 'category', 'payment_method', 'entry_date', 'created_at']
    search_fields = ['description', 'business_id', 'vendor_customer']
    ordering = ['-entry_date', '-created_at']


@admin.register(IncomeExpense)
class IncomeExpenseAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'amount', 'category', 'transaction_date', 'payment_status', 'business_id']
    list_filter = ['transaction_type', 'category', 'payment_status', 'transaction_date', 'created_at']
    search_fields = ['description', 'business_id', 'vendor_customer', 'invoice_number']
    ordering = ['-transaction_date', '-created_at']


@admin.register(BasicLedger)
class BasicLedgerAdmin(admin.ModelAdmin):
    list_display = ['account', 'account_type', 'debit_amount', 'credit_amount', 'balance', 'entry_date', 'business_id']
    list_filter = ['account_type', 'entry_date']
    search_fields = ['account', 'business_id', 'description']
    ordering = ['account', 'entry_date']


@admin.register(TaxCalculation)
class TaxCalculationAdmin(admin.ModelAdmin):
    list_display = ['tax_type', 'tax_period_start', 'tax_period_end', 'net_tax_amount', 'payment_status', 'due_date', 'business_id']
    list_filter = ['tax_type', 'payment_status', 'tax_period_start', 'tax_period_end']
    search_fields = ['business_id', 'filing_reference']
    ordering = ['-tax_period_end', 'tax_type']


# Admin site configuration
admin.site.site_header = "FBS App Administration"
admin.site.site_title = "FBS App Admin"
admin.site.index_title = "Welcome to FBS App Administration"
