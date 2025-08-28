"""
FBS App Signals

Django signals for the FBS app.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
import logging

logger = logging.getLogger('fbs_app')


# Import models
from .models.core import (
    OdooDatabase, TokenMapping, RequestLog, BusinessRule,
    CacheEntry, Handshake, Notification, ApprovalRequest, ApprovalResponse
)
from .models.msme import (
    MSMESetupWizard, MSMEKPI, MSMECompliance, MSMEMarketing,
    MSMETemplate, MSMEAnalytics
)
from .models.core import CustomField
from .models.discovery import OdooModel, OdooField, OdooModule, DiscoverySession
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


@receiver(post_save, sender=OdooDatabase)
def odoo_database_post_save(sender, instance, created, **kwargs):
    """Handle post-save for OdooDatabase"""
    if created:
        logger.info(f"New Odoo database created: {instance.name}")
    else:
        logger.info(f"Odoo database updated: {instance.name}")


@receiver(post_save, sender=TokenMapping)
def token_mapping_post_save(sender, instance, created, **kwargs):
    """Handle post-save for TokenMapping"""
    if created:
        logger.info(f"New token mapping created for user: {instance.user}")
    else:
        logger.info(f"Token mapping updated for user: {instance.user}")


@receiver(post_save, sender=RequestLog)
def request_log_post_save(sender, instance, created, **kwargs):
    """Handle post-save for RequestLog"""
    if created:
        logger.debug(f"Request logged: {instance.method} {instance.path}")


@receiver(post_save, sender=BusinessRule)
def business_rule_post_save(sender, instance, created, **kwargs):
    """Handle post-save for BusinessRule"""
    if created:
        logger.info(f"New business rule created: {instance.name}")
    else:
        logger.info(f"Business rule updated: {instance.name}")


@receiver(post_save, sender=CacheEntry)
def cache_entry_post_save(sender, instance, created, **kwargs):
    """Handle post-save for CacheEntry"""
    if created:
        logger.debug(f"New cache entry created: {instance.key}")
    else:
        logger.debug(f"Cache entry updated: {instance.key}")


@receiver(post_save, sender=Handshake)
def handshake_post_save(sender, instance, created, **kwargs):
    """Handle post-save for Handshake"""
    if created:
        logger.info(f"New handshake created for solution: {instance.solution_name}")
    else:
        logger.info(f"Handshake updated for solution: {instance.solution_name}")


@receiver(post_save, sender=Notification)
def notification_post_save(sender, instance, created, **kwargs):
    """Handle post-save for Notification"""
    if created:
        logger.info(f"New notification created for user: {instance.user}")
    else:
        logger.debug(f"Notification updated for user: {instance.user}")


@receiver(post_save, sender=ApprovalRequest)
def approval_request_post_save(sender, instance, created, **kwargs):
    """Handle post-save for ApprovalRequest"""
    if created:
        logger.info(f"New approval request created: {instance.approval_type}")
    else:
        logger.info(f"Approval request updated: {instance.approval_type}")


@receiver(post_save, sender=MSMESetupWizard)
def msme_setup_wizard_post_save(sender, instance, created, **kwargs):
    """Handle post-save for MSMESetupWizard"""
    if created:
        logger.info(f"New MSME setup wizard created for solution: {instance.solution_name}")
    else:
        logger.info(f"MSME setup wizard updated for solution: {instance.solution_name}")


@receiver(post_save, sender=MSMEKPI)
def msme_kpi_post_save(sender, instance, created, **kwargs):
    """Handle post-save for MSMEKPI"""
    if created:
        logger.info(f"New MSME KPI created: {instance.kpi_name}")
    else:
        logger.debug(f"MSME KPI updated: {instance.kpi_name}")


@receiver(post_save, sender=WorkflowDefinition)
def workflow_definition_post_save(sender, instance, created, **kwargs):
    """Handle post-save for WorkflowDefinition"""
    if created:
        logger.info(f"New workflow definition created: {instance.name}")
    else:
        logger.info(f"Workflow definition updated: {instance.name}")


@receiver(post_save, sender=WorkflowInstance)
def workflow_instance_post_save(sender, instance, created, **kwargs):
    """Handle post-save for WorkflowInstance"""
    if created:
        logger.info(f"New workflow instance created: {instance.workflow_definition.name}")
    else:
        logger.debug(f"Workflow instance updated: {instance.workflow_definition.name}")


@receiver(post_save, sender=Dashboard)
def dashboard_post_save(sender, instance, created, **kwargs):
    """Handle post-save for Dashboard"""
    if created:
        logger.info(f"New dashboard created: {instance.name}")
    else:
        logger.info(f"Dashboard updated: {instance.name}")


@receiver(post_save, sender=Report)
def report_post_save(sender, instance, created, **kwargs):
    """Handle post-save for Report"""
    if created:
        logger.info(f"New report created: {instance.name}")
    else:
        logger.info(f"Report updated: {instance.name}")


@receiver(post_save, sender=ComplianceRule)
def compliance_rule_post_save(sender, instance, created, **kwargs):
    """Handle post-save for ComplianceRule"""
    if created:
        logger.info(f"New compliance rule created: {instance.name}")
    else:
        logger.info(f"Compliance rule updated: {instance.name}")


@receiver(post_save, sender=AuditTrail)
def audit_trail_post_save(sender, instance, created, **kwargs):
    """Handle post-save for AuditTrail"""
    if created:
        logger.info(f"New audit trail entry created: {instance.action}")
    else:
        logger.debug(f"Audit trail entry updated: {instance.action}")


@receiver(post_save, sender=CashEntry)
def cash_entry_post_save(sender, instance, created, **kwargs):
    """Handle post-save for CashEntry"""
    if created:
        logger.info(f"New cash entry created: {instance.entry_type} - {instance.amount}")
    else:
        logger.debug(f"Cash entry updated: {instance.entry_type} - {instance.amount}")


@receiver(post_save, sender=IncomeExpense)
def income_expense_post_save(sender, instance, created, **kwargs):
    """Handle post-save for IncomeExpense"""
    if created:
        logger.info(f"New income/expense record created: {instance.transaction_type} - {instance.amount}")
    else:
        logger.debug(f"Income/expense record updated: {instance.transaction_type} - {instance.amount}")


@receiver(post_save, sender=BasicLedger)
def basic_ledger_post_save(sender, instance, created, **kwargs):
    """Handle post-save for BasicLedger"""
    if created:
        logger.info(f"New ledger entry created: {instance.account} - {instance.description}")
    else:
        logger.debug(f"Ledger entry updated: {instance.account} - {instance.description}")


@receiver(post_save, sender=TaxCalculation)
def tax_calculation_post_save(sender, instance, created, **kwargs):
    """Handle post-save for TaxCalculation"""
    if created:
        logger.info(f"New tax calculation created: {instance.tax_type} - {instance.net_tax_amount}")
    else:
        logger.debug(f"Tax calculation updated: {instance.tax_type} - {instance.net_tax_amount}")


# Cleanup signals with safety checks
@receiver(post_delete, sender=CacheEntry)
def cache_entry_post_delete(sender, instance, **kwargs):
    """Handle post-delete for CacheEntry"""
    try:
        logger.debug(f"Cache entry deleted: {instance.key}")
    except Exception as e:
        logger.warning(f"Error in cache_entry_post_delete signal: {e}")
        # Don't let signal failures break the main operation


@receiver(post_delete, sender=RequestLog)
def request_log_post_delete(sender, instance, **kwargs):
    """Handle post-delete for RequestLog"""
    try:
        logger.debug(f"Request log deleted: {instance.method} {instance.path}")
    except Exception as e:
        logger.warning(f"Error in request_log_post_delete signal: {e}")
        # Don't let signal failures break the main operation


# Add safety wrapper for all FBS signals
def safe_signal_execution(func):
    """Decorator to safely execute FBS signals without breaking host operations"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"FBS signal {func.__name__} failed: {e}")
            # Log the error but don't break the main operation
            return None
    return wrapper


