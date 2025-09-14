"""
FBS v3 Models - Streamlined Business Intelligence

Consolidated from 60+ Django models to 15 focused models.
Preserves all critical business intelligence while eliminating complexity.
"""

import sqlalchemy as sa
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Float, Text, JSON, UUID, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
# Base is now imported from database module
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

from ..core.database import Base

# ============================================================================
# COMPLIANCE MODELS (MIGRATED FROM DJANGO)
# ============================================================================

class ComplianceRule(Base):
    """Compliance rules for business operations - migrated from Django"""

    __tablename__ = 'compliance_rules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_name = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    compliance_type = Column(String(20), nullable=False)  # tax, regulatory, audit, financial, operational
    requirements = Column(JSON, default=list, nullable=False)
    check_frequency = Column(String(20), default='monthly', nullable=False)  # daily, weekly, monthly, quarterly, yearly
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ComplianceRule(solution='{self.solution_name}', name='{self.name}')>"


class AuditTrail(Base):
    """Audit trail for business operations - migrated from Django"""

    __tablename__ = 'audit_trails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=False)
    user_id = Column(String(100), nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    model_metadata = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return f"<AuditTrail(action='{self.action}', resource='{self.resource_type}:{self.resource_id}')>"


class ReportSchedule(Base):
    """Scheduled reports for compliance - migrated from Django"""

    __tablename__ = 'report_schedules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_name = Column(String(100), nullable=False)
    report_type = Column(String(50), nullable=False)
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly
    next_run = Column(DateTime(timezone=True), nullable=False)
    last_run = Column(DateTime(timezone=True), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    parameters = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<ReportSchedule(type='{self.report_type}', frequency='{self.frequency}')>"


class RecurringTransaction(Base):
    """Recurring financial transactions - migrated from Django"""

    __tablename__ = 'recurring_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    solution_name = Column(String(100), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    transaction_type = Column(String(20), nullable=False)  # income, expense
    amount = Column(Float, nullable=False)
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    category = Column(String(100), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    next_due = Column(DateTime(timezone=True), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    model_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<RecurringTransaction(name='{self.name}', amount={self.amount})>"


class UserActivityLog(Base):
    """User activity logging for audit purposes - migrated from Django"""

    __tablename__ = 'user_activity_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), nullable=False)
    solution_name = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<UserActivityLog(user='{self.user_id}', action='{self.action}')>"


# ============================================================================
# AUTHENTICATION MODELS (MIGRATED FROM DJANGO)
# ============================================================================

class Handshake(Base):
    """Handshake authentication tokens for secure API access"""

    __tablename__ = 'handshakes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    handshake_id = Column(String(100), nullable=False, unique=True)
    secret_key = Column(String(100), nullable=False)
    solution_name = Column(String(100), nullable=False)
    status = Column(String(20), default='active', nullable=False)  # active, used, expired, revoked
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=sa.text("now()"), nullable=False)
    used_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    handshake_metadata = Column(JSON, default=dict, nullable=False)

    def __repr__(self):
        return f"<Handshake(id='{self.handshake_id}', status='{self.status}')>"


# ============================================================================
# ACCOUNTING MODELS (MIGRATED FROM DJANGO)
# ============================================================================

class CashEntry(Base):
    """Cash basis accounting entries - migrated from Django"""

    __tablename__ = 'cash_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(100), nullable=False)  # Reference to business/solution
    entry_date = Column(DateTime(timezone=True), nullable=False)
    entry_type = Column(String(20), nullable=False)  # income, expense, transfer, adjustment
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    payment_method = Column(String(50), nullable=False)  # cash, bank_transfer, check, credit_card, debit_card, mobile_payment, other
    reference_number = Column(String(100), nullable=True)
    vendor_customer = Column(String(200), nullable=True)
    tax_amount = Column(Float, default=0.0, nullable=False)
    tax_rate = Column(Float, default=0.0, nullable=False)
    notes = Column(Text, nullable=True)
    attachments = Column(JSON, default=list, nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<CashEntry(type='{self.entry_type}', amount={self.amount})>"


class IncomeExpense(Base):
    """Income and expense tracking - migrated from Django"""

    __tablename__ = 'income_expenses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(100), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # income, expense
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), nullable=True)
    payment_method = Column(String(50), nullable=True)
    reference_number = Column(String(100), nullable=True)
    tax_category = Column(String(50), nullable=True)
    tax_amount = Column(Float, default=0.0, nullable=False)
    recurring = Column(Boolean, default=False, nullable=False)
    recurring_frequency = Column(String(20), nullable=True)  # monthly, quarterly, yearly
    vendor_customer = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    attachments = Column(JSON, default=list, nullable=False)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<IncomeExpense(type='{self.transaction_type}', amount={self.amount})>"


class BasicLedger(Base):
    """Basic ledger for accounting - migrated from Django"""

    __tablename__ = 'basic_ledgers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(100), nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(50), nullable=False)  # asset, liability, equity, income, expense
    account_code = Column(String(20), nullable=True)
    parent_account_id = Column(Integer, ForeignKey('basic_ledgers.id'), nullable=True)
    balance = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    parent_account = relationship("BasicLedger", remote_side=[id], backref="sub_accounts")

    def __repr__(self):
        return f"<BasicLedger(name='{self.account_name}', balance={self.balance})>"


class TaxCalculation(Base):
    """Tax calculations and records - migrated from Django"""

    __tablename__ = 'tax_calculations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    business_id = Column(String(100), nullable=False)
    tax_period = Column(String(20), nullable=False)  # monthly, quarterly, yearly
    tax_year = Column(Integer, nullable=False)
    tax_type = Column(String(50), nullable=False)  # vat, income_tax, payroll_tax, withholding_tax
    taxable_amount = Column(Float, nullable=False)
    tax_rate = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0, nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default='pending', nullable=False)  # pending, paid, overdue
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<TaxCalculation(type='{self.tax_type}', amount={self.tax_amount})>"

# ============================================================================
# MODULE GENERATION MODELS
# ============================================================================

class ModuleTemplate(Base):
    """Template for module generation"""
    __tablename__ = "module_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    category = Column(String(50))
    template_data = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=sa.text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=sa.text("now()"), onupdate=sa.text("now()"))

    # Relationships
    generated_modules = relationship("GeneratedModule", back_populates="template")


