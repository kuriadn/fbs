"""
Alembic Migration for License Manager Models

Creates database tables for License Management System models.
Run this after creating the core FBS models.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, Enum, Float
from sqlalchemy.sql import func
from enum import Enum as PyEnum

class LicenseType(PyEnum):
    TRIAL = "trial"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class LicenseStatus(PyEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

class FeatureUsageStatus(PyEnum):
    ACTIVE = "active"
    EXCEEDED = "exceeded"
    BLOCKED = "blocked"

def upgrade():
    """Upgrade database schema for License Manager models"""

    # Create solution licenses table
    op.create_table(
        'solution_licenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=255), nullable=False),
        sa.Column('solution_db', sa.String(length=100), nullable=True),
        sa.Column('license_type', sa.Enum('TRIAL', 'BASIC', 'PROFESSIONAL', 'ENTERPRISE', name='licensetype'), nullable=False),
        sa.Column('license_key', sa.String(length=255), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'EXPIRED', 'SUSPENDED', 'CANCELLED', name='licensestatus'), nullable=False),
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

    # Create feature usage table
    op.create_table(
        'feature_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=255), nullable=False),
        sa.Column('feature_name', sa.String(length=100), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('period_start', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'EXCEEDED', 'BLOCKED', name='featureusagestatus'), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create license audit log table
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

    # Create upgrade recommendations table
    op.create_table(
        'upgrade_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('solution_name', sa.String(length=255), nullable=False),
        sa.Column('current_tier', sa.Enum('TRIAL', 'BASIC', 'PROFESSIONAL', 'ENTERPRISE', name='licensetype'), nullable=False),
        sa.Column('recommended_tier', sa.Enum('TRIAL', 'BASIC', 'PROFESSIONAL', 'ENTERPRISE', name='licensetype'), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('feature_usage', sa.JSON(), nullable=False),
        sa.Column('potential_savings', sa.Float(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for better performance
    op.create_index(op.f('ix_solution_licenses_solution_name'), 'solution_licenses', ['solution_name'], unique=True)
    op.create_index(op.f('ix_solution_licenses_license_type'), 'solution_licenses', ['license_type'], unique=False)
    op.create_index(op.f('ix_solution_licenses_status'), 'solution_licenses', ['status'], unique=False)
    op.create_index(op.f('ix_feature_usage_solution_name'), 'feature_usage', ['solution_name'], unique=False)
    op.create_index(op.f('ix_feature_usage_feature_name'), 'feature_usage', ['feature_name'], unique=False)
    op.create_index(op.f('ix_license_audit_logs_solution_name'), 'license_audit_logs', ['solution_name'], unique=False)
    op.create_index(op.f('ix_license_audit_logs_action'), 'license_audit_logs', ['action'], unique=False)
    op.create_index(op.f('ix_upgrade_recommendations_solution_name'), 'upgrade_recommendations', ['solution_name'], unique=False)
    op.create_index(op.f('ix_upgrade_recommendations_priority'), 'upgrade_recommendations', ['priority'], unique=False)

    # Insert default trial license data (optional - can be done via application)
    # This is handled by the LicenseService when first accessed


def downgrade():
    """Downgrade database schema"""

    # Drop indexes
    op.drop_index(op.f('ix_upgrade_recommendations_priority'), table_name='upgrade_recommendations')
    op.drop_index(op.f('ix_upgrade_recommendations_solution_name'), table_name='upgrade_recommendations')
    op.drop_index(op.f('ix_license_audit_logs_action'), table_name='license_audit_logs')
    op.drop_index(op.f('ix_license_audit_logs_solution_name'), table_name='license_audit_logs')
    op.drop_index(op.f('ix_feature_usage_feature_name'), table_name='feature_usage')
    op.drop_index(op.f('ix_feature_usage_solution_name'), table_name='feature_usage')
    op.drop_index(op.f('ix_solution_licenses_status'), table_name='solution_licenses')
    op.drop_index(op.f('ix_solution_licenses_license_type'), table_name='solution_licenses')
    op.drop_index(op.f('ix_solution_licenses_solution_name'), table_name='solution_licenses')

    # Drop tables
    op.drop_table('upgrade_recommendations')
    op.drop_table('license_audit_logs')
    op.drop_table('feature_usage')
    op.drop_table('solution_licenses')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS licensetype")
    op.execute("DROP TYPE IF EXISTS licensestatus")
    op.execute("DROP TYPE IF EXISTS featureusagestatus")