# Apply safety wrapper to all post_save signals
@receiver(post_save, sender=OdooDatabase)
@safe_signal_execution
def odoo_database_post_save(sender, instance, created, **kwargs):
    """Handle post-save for OdooDatabase"""
    if created:
        logger.info(f"New Odoo database created: {instance.name}")
    else:
        logger.info(f"Odoo database updated: {instance.name}")


@receiver(post_save, sender=TokenMapping)
@safe_signal_execution
def token_mapping_post_save(sender, instance, created, **kwargs):
    """Handle post-save for TokenMapping"""
    if created:
        logger.info(f"New token mapping created for user: {instance.user}")
    else:
        logger.info(f"Token mapping updated for user: {instance.user}")


@receiver(post_save, sender=RequestLog)
@safe_signal_execution
def request_log_post_save(sender, instance, created, **kwargs):
    """Handle post-save for RequestLog"""
    if created:
        logger.debug(f"Request logged: {instance.method} {instance.path}")


@receiver(post_save, sender=BusinessRule)
@safe_signal_execution
def business_rule_post_save(sender, instance, created, **kwargs):
    """Handle post-save for BusinessRule"""
    if created:
        logger.info(f"New business rule created: {instance.name}")
    else:
        logger.info(f"Business rule updated: {instance.name}")