class GeneratedModule(Base):
    """Generated module metadata"""
    __tablename__ = "generated_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    module_name = Column(String(100), nullable=False)
    tenant_id = Column(String(50), nullable=False)
    user_id = Column(String(50), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("module_templates.id"), nullable=True)

    # Module metadata
    version = Column(String(20), default="1.0.0")
    category = Column(String(50))
    description = Column(Text)

    # File storage
    dms_reference = Column(String(255))
    zip_size = Column(Integer)
    files_count = Column(Integer)

    # Generation details
    generation_time = Column(DateTime(timezone=True), server_default=sa.text("now()"))
    spec_snapshot = Column(JSON)  # Store the original spec for reference

    # Status
    is_installed = Column(Boolean, default=False)
    installation_time = Column(DateTime(timezone=True), nullable=True)
    odoo_module_id = Column(Integer, nullable=True)

    # Relationships
    template = relationship("ModuleTemplate", back_populates="generated_modules")
    generation_history = relationship("ModuleGenerationHistory", back_populates="generated_module")


class ModuleGenerationHistory(Base):
    """Audit log for module generation activities"""
    __tablename__ = "module_generation_history"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()"))
    generated_module_id = Column(UUID(as_uuid=True), ForeignKey("generated_modules.id"), nullable=True)

    module_name = Column(String(100), nullable=False)
    user_id = Column(String(50), nullable=False)
    tenant_id = Column(String(50), nullable=False)

    # Activity details
    activity_type = Column(String(50), nullable=False)  # 'generate', 'install', 'download', etc.
    spec_summary = Column(Text)
    dms_reference = Column(String(255))

    # Timing
    generation_time = Column(DateTime(timezone=True), server_default=sa.text("now()"))
    processing_time_ms = Column(Integer, nullable=True)

    # Results
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Metadata
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Relationships
    generated_module = relationship("GeneratedModule", back_populates="generation_history")


# ============================================================================
# ENUMS & CONSTANTS
# ============================================================================

class BusinessType(str, Enum):
    RETAIL = "retail"
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    RESTAURANT = "restaurant"
    CONSULTING = "consulting"
    ECOMMERCE = "ecommerce"
    OTHER = "other"

