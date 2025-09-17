"""
FBS v3 Alembic Migration

Database migration for FBS v3 streamlined models.
Creates all tables and indexes for the new architecture.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic
revision = 'fbs_v3_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create FBS v3 database schema"""

    # ============================================================================
    # CORE TABLES
    # ============================================================================

    # Business Entities
    op.create_table(
        'business_entities',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('industry', sa.String(100), nullable=True),
        sa.Column('size', sa.String(20), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Users
    op.create_table(
        'users',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', UUID(), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), default='user', nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Auth Tokens
    op.create_table(
        'auth_tokens',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', UUID(), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token')
    )

    # ============================================================================
    # BUSINESS INTELLIGENCE TABLES
    # ============================================================================

    # Business Metrics
    op.create_table(
        'business_metrics',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', UUID(), nullable=False),
        sa.Column('metric_type', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('value', sa.DECIMAL(15, 2), nullable=False),
        sa.Column('target', sa.DECIMAL(15, 2), nullable=True),
        sa.Column('period', sa.String(20), default='monthly', nullable=True),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Dashboards
    op.create_table(
        'dashboards',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), default='business', nullable=True),
        sa.Column('layout', sa.JSON(), nullable=True),
        sa.Column('widgets', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), default=False, nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('created_by', UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Reports
    op.create_table(
        'reports',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('schedule', sa.JSON(), nullable=True),
        sa.Column('output_format', sa.String(20), default='pdf', nullable=True),
        sa.Column('template', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('created_by', UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # ============================================================================
    # WORKFLOW TABLES
    # ============================================================================

    # Workflows
    op.create_table(
        'workflows',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', UUID(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), default='draft', nullable=True),
        sa.Column('current_step', sa.Integer(), default=0, nullable=True),
        sa.Column('steps', sa.JSON(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_by', UUID(), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Workflow Steps
    op.create_table(
        'workflow_steps',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('workflow_id', UUID(), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('assignee', UUID(), nullable=True),
        sa.Column('status', sa.String(20), default='pending', nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id']),
        sa.ForeignKeyConstraint(['assignee'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

# ============================================================================
# ODOO DISCOVERY TABLES (CRITICAL)
# ============================================================================

# Odoo Models
op.create_table(
    'odoo_models',
    sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('business_id', UUID(), nullable=False),
    sa.Column('model_name', sa.String(100), nullable=False),
    sa.Column('technical_name', sa.String(100), nullable=False),
    sa.Column('display_name', sa.String(200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('module_name', sa.String(100), nullable=False),
    sa.Column('model_type', sa.String(50), default='business', nullable=True),
    sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
    sa.Column('is_installed', sa.Boolean(), default=True, nullable=True),
    sa.Column('capabilities', sa.JSON(), nullable=True),
    sa.Column('constraints', sa.JSON(), nullable=True),
    sa.Column('discovered_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_verified', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
    sa.PrimaryKeyConstraint('id')
)

# Odoo Fields
op.create_table(
    'odoo_fields',
    sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('odoo_model_id', UUID(), nullable=False),
    sa.Column('field_name', sa.String(100), nullable=False),
    sa.Column('technical_name', sa.String(100), nullable=False),
    sa.Column('display_name', sa.String(200), nullable=False),
    sa.Column('field_type', sa.String(100), nullable=False),
    sa.Column('required', sa.Boolean(), default=False, nullable=True),
    sa.Column('readonly', sa.Boolean(), default=False, nullable=True),
    sa.Column('computed', sa.Boolean(), default=False, nullable=True),
    sa.Column('stored', sa.Boolean(), default=True, nullable=True),
    sa.Column('default_value', sa.Text(), nullable=True),
    sa.Column('help_text', sa.Text(), nullable=True),
    sa.Column('selection_options', sa.JSON(), nullable=True),
    sa.Column('relation_model', sa.String(100), nullable=True),
    sa.Column('field_constraints', sa.JSON(), nullable=True),
    sa.Column('discovered_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['odoo_model_id'], ['odoo_models.id']),
    sa.PrimaryKeyConstraint('id')
)

# Odoo Modules
op.create_table(
    'odoo_modules',
    sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('business_id', UUID(), nullable=False),
    sa.Column('module_name', sa.String(100), nullable=False),
    sa.Column('technical_name', sa.String(100), nullable=False),
    sa.Column('display_name', sa.String(200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('version', sa.String(50), nullable=False),
    sa.Column('author', sa.String(200), nullable=True),
    sa.Column('website', sa.String(255), nullable=True),
    sa.Column('category', sa.String(100), nullable=False),
    sa.Column('is_installed', sa.Boolean(), default=True, nullable=True),
    sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
    sa.Column('auto_install', sa.Boolean(), default=False, nullable=True),
    sa.Column('depends', sa.JSON(), nullable=True),
    sa.Column('data_files', sa.JSON(), nullable=True),
    sa.Column('demo_data', sa.Boolean(), default=False, nullable=True),
    sa.Column('application', sa.Boolean(), default=False, nullable=True),
    sa.Column('discovered_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('last_verified', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
    sa.PrimaryKeyConstraint('id')
)

# Discovery Sessions
op.create_table(
    'discovery_sessions',
    sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('business_id', UUID(), nullable=False),
    sa.Column('session_id', sa.String(100), nullable=False),
    sa.Column('session_type', sa.String(50), nullable=False),
    sa.Column('status', sa.String(20), default='running', nullable=True),
    sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('total_models', sa.Integer(), default=0, nullable=True),
    sa.Column('total_fields', sa.Integer(), default=0, nullable=True),
    sa.Column('total_modules', sa.Integer(), default=0, nullable=True),
    sa.Column('errors', sa.JSON(), nullable=True),
    sa.Column('configuration', sa.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('session_id')
)

# ============================================================================
# MSME BUSINESS INTELLIGENCE TABLES (CRITICAL)
# ============================================================================

# MSME Setup Wizards
op.create_table(
    'msme_setup_wizards',
    sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('business_id', UUID(), nullable=False),
    sa.Column('status', sa.String(20), default='not_started', nullable=True),
    sa.Column('current_step', sa.String(100), nullable=True),
    sa.Column('total_steps', sa.Integer(), default=0, nullable=True),
    sa.Column('progress', sa.DECIMAL(5, 2), default=0.0, nullable=True),
    sa.Column('business_type', sa.String(100), nullable=True),
    sa.Column('configuration', sa.JSON(), nullable=True),
    sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
    sa.PrimaryKeyConstraint('id')
)

# MSME KPIs
op.create_table(
    'msme_kpis',
    sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('business_id', UUID(), nullable=False),
    sa.Column('kpi_name', sa.String(200), nullable=False),
    sa.Column('kpi_type', sa.String(20), nullable=False),
    sa.Column('current_value', sa.DECIMAL(15, 2), nullable=False),
    sa.Column('target_value', sa.DECIMAL(15, 2), nullable=True),
    sa.Column('unit', sa.String(50), nullable=True),
    sa.Column('period', sa.String(20), default='monthly', nullable=True),
    sa.Column('trend', sa.String(20), nullable=True),
    sa.Column('last_updated', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
    sa.PrimaryKeyConstraint('id')
)

# MSME Compliance
op.create_table(
    'msme_compliance',
    sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('business_id', UUID(), nullable=False),
    sa.Column('compliance_type', sa.String(20), nullable=False),
    sa.Column('status', sa.String(20), default='pending', nullable=True),
    sa.Column('due_date', sa.Date(), nullable=False),
    sa.Column('actual_completion_date', sa.Date(), nullable=True),
    sa.Column('requirements', sa.JSON(), nullable=True),
    sa.Column('documents', sa.JSON(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('last_checked', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
    sa.PrimaryKeyConstraint('id')
)

# MSME Marketing
op.create_table(
    'msme_marketing',
    sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('business_id', UUID(), nullable=False),
    sa.Column('campaign_name', sa.String(200), nullable=False),
    sa.Column('campaign_type', sa.String(20), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('budget', sa.DECIMAL(15, 2), nullable=True),
    sa.Column('target_audience', sa.JSON(), nullable=True),
    sa.Column('metrics', sa.JSON(), nullable=True),
    sa.Column('status', sa.String(20), default='active', nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
    sa.PrimaryKeyConstraint('id')
)

# MSME Analytics
op.create_table(
    'msme_analytics',
    sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('business_id', UUID(), nullable=False),
    sa.Column('metric_name', sa.String(200), nullable=False),
    sa.Column('metric_value', sa.DECIMAL(15, 2), nullable=False),
    sa.Column('metric_type', sa.String(50), nullable=False),
    sa.Column('period', sa.String(20), default='monthly', nullable=True),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('context', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
    sa.PrimaryKeyConstraint('id')
)

# ============================================================================
# INTEGRATION TABLES
# ============================================================================

# Odoo Connections
op.create_table(
        'odoo_connections',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', UUID(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('host', sa.String(255), nullable=False),
        sa.Column('port', sa.Integer(), default=8069, nullable=True),
        sa.Column('protocol', sa.String(10), default='http', nullable=True),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
        sa.PrimaryKeyConstraint('id')
    )

# Business Templates
op.create_table(
        'business_templates',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('business_type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # ============================================================================
    # AUDIT TABLES
    # ============================================================================

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('business_id', UUID(), nullable=True),
        sa.Column('user_id', UUID(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource', sa.String(100), nullable=False),
        sa.Column('resource_id', UUID(), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['business_entities.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # ============================================================================
    # COMPLIANCE TABLES (MIGRATED FROM DJANGO)
    # ============================================================================

    # Compliance Rules
    op.create_table(
        'compliance_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('compliance_type', sa.String(length=20), nullable=False),
        sa.Column('requirements', sa.JSON(), nullable=False),
        sa.Column('check_frequency', sa.String(length=20), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('solution_name', 'name')
    )

    # Audit Trails
    op.create_table(
        'audit_trails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Report Schedules
    op.create_table(
        'report_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=100), nullable=False),
        sa.Column('report_type', sa.String(length=50), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('next_run', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Recurring Transactions
    op.create_table(
        'recurring_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_due', sa.DateTime(timezone=True), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # User Activity Logs
    op.create_table(
        'user_activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=100), nullable=False),
        sa.Column('solution_name', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # ============================================================================
    # ACCOUNTING TABLES (MIGRATED FROM DJANGO)
    # ============================================================================

    # Cash Entries
    op.create_table(
        'cash_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.String(length=100), nullable=False),
        sa.Column('entry_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('entry_type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('vendor_customer', sa.String(length=200), nullable=True),
        sa.Column('tax_amount', sa.Float(), nullable=False),
        sa.Column('tax_rate', sa.Float(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Income Expenses
    op.create_table(
        'income_expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.String(length=100), nullable=False),
        sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('tax_category', sa.String(length=50), nullable=True),
        sa.Column('tax_amount', sa.Float(), nullable=False),
        sa.Column('recurring', sa.Boolean(), nullable=False),
        sa.Column('recurring_frequency', sa.String(length=20), nullable=True),
        sa.Column('vendor_customer', sa.String(length=200), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Basic Ledgers
    op.create_table(
        'basic_ledgers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.String(length=100), nullable=False),
        sa.Column('account_name', sa.String(length=100), nullable=False),
        sa.Column('account_type', sa.String(length=50), nullable=False),
        sa.Column('account_code', sa.String(length=20), nullable=True),
        sa.Column('parent_account_id', sa.Integer(), nullable=True),
        sa.Column('balance', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_account_id'], ['basic_ledgers.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Tax Calculations
    op.create_table(
        'tax_calculations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('business_id', sa.String(length=100), nullable=False),
        sa.Column('tax_period', sa.String(length=20), nullable=False),
        sa.Column('tax_year', sa.Integer(), nullable=False),
        sa.Column('tax_type', sa.String(length=50), nullable=False),
        sa.Column('taxable_amount', sa.Float(), nullable=False),
        sa.Column('tax_rate', sa.Float(), nullable=False),
        sa.Column('tax_amount', sa.Float(), nullable=False),
        sa.Column('paid_amount', sa.Float(), nullable=False),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # ============================================================================
    # LICENSE MANAGER TABLES
    # ============================================================================

    # Solution Licenses
    op.create_table(
        'solution_licenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=255), nullable=False),
        sa.Column('solution_db', sa.String(length=100), nullable=True),
        sa.Column('license_type', sa.String(length=20), nullable=False),
        sa.Column('license_key', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('activation_date', sa.DateTime(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('msme_businesses_limit', sa.Integer(), nullable=False),
        sa.Column('workflows_limit', sa.Integer(), nullable=False),
        sa.Column('reports_limit', sa.Integer(), nullable=False),
        sa.Column('users_limit', sa.Integer(), nullable=False),
        sa.Column('storage_limit_gb', sa.Float(), nullable=False),
        sa.Column('enable_msme', sa.Boolean(), nullable=False),
        sa.Column('enable_bi', sa.Boolean(), nullable=False),
        sa.Column('enable_workflows', sa.Boolean(), nullable=False),
        sa.Column('enable_compliance', sa.Boolean(), nullable=False),
        sa.Column('enable_accounting', sa.Boolean(), nullable=False),
        sa.Column('enable_dms', sa.Boolean(), nullable=False),
        sa.Column('enable_licensing', sa.Boolean(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_checked_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('solution_name')
    )

    # Feature Usage
    op.create_table(
        'feature_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=255), nullable=False),
        sa.Column('feature_name', sa.String(length=100), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # License Audit Logs
    op.create_table(
        'license_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=255), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('performed_by', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Upgrade Recommendations
    op.create_table(
        'upgrade_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=255), nullable=False),
        sa.Column('current_tier', sa.String(length=20), nullable=False),
        sa.Column('recommended_tier', sa.String(length=20), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('feature_usage', sa.JSON(), nullable=False),
        sa.Column('potential_savings', sa.Float(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

# ============================================================================
# INDEXES
    # ============================================================================

    # Business metrics indexes
    op.create_index('idx_business_metrics_business_date', 'business_metrics', ['business_id', 'date'])
    op.create_index('idx_business_metrics_type_period', 'business_metrics', ['metric_type', 'period'])

    # Workflows indexes
    op.create_index('idx_workflows_business_status', 'workflows', ['business_id', 'status'])
    op.create_index('idx_workflows_current_step', 'workflows', ['current_step'], postgresql_where=sa.text("status = 'active'"))

# Odoo discovery indexes
op.create_index('idx_odoo_models_business', 'odoo_models', ['business_id', 'is_active'])
op.create_index('idx_odoo_fields_model', 'odoo_fields', ['odoo_model_id'])
op.create_index('idx_odoo_modules_business', 'odoo_modules', ['business_id', 'is_active'])
op.create_index('idx_discovery_sessions_business', 'discovery_sessions', ['business_id', 'status'])

# MSME business intelligence indexes
op.create_index('idx_msme_kpis_business', 'msme_kpis', ['business_id', 'kpi_type'])
op.create_index('idx_msme_compliance_business', 'msme_compliance', ['business_id', 'compliance_type'])
op.create_index('idx_msme_marketing_business', 'msme_marketing', ['business_id', 'status'])
op.create_index('idx_msme_analytics_business', 'msme_analytics', ['business_id', 'metric_name', 'date'])

    # Audit logs indexes
    op.create_index('idx_audit_logs_business_created', 'audit_logs', ['business_id', 'created_at'])
    op.create_index('idx_audit_logs_user_created', 'audit_logs', ['user_id', 'created_at'])

# Compliance indexes
op.create_index('idx_compliance_rules_solution_name', 'compliance_rules', ['solution_name'], unique=False)
op.create_index('idx_compliance_rules_type', 'compliance_rules', ['compliance_type'], unique=False)
op.create_index('idx_audit_trails_solution_name', 'audit_trails', ['solution_name'], unique=False)
op.create_index('idx_audit_trails_action', 'audit_trails', ['action'], unique=False)
op.create_index('idx_audit_trails_timestamp', 'audit_trails', ['timestamp'], unique=False)
op.create_index('idx_report_schedules_solution_name', 'report_schedules', ['solution_name'], unique=False)
op.create_index('idx_report_schedules_next_run', 'report_schedules', ['next_run'], unique=False)
op.create_index('idx_recurring_transactions_solution_name', 'recurring_transactions', ['solution_name'], unique=False)
op.create_index('idx_recurring_transactions_next_due', 'recurring_transactions', ['next_due'], unique=False)
op.create_index('idx_user_activity_logs_user_id', 'user_activity_logs', ['user_id'], unique=False)
op.create_index('idx_user_activity_logs_timestamp', 'user_activity_logs', ['timestamp'], unique=False)

# Accounting indexes
op.create_index('idx_cash_entries_business_id', 'cash_entries', ['business_id'], unique=False)
op.create_index('idx_cash_entries_entry_date', 'cash_entries', ['entry_date'], unique=False)
op.create_index('idx_cash_entries_entry_type', 'cash_entries', ['entry_type'], unique=False)
op.create_index('idx_income_expenses_business_id', 'income_expenses', ['business_id'], unique=False)
op.create_index('idx_income_expenses_transaction_date', 'income_expenses', ['transaction_date'], unique=False)
op.create_index('idx_income_expenses_transaction_type', 'income_expenses', ['transaction_type'], unique=False)
op.create_index('idx_basic_ledgers_business_id', 'basic_ledgers', ['business_id'], unique=False)
op.create_index('idx_basic_ledgers_account_type', 'basic_ledgers', ['account_type'], unique=False)
op.create_index('idx_tax_calculations_business_id', 'tax_calculations', ['business_id'], unique=False)
op.create_index('idx_tax_calculations_due_date', 'tax_calculations', ['due_date'], unique=False)
op.create_index('idx_tax_calculations_status', 'tax_calculations', ['status'], unique=False)


# License Manager indexes
op.create_index('idx_solution_licenses_solution_name', 'solution_licenses', ['solution_name'], unique=True)
op.create_index('idx_solution_licenses_license_type', 'solution_licenses', ['license_type'], unique=False)
op.create_index('idx_solution_licenses_status', 'solution_licenses', ['status'], unique=False)
op.create_index('idx_feature_usage_solution_name', 'feature_usage', ['solution_name'], unique=False)
op.create_index('idx_feature_usage_feature_name', 'feature_usage', ['feature_name'], unique=False)
op.create_index('idx_license_audit_logs_solution_name', 'license_audit_logs', ['solution_name'], unique=False)
op.create_index('idx_license_audit_logs_action', 'license_audit_logs', ['action'], unique=False)
op.create_index('idx_upgrade_recommendations_solution_name', 'upgrade_recommendations', ['solution_name'], unique=False)
op.create_index('idx_upgrade_recommendations_priority', 'upgrade_recommendations', ['priority'], unique=False)

def downgrade():
    """Drop FBS v3 database schema"""

    # Drop indexes first
    # License Manager indexes
    op.drop_index('idx_upgrade_recommendations_priority')
    op.drop_index('idx_upgrade_recommendations_solution_name')
    op.drop_index('idx_license_audit_logs_action')
    op.drop_index('idx_license_audit_logs_solution_name')
    op.drop_index('idx_feature_usage_feature_name')
    op.drop_index('idx_feature_usage_solution_name')
    op.drop_index('idx_solution_licenses_status')
    op.drop_index('idx_solution_licenses_license_type')
    op.drop_index('idx_solution_licenses_solution_name')

    op.drop_index('idx_dms_documents_created_by')
    op.drop_index('idx_dms_documents_state')
    op.drop_index('idx_dms_documents_solution_name')
    op.drop_index('idx_dms_document_tags_name')
    op.drop_index('idx_dms_document_categories_name')
    op.drop_index('idx_dms_document_types_name')

    # Other indexes
    op.drop_index('idx_audit_logs_user_created')
    op.drop_index('idx_audit_logs_business_created')
    op.drop_index('idx_workflows_current_step')
    op.drop_index('idx_workflows_business_status')
    op.drop_index('idx_business_metrics_type_period')
    op.drop_index('idx_business_metrics_business_date')

    # Drop tables in reverse order
    # Accounting tables
    op.drop_table('tax_calculations')
    op.drop_table('basic_ledgers')
    op.drop_table('income_expenses')
    op.drop_table('cash_entries')

    # Compliance tables
    op.drop_table('user_activity_logs')
    op.drop_table('recurring_transactions')
    op.drop_table('report_schedules')
    op.drop_table('audit_trails')
    op.drop_table('compliance_rules')

    # License Manager tables
    op.drop_table('upgrade_recommendations')
    op.drop_table('license_audit_logs')
    op.drop_table('feature_usage')
    op.drop_table('solution_licenses')


    # Other tables
    op.drop_table('audit_logs')
    op.drop_table('business_templates')
    op.drop_table('odoo_connections')
    op.drop_table('workflow_steps')
    op.drop_table('workflows')
    op.drop_table('reports')
    op.drop_table('dashboards')
    op.drop_table('business_metrics')
    op.drop_table('auth_tokens')
    op.drop_table('users')
    op.drop_table('business_entities')