@receiver(post_save, sender=CacheEntry)
@safe_signal_execution
def cache_entry_post_save(sender, instance, created, **kwargs):
    """Handle post-save for CacheEntry"""
    if created:
        logger.debug(f"New cache entry created: {instance.key}")
    else:
        logger.debug(f"Cache entry updated: {instance.key}")


@receiver(post_save, sender=Handshake)
@safe_signal_execution
def handshake_post_save(sender, instance, created, **kwargs):
    """Handle post-save for Handshake"""
    if created:
        logger.info(f"New handshake created for solution: {instance.solution_name}")
    else:
        logger.info(f"Handshake updated for solution: {instance.solution_name}")


@receiver(post_save, sender=Notification)
@safe_signal_execution
def notification_post_save(sender, instance, created, **kwargs):
    """Handle post-save for Notification"""
    if created:
        logger.info(f"New notification created for user: {instance.user}")
    else:
        logger.debug(f"Notification updated for user: {instance.user}")


@receiver(post_save, sender=ApprovalRequest)
@safe_signal_execution
def approval_request_post_save(sender, instance, created, **kwargs):
    """Handle post-save for ApprovalRequest"""
    if created:
        logger.info(f"New approval request created: {instance.title}")
    else:
        logger.info(f"Approval request updated: {instance.title}")


@receiver(post_save, sender=ApprovalResponse)
@safe_signal_execution
def approval_response_post_save(sender, instance, created, **kwargs):
    """Handle post-save for ApprovalResponse"""
    if created:
        logger.info(f"New approval response created for: {instance.approval_request.title}")
    else:
        logger.debug(f"Approval response updated for: {instance.approval_request.title}")


@receiver(post_save, sender=CustomField)
@safe_signal_execution
def custom_field_post_save(sender, instance, created, **kwargs):
    """Handle post-save for CustomField"""
    if created:
        logger.info(f"New custom field created: {instance.field_name}")
    else:
        logger.debug(f"Custom field updated: {instance.field_name}")


@receiver(post_save, sender=OdooModel)
@safe_signal_execution
def odoo_model_post_save(sender, instance, created, **kwargs):
    """Handle post-save for OdooModel"""
    if created:
        logger.info(f"New Odoo model discovered: {instance.model_name}")
    else:
        logger.debug(f"Odoo model updated: {instance.model_name}")


@receiver(post_save, sender=OdooField)
@safe_signal_execution
def odoo_field_post_save(sender, instance, created, **kwargs):
    """Handle post-save for OdooField"""
    if created:
        logger.info(f"New Odoo field discovered: {instance.field_name}")
    else:
        logger.debug(f"Odoo field updated: {instance.field_name}")


@receiver(post_save, sender=OdooModule)
@safe_signal_execution
def odoo_module_post_save(sender, instance, created, **kwargs):
    """Handle post-save for OdooModule"""
    if created:
        logger.info(f"New Odoo module discovered: {instance.module_name}")
    else:
        logger.debug(f"Odoo module updated: {instance.module_name}")