class BusinessSize(str, Enum):
    MICRO = "micro"      # 1-10 employees
    SMALL = "small"      # 11-50 employees
    MEDIUM = "medium"    # 51-250 employees

class MetricType(str, Enum):
    KPI = "kpi"
    COMPLIANCE = "compliance"
    MARKETING = "marketing"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"

class WorkflowType(str, Enum):
    APPROVAL = "approval"
    ONBOARDING = "onboarding"
    COMPLIANCE = "compliance"
    ORDER_PROCESSING = "order_processing"

class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# ============================================================================
# CORE MODELS
# ============================================================================

class BusinessEntity(Base):
    """Unified business entity - replaces 6+ MSME models"""
    __tablename__ = "business_entities"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # retail, manufacturing, etc.
    industry = Column(String(100))
    size = Column(String(20), default="micro")

    # Flexible configuration storage
    configuration = Column(JSON, default=dict)  # Business-specific settings
    model_metadata = Column(JSON, default=dict)       # Additional properties

    # Status and timestamps
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class User(Base):
    """Simplified user model"""
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, manager, user

    # Simple permission system
    permissions = Column(JSON, default=dict)

    # Auth fields
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AuthToken(Base):
    """Authentication tokens"""
    __tablename__ = "auth_tokens"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

# ============================================================================
# BUSINESS INTELLIGENCE MODELS
# ============================================================================

class BusinessMetric(Base):
    """Unified metrics - replaces MSMEKPI, MSMEAnalytics, MSMEMarketing"""
    __tablename__ = "business_metrics"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    # Metric classification
    metric_type = Column(String(50), nullable=False)  # kpi, compliance, marketing, operational
    name = Column(String(255), nullable=False)
    value = Column(DECIMAL(15, 2))
    target = Column(DECIMAL(15, 2))

    # Time dimensions
    period = Column(String(20), default="monthly")  # daily, weekly, monthly, quarterly
    date = Column(DateTime, nullable=False)

    # Flexible metadata
    model_metadata = Column(JSON, default=dict)  # thresholds, chart configs, etc.

    created_at = Column(DateTime, server_default=func.now())

class Dashboard(Base):
    """Flexible dashboard system"""
    __tablename__ = "dashboards"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    name = Column(String(255), nullable=False)
    type = Column(String(50), default="business")  # business, financial, compliance, custom

    # React component layout
    layout = Column(JSON, default=dict)
    widgets = Column(JSON, default=list)

    is_public = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    created_by = Column(UUID, ForeignKey('users.id'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Report(Base):
    """Unified reporting system"""
    __tablename__ = "reports"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # sales, financial, compliance

    # Report configuration
    configuration = Column(JSON, default=dict)  # filters, parameters, etc.
    schedule = Column(JSON)  # automated scheduling (optional)

    # Output settings
    output_format = Column(String(20), default="pdf")  # pdf, excel, json
    template = Column(Text)  # Custom template (optional)

    is_active = Column(Boolean, default=True)
    created_by = Column(UUID, ForeignKey('users.id'))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# ============================================================================
# WORKFLOW MODELS (Simplified)
# ============================================================================

class Workflow(Base):
    """Streamlined workflow - preserves core functionality"""
    __tablename__ = "workflows"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # approval, onboarding, compliance
    status = Column(String(20), default="draft")

    # Current state
    current_step = Column(Integer, default=0)

    # Workflow definition (JSON for flexibility)
    steps = Column(JSON, default=list)  # Simplified step definitions
    data = Column(JSON, default=dict)   # Workflow-specific data

    # Metadata
    created_by = Column(UUID, ForeignKey('users.id'))
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class WorkflowStep(Base):
    """Workflow step execution"""
    __tablename__ = "workflow_steps"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    workflow_id = Column(UUID, ForeignKey('workflows.id'), nullable=False)

    step_number = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # task, approval, notification

    # Assignment
    assignee = Column(UUID, ForeignKey('users.id'))

    # Status
    status = Column(String(20), default="pending")
    completed_at = Column(DateTime)

    # Step data
    data = Column(JSON, default=dict)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# ============================================================================
# INTEGRATION MODELS
# ============================================================================

class OdooConnection(Base):
    """Odoo database connections"""
    __tablename__ = "odoo_connections"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    name = Column(String(100), nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=8069)
    protocol = Column(String(10), default="http")

    username = Column(String(100), nullable=False)
    password = Column(String(255), nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class BusinessTemplate(Base):
    """Business templates - replaces MSMETemplate"""
    __tablename__ = "business_templates"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())

    name = Column(String(255), nullable=False)
    business_type = Column(String(50), nullable=False)
    description = Column(Text)

    # Template configuration
    configuration = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())

# ============================================================================
# ODOO DISCOVERY MODELS (CRITICAL - PRESERVED)
# ============================================================================

class OdooModel(Base):
    """Odoo model discovery - CRITICAL for auto-discovery"""
    __tablename__ = "odoo_models"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    # Odoo model information
    model_name = Column(String(100), nullable=False)
    technical_name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)

    # Module and categorization
    module_name = Column(String(100), nullable=False)
    model_type = Column(String(50), default='business')  # base, business, system, custom

    # Status and capabilities
    is_active = Column(Boolean, default=True)
    is_installed = Column(Boolean, default=True)
    capabilities = Column(JSON, default=list)  # Available operations
    constraints = Column(JSON, default=dict)  # Model constraints

    # Discovery metadata
    discovered_at = Column(DateTime, server_default=func.now())
    last_verified = Column(DateTime, server_default=func.now(), onupdate=func.now())

