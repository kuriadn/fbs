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
    MSMETemplate, MSMEAnalytics, CustomField
)
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
        logger.debug(f"Request logged: {instance.method} {instance.endpoint}")


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
        logger.info(f"New handshake created for system: {instance.system_name}")
    else:
        logger.info(f"Handshake updated for system: {instance.system_name}")


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
        logger.info(f"New approval request created: {instance.request_type}")
    else:
        logger.info(f"Approval request updated: {instance.request_type}")


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
        logger.info(f"New workflow instance created: {instance.workflow.name}")
    else:
        logger.debug(f"Workflow instance updated: {instance.workflow.name}")


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


# Cleanup signals
@receiver(post_delete, sender=CacheEntry)
def cache_entry_post_delete(sender, instance, **kwargs):
    """Handle post-delete for CacheEntry"""
    logger.debug(f"Cache entry deleted: {instance.key}")


@receiver(post_delete, sender=RequestLog)
def request_log_post_delete(sender, instance, **kwargs):
    """Handle post-delete for RequestLog"""
    logger.debug(f"Request log deleted: {instance.method} {instance.endpoint}")


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