@receiver(post_save, sender=DiscoverySession)
@safe_signal_execution
def discovery_session_post_save(sender, instance, created, **kwargs):
    """Handle post-save for DiscoverySession"""
    if created:
        logger.info(f"New discovery session started: {instance.session_id}")
    else:
        logger.debug(f"Discovery session updated: {instance.session_id}")


@receiver(post_save, sender=WorkflowDefinition)
@safe_signal_execution
def workflow_definition_post_save(sender, instance, created, **kwargs):
    """Handle post-save for WorkflowDefinition"""
    if created:
        logger.info(f"New workflow definition created: {instance.name}")
    else:
        logger.info(f"Workflow definition updated: {instance.name}")


@receiver(post_save, sender=WorkflowInstance)
@safe_signal_execution
def workflow_instance_post_save(sender, instance, created, **kwargs):
    """Handle post-save for WorkflowInstance"""
    if created:
        logger.info(f"New workflow instance created: {instance.workflow.name}")
    else:
        logger.debug(f"Workflow instance updated: {instance.workflow.name}")


@receiver(post_save, sender=WorkflowStep)
@safe_signal_execution
def workflow_step_post_save(sender, instance, created, **kwargs):
    """Handle post-save for WorkflowStep"""
    if created:
        logger.info(f"New workflow step created: {instance.step_name}")
    else:
        logger.debug(f"Workflow step updated: {instance.step_name}")


@receiver(post_save, sender=WorkflowTransition)
@safe_signal_execution
def workflow_transition_post_save(sender, instance, created, **kwargs):
    """Handle post-save for WorkflowTransition"""
    if created:
        logger.info(f"New workflow transition created: {instance.name}")
    else:
        logger.debug(f"Workflow transition updated: {instance.name}")


@receiver(post_save, sender=Dashboard)
@safe_signal_execution
def dashboard_post_save(sender, instance, created, **kwargs):
    """Handle post-save for Dashboard"""
    if created:
        logger.info(f"New dashboard created: {instance.name}")
    else:
        logger.info(f"Dashboard updated: {instance.name}")


@receiver(post_save, sender=Report)
@safe_signal_execution
def report_post_save(sender, instance, created, **kwargs):
    """Handle post-save for Report"""
    if created:
        logger.info(f"New report created: {instance.name}")
    else:
        logger.info(f"Report updated: {instance.name}")


@receiver(post_save, sender=KPI)
@safe_signal_execution
def kpi_post_save(sender, instance, created, **kwargs):
    """Handle post-save for KPI"""
    if created:
        logger.info(f"New KPI created: {instance.name}")
    else:
        logger.info(f"KPI updated: {instance.name}")


@receiver(post_save, sender=Chart)
@safe_signal_execution
def chart_post_save(sender, instance, created, **kwargs):
    """Handle post-save for Chart"""
    if created:
        logger.info(f"New chart created: {instance.name}")
    else:
        logger.info(f"Chart updated: {instance.name}")


@receiver(post_save, sender=ComplianceRule)
@safe_signal_execution
def compliance_rule_post_save(sender, instance, created, **kwargs):
    """Handle post-save for ComplianceRule"""
    if created:
        logger.info(f"New compliance rule created: {instance.name}")
    else:
        logger.info(f"Compliance rule updated: {instance.name}")


@receiver(post_save, sender=AuditTrail)
@safe_signal_execution
def audit_trail_post_save(sender, instance, created, **kwargs):
    """Handle post-save for AuditTrail"""
    if created:
        logger.info(f"New audit trail entry created: {instance.action}")
    else:
        logger.debug(f"Audit trail entry updated: {instance.action}")


@receiver(post_save, sender=ReportSchedule)
@safe_signal_execution
def report_schedule_post_save(sender, instance, created, **kwargs):
    """Handle post-save for ReportSchedule"""
    if created:
        logger.info(f"New report schedule created: {instance.name}")
    else:
        logger.info(f"Report schedule updated: {instance.name}")