class OdooField(Base):
    """Odoo field discovery - CRITICAL for auto-discovery"""
    __tablename__ = "odoo_fields"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    odoo_model_id = Column(UUID, ForeignKey('odoo_models.id'), nullable=False)

    # Field information
    field_name = Column(String(100), nullable=False)
    technical_name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    field_type = Column(String(100), nullable=False)

    # Field properties
    required = Column(Boolean, default=False)
    readonly = Column(Boolean, default=False)
    computed = Column(Boolean, default=False)
    stored = Column(Boolean, default=True)

    # Field configuration
    default_value = Column(Text)
    help_text = Column(Text)
    selection_options = Column(JSON, default=list)  # For selection fields
    relation_model = Column(String(100))  # For relational fields
    field_constraints = Column(JSON, default=dict)

    discovered_at = Column(DateTime, server_default=func.now())

class OdooModule(Base):
    """Odoo module discovery - CRITICAL for auto-discovery"""
    __tablename__ = "odoo_modules"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    # Module information
    module_name = Column(String(100), nullable=False)
    technical_name = Column(String(100), nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text)

    # Module metadata
    version = Column(String(50), nullable=False)
    author = Column(String(200))
    website = Column(String(255))
    category = Column(String(100), nullable=False)

    # Installation status
    is_installed = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    auto_install = Column(Boolean, default=False)

    # Dependencies and data
    depends = Column(JSON, default=list)  # Module dependencies
    data_files = Column(JSON, default=list)  # Data files
    demo_data = Column(Boolean, default=False)
    application = Column(Boolean, default=False)

    # Discovery metadata
    discovered_at = Column(DateTime, server_default=func.now())
    last_verified = Column(DateTime, server_default=func.now(), onupdate=func.now())

class DiscoverySession(Base):
    """Discovery session tracking - CRITICAL for auto-discovery"""
    __tablename__ = "discovery_sessions"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    session_id = Column(String(100), unique=True, nullable=False)
    session_type = Column(String(50), nullable=False)  # 'full', 'incremental', 'targeted'
    status = Column(String(20), default='running')  # running, completed, failed, cancelled

    # Progress tracking
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    total_models = Column(Integer, default=0)
    total_fields = Column(Integer, default=0)
    total_modules = Column(Integer, default=0)

    # Results and errors
    errors = Column(JSON, default=list)
    configuration = Column(JSON, default=dict)

# ============================================================================
# MSME BUSINESS INTELLIGENCE MODELS (CRITICAL - PRESERVED)
# ============================================================================

class MSMESetupWizard(Base):
    """MSME setup wizard - CRITICAL for business intelligence"""
    __tablename__ = "msme_setup_wizards"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    # Setup status
    status = Column(String(20), default='not_started')  # not_started, in_progress, completed, paused
    current_step = Column(String(100))
    total_steps = Column(Integer, default=0)
    progress = Column(DECIMAL(5, 2), default=0.0)

    # Business configuration
    business_type = Column(String(100))
    configuration = Column(JSON, default=dict)

    # Timestamps
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)

class MSMEKPI(Base):
    """MSME KPIs - CRITICAL for business intelligence"""
    __tablename__ = "msme_kpis"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    # KPI definition
    kpi_name = Column(String(200), nullable=False)
    kpi_type = Column(String(20), nullable=False)  # financial, operational, customer, growth, compliance
    current_value = Column(DECIMAL(15, 2), nullable=False)
    target_value = Column(DECIMAL(15, 2))

    # Time and trend
    unit = Column(String(50))
    period = Column(String(20), default='monthly')
    trend = Column(String(20))  # 'up', 'down', 'stable'

    last_updated = Column(DateTime, server_default=func.now(), onupdate=func.now())

class MSMECompliance(Base):
    """MSME compliance tracking - CRITICAL for business intelligence"""
    __tablename__ = "msme_compliance"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    # Compliance details
    compliance_type = Column(String(20), nullable=False)  # tax, regulatory, financial, operational
    status = Column(String(20), default='pending')  # compliant, non_compliant, at_risk, pending
    due_date = Column(Date, nullable=False)
    actual_completion_date = Column(Date)

    # Requirements and tracking
    requirements = Column(JSON, default=list)
    documents = Column(JSON, default=list)
    notes = Column(Text)

    last_checked = Column(DateTime, server_default=func.now(), onupdate=func.now())

class MSMEMarketing(Base):
    """MSME marketing analytics - CRITICAL for business intelligence"""
    __tablename__ = "msme_marketing"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    # Campaign details
    campaign_name = Column(String(200), nullable=False)
    campaign_type = Column(String(20), nullable=False)  # digital, traditional, social_media, email, content
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    # Budget and metrics
    budget = Column(DECIMAL(15, 2))
    target_audience = Column(JSON, default=dict)
    metrics = Column(JSON, default=dict)
    status = Column(String(20), default='active')

    created_at = Column(DateTime, server_default=func.now())

class MSMEAnalytics(Base):
    """MSME analytics data - CRITICAL for business intelligence"""
    __tablename__ = "msme_analytics"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'), nullable=False)

    # Analytics data
    metric_name = Column(String(200), nullable=False)
    metric_value = Column(DECIMAL(15, 2), nullable=False)
    metric_type = Column(String(50), nullable=False)
    period = Column(String(20), default='monthly')
    date = Column(DateTime, nullable=False)

    # Additional context
    context = Column(JSON, default=dict)

    created_at = Column(DateTime, server_default=func.now())

# ============================================================================
# AUDIT & LOGGING (Minimal)
# ============================================================================

class AuditLog(Base):
    """Consolidated audit logging"""
    __tablename__ = "audit_logs"

    id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    business_id = Column(UUID, ForeignKey('business_entities.id'))
    user_id = Column(UUID, ForeignKey('users.id'))

    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    resource = Column(String(100), nullable=False)  # model/table name
    resource_id = Column(UUID)

    # Change details
    old_values = Column(JSON)
    new_values = Column(JSON)

    # Context
    ip_address = Column(String(45))
    user_agent = Column(Text)

    created_at = Column(DateTime, server_default=func.now())

# ============================================================================
# ODOO DISCOVERY Pydantic Models (CRITICAL)
# ============================================================================

class OdooModelBase(BaseModel):
    model_name: str
    technical_name: str
    display_name: str
    description: Optional[str] = None
    module_name: str
    model_type: str = "business"
    capabilities: List[str] = []
    constraints: Dict[str, Any] = {}

class OdooModelCreate(OdooModelBase):
    business_id: str

class OdooModelResponse(OdooModelBase):
    id: str
    business_id: str
    is_active: bool
    is_installed: bool
    discovered_at: datetime
    last_verified: datetime

class OdooFieldBase(BaseModel):
    field_name: str
    technical_name: str
    display_name: str
    field_type: str
    required: bool = False
    readonly: bool = False
    computed: bool = False
    stored: bool = True
    default_value: Optional[str] = None
    help_text: Optional[str] = None
    selection_options: List[Dict[str, Any]] = []
    relation_model: Optional[str] = None
    field_constraints: Dict[str, Any] = {}

class OdooFieldCreate(OdooFieldBase):
    odoo_model_id: str