@receiver(post_save, sender=RecurringTransaction)
@safe_signal_execution
def recurring_transaction_post_save(sender, instance, created, **kwargs):
    """Handle post-save for RecurringTransaction"""
    if created:
        logger.info(f"New recurring transaction created: {instance.description}")
    else:
        logger.debug(f"Recurring transaction updated: {instance.description}")


@receiver(post_save, sender=UserActivityLog)
@safe_signal_execution
def user_activity_log_post_save(sender, instance, created, **kwargs):
    """Handle post-save for UserActivityLog"""
    if created:
        logger.info(f"New user activity logged: {instance.action}")
    else:
        logger.debug(f"User activity log updated: {instance.action}")


@receiver(post_save, sender=CashEntry)
@safe_signal_execution
def cash_entry_post_save(sender, instance, created, **kwargs):
    """Handle post-save for CashEntry"""
    if created:
        logger.info(f"New cash entry created: {instance.entry_type} - {instance.amount}")
    else:
        logger.debug(f"Cash entry updated: {instance.entry_type} - {instance.amount}")


@receiver(post_save, sender=IncomeExpense)
@safe_signal_execution
def income_expense_post_save(sender, instance, created, **kwargs):
    """Handle post-save for IncomeExpense"""
    if created:
        logger.info(f"New income/expense record created: {instance.transaction_type} - {instance.amount}")
    else:
        logger.debug(f"Income/expense record updated: {instance.transaction_type} - {instance.amount}")


@receiver(post_save, sender=BasicLedger)
@safe_signal_execution
def basic_ledger_post_save(sender, instance, created, **kwargs):
    """Handle post-save for BasicLedger"""
    if created:
        logger.info(f"New ledger entry created: {instance.account} - {instance.description}")
    else:
        logger.debug(f"Ledger entry updated: {instance.account} - {instance.description}")


@receiver(post_save, sender=TaxCalculation)
@safe_signal_execution
def tax_calculation_post_save(sender, instance, created, **kwargs):
    """Handle post-save for TaxCalculation"""
    if created:
        logger.info(f"New tax calculation created: {instance.tax_type} - {instance.net_tax_amount}")
    else:
        logger.debug(f"Tax calculation updated: {instance.tax_type} - {instance.net_tax_amount}")


# Pre-save signals for validation with safety wrapper
@receiver(pre_save, sender=MSMEKPI)
@safe_signal_execution
def msme_kpi_pre_save(sender, instance, **kwargs):
    """Validate MSME KPI before saving"""
    if instance.target_value and instance.current_value:
        if instance.target_value < 0:
            logger.warning(f"KPI target value is negative: {instance.kpi_name}")


@receiver(pre_save, sender=CashEntry)
@safe_signal_execution
def cash_entry_pre_save(sender, instance, **kwargs):
    """Validate cash entry before saving"""
    if instance.amount < 0:
        logger.warning(f"Cash entry amount is negative: {instance.description}")


@receiver(pre_save, sender=IncomeExpense)
@safe_signal_execution
def income_expense_pre_save(sender, instance, **kwargs):
    """Validate income/expense before saving"""
    if instance.amount < 0:
        logger.warning(f"Income/expense amount is negative: {instance.description}")


# Pre-save signals for validation
@receiver(pre_save, sender=MSMEKPI)
def msme_kpi_pre_save(sender, instance, **kwargs):
    """Validate MSME KPI before saving"""
    if instance.target_value and instance.current_value:
        if instance.target_value < 0:
            logger.warning(f"KPI target value is negative: {instance.kpi_name}")


@receiver(pre_save, sender=CashEntry)
def cash_entry_pre_save(sender, instance, **kwargs):
    """Validate cash entry before saving"""
    if instance.amount < 0:
        logger.warning(f"Cash entry amount is negative: {instance.description}")


@receiver(pre_save, sender=IncomeExpense)
def income_expense_pre_save(sender, instance, **kwargs):
    """Validate income/expense before saving"""
    if instance.amount < 0:
        logger.warning(f"Income/expense amount is negative: {instance.description}")