class OdooFieldResponse(OdooFieldBase):
    id: str
    odoo_model_id: str
    discovered_at: datetime

class OdooModuleBase(BaseModel):
    module_name: str
    technical_name: str
    display_name: str
    description: Optional[str] = None
    version: str
    author: Optional[str] = None
    website: Optional[str] = None
    category: str
    is_installed: bool = True
    is_active: bool = True
    auto_install: bool = False
    depends: List[str] = []
    data_files: List[str] = []
    demo_data: bool = False
    application: bool = False

class OdooModuleCreate(OdooModuleBase):
    business_id: str

class OdooModuleResponse(OdooModuleBase):
    id: str
    business_id: str
    discovered_at: datetime
    last_verified: datetime

class DiscoverySessionBase(BaseModel):
    session_type: str  # 'full', 'incremental', 'targeted'
    configuration: Dict[str, Any] = {}

class DiscoverySessionCreate(DiscoverySessionBase):
    business_id: str
    session_id: str

class DiscoverySessionResponse(DiscoverySessionBase):
    id: str
    business_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    total_models: int
    total_fields: int
    total_modules: int
    errors: List[Dict[str, Any]]

# ============================================================================
# MSME BUSINESS INTELLIGENCE Pydantic Models (CRITICAL)
# ============================================================================

class MSMESetupWizardBase(BaseModel):
    business_type: Optional[str] = None
    configuration: Dict[str, Any] = {}

class MSMESetupWizardCreate(MSMESetupWizardBase):
    business_id: str

class MSMESetupWizardResponse(MSMESetupWizardBase):
    id: str
    business_id: str
    status: str
    current_step: Optional[str]
    total_steps: int
    progress: float
    started_at: datetime
    completed_at: Optional[datetime]

class MSMEKPIBase(BaseModel):
    kpi_name: str
    kpi_type: str
    current_value: float
    target_value: Optional[float] = None
    unit: Optional[str] = None
    period: str = "monthly"
    trend: Optional[str] = None

class MSMEKPICreate(MSMEKPIBase):
    business_id: str

class MSMEKPIResponse(MSMEKPIBase):
    id: str
    business_id: str
    last_updated: datetime

class MSMEComplianceBase(BaseModel):
    compliance_type: str
    status: str = "pending"
    due_date: date
    actual_completion_date: Optional[date] = None
    requirements: List[Dict[str, Any]] = []
    documents: List[Dict[str, Any]] = []
    notes: Optional[str] = None

class MSMEComplianceCreate(MSMEComplianceBase):
    business_id: str

class MSMEComplianceResponse(MSMEComplianceBase):
    id: str
    business_id: str
    last_checked: datetime

class MSMEMarketingBase(BaseModel):
    campaign_name: str
    campaign_type: str
    start_date: date
    end_date: Optional[date] = None
    budget: Optional[float] = None
    target_audience: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}
    status: str = "active"

class MSMEMarketingCreate(MSMEMarketingBase):
    business_id: str

class MSMEMarketingResponse(MSMEMarketingBase):
    id: str
    business_id: str
    created_at: datetime

class MSMEAnalyticsBase(BaseModel):
    metric_name: str
    metric_value: float
    metric_type: str
    period: str = "monthly"
    date: datetime
    context: Dict[str, Any] = {}

class MSMEAnalyticsCreate(MSMEAnalyticsBase):
    business_id: str

class MSMEAnalyticsResponse(MSMEAnalyticsBase):
    id: str
    business_id: str
    created_at: datetime

# ============================================================================
# Pydantic Models for API
# ============================================================================

class BusinessEntityBase(BaseModel):
    name: str
    type: BusinessType
    industry: Optional[str] = None
    size: BusinessSize = BusinessSize.MICRO
    configuration: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}

class BusinessEntityCreate(BusinessEntityBase):
    pass

class BusinessEntityResponse(BusinessEntityBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class BusinessMetricBase(BaseModel):
    metric_type: MetricType
    name: str
    value: float
    target: Optional[float] = None
    period: str = "monthly"
    date: date
    metadata: Dict[str, Any] = {}

class BusinessMetricCreate(BusinessMetricBase):
    business_id: str

class BusinessMetricResponse(BusinessMetricBase):
    id: str
    business_id: str
    created_at: datetime

class DashboardBase(BaseModel):
    name: str
    type: str = "business"
    layout: Dict[str, Any] = {}
    widgets: List[Dict[str, Any]] = []
    is_public: bool = False

class DashboardCreate(DashboardBase):
    business_id: str

class DashboardResponse(DashboardBase):
    id: str
    business_id: str
    is_active: bool
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

class WorkflowBase(BaseModel):
    name: str
    type: WorkflowType
    steps: List[Dict[str, Any]] = []
    data: Dict[str, Any] = {}

class WorkflowCreate(WorkflowBase):
    business_id: str

class WorkflowResponse(WorkflowBase):
    id: str
    business_id: str
    status: WorkflowStatus
    current_step: int
    created_by: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    updated_at: datetime

# ============================================================================
# Database Indexes (Optimized for Performance)
# ============================================================================

# These would be created in Alembic migrations
INDEXES = [
    # Business metrics - optimized for time-series queries
    "CREATE INDEX idx_business_metrics_business_date ON business_metrics(business_id, date)",
    "CREATE INDEX idx_business_metrics_type_period ON business_metrics(metric_type, period)",

    # Workflows - optimized for active workflow queries
    "CREATE INDEX idx_workflows_business_status ON workflows(business_id, status)",
    "CREATE INDEX idx_workflows_current_step ON workflows(current_step) WHERE status = 'active'",

    # Audit logs - optimized for chronological queries
    "CREATE INDEX idx_audit_logs_business_created ON audit_logs(business_id, created_at)",
    "CREATE INDEX idx_audit_logs_user_created ON audit_logs(user_id, created_at)",
]

__all__ = [
    # SQLAlchemy models
    "BusinessEntity", "User", "AuthToken",
    "BusinessMetric", "Dashboard", "Report",
    "Workflow", "WorkflowStep",
    "OdooConnection", "BusinessTemplate", "AuditLog",

    # COMPLIANCE MODELS (MIGRATED FROM DJANGO)
    "ComplianceRule", "AuditTrail", "ReportSchedule", "RecurringTransaction", "UserActivityLog",

    # ACCOUNTING MODELS (MIGRATED FROM DJANGO)
    "CashEntry", "IncomeExpense", "BasicLedger", "TaxCalculation",

    # ODOO DISCOVERY MODELS (CRITICAL)
    "OdooModel", "OdooField", "OdooModule", "DiscoverySession",

    # MSME BUSINESS INTELLIGENCE MODELS (CRITICAL)
    "MSMESetupWizard", "MSMEKPI", "MSMECompliance", "MSMEMarketing", "MSMEAnalytics",

    # Pydantic models - Core
    "BusinessEntityBase", "BusinessEntityCreate", "BusinessEntityResponse",
    "BusinessMetricBase", "BusinessMetricCreate", "BusinessMetricResponse",
    "DashboardBase", "DashboardCreate", "DashboardResponse",
    "WorkflowBase", "WorkflowCreate", "WorkflowResponse",

    # Pydantic models - ODOO DISCOVERY (CRITICAL)
    "OdooModelBase", "OdooModelCreate", "OdooModelResponse",
    "OdooFieldBase", "OdooFieldCreate", "OdooFieldResponse",
    "OdooModuleBase", "OdooModuleCreate", "OdooModuleResponse",
    "DiscoverySessionBase", "DiscoverySessionCreate", "DiscoverySessionResponse",

    # Pydantic models - MSME BUSINESS INTELLIGENCE (CRITICAL)
    "MSMESetupWizardBase", "MSMESetupWizardCreate", "MSMESetupWizardResponse",
    "MSMEKPIBase", "MSMEKPICreate", "MSMEKPIResponse",
    "MSMEComplianceBase", "MSMEComplianceCreate", "MSMEComplianceResponse",
    "MSMEMarketingBase", "MSMEMarketingCreate", "MSMEMarketingResponse",
    "MSMEAnalyticsBase", "MSMEAnalyticsCreate", "MSMEAnalyticsResponse",

    # Module Generation Models
    "ModuleGenerationHistory", "GeneratedModule", "ModuleTemplate",

    # Enums
    "BusinessType", "BusinessSize", "MetricType", "WorkflowType", "WorkflowStatus",

    # Database utilities
    "INDEXES"
]
