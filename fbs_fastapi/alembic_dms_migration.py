"""
Alembic Migration for DMS Models

Creates database tables for Document Management System models.
Run this after creating the core FBS models.
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table, Float, JSON, Enum
from sqlalchemy.sql import func
from enum import Enum as PyEnum

# Define enums for migration
class DocumentState(PyEnum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class ConfidentialityLevel(PyEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"

def upgrade():
    """Upgrade database schema for DMS models"""

    # Create document types table
    op.create_table(
        'dms_document_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=False),
        sa.Column('allowed_extensions', sa.String(length=500), nullable=False),
        sa.Column('max_file_size', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )

    # Create document categories table
    op.create_table(
        'dms_document_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_id'], ['dms_document_categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name', 'parent')
    )

    # Create document tags table
    op.create_table(
        'dms_document_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create file attachments table
    op.create_table(
        'dms_file_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('checksum', sa.String(length=128), nullable=True),
        sa.Column('uploaded_by', sa.String(length=100), nullable=False),
        sa.Column('solution_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create documents table
    op.create_table(
        'dms_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('document_type_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('attachment_id', sa.Integer(), nullable=True),
        sa.Column('state', sa.Enum('DRAFT', 'PENDING', 'APPROVED', 'REJECTED', 'ARCHIVED', name='documentstate'), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('expiry_date', sa.DateTime(), nullable=True),
        sa.Column('company_id', sa.String(length=100), nullable=False),
        sa.Column('solution_name', sa.String(length=100), nullable=False),
        sa.Column('confidentiality_level', sa.Enum('PUBLIC', 'INTERNAL', 'CONFIDENTIAL', name='confidentialitylevel'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['document_type_id'], ['dms_document_types.id'], ),
        sa.ForeignKeyConstraint(['category_id'], ['dms_document_categories.id'], ),
        sa.ForeignKeyConstraint(['attachment_id'], ['dms_file_attachments.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create document workflows table
    op.create_table(
        'dms_document_workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('workflow_type', sa.String(length=50), nullable=False),
        sa.Column('current_step', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('solution_name', sa.String(length=100), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['dms_documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create document approvals table
    op.create_table(
        'dms_document_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_id', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(length=100), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['workflow_id'], ['dms_document_workflows.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create many-to-many association table for document tags
    op.create_table(
        'dms_document_tags',
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['dms_documents.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['dms_document_tags.id'], ),
        sa.PrimaryKeyConstraint('document_id', 'tag_id')
    )

    # Create indexes for better performance
    op.create_index(op.f('ix_dms_document_types_name'), 'dms_document_types', ['name'], unique=False)
    op.create_index(op.f('ix_dms_document_categories_name'), 'dms_document_categories', ['name'], unique=False)
    op.create_index(op.f('ix_dms_document_tags_name'), 'dms_document_tags', ['name'], unique=False)
    op.create_index(op.f('ix_dms_documents_solution_name'), 'dms_documents', ['solution_name'], unique=False)
    op.create_index(op.f('ix_dms_documents_state'), 'dms_documents', ['state'], unique=False)
    op.create_index(op.f('ix_dms_documents_created_by'), 'dms_documents', ['created_by'], unique=False)
    op.create_index(op.f('ix_dms_file_attachments_solution_name'), 'dms_file_attachments', ['solution_name'], unique=False)


def downgrade():
    """Downgrade database schema"""

    # Drop indexes
    op.drop_index(op.f('ix_dms_file_attachments_solution_name'), table_name='dms_file_attachments')
    op.drop_index(op.f('ix_dms_documents_created_by'), table_name='dms_documents')
    op.drop_index(op.f('ix_dms_documents_state'), table_name='dms_documents')
    op.drop_index(op.f('ix_dms_documents_solution_name'), table_name='dms_documents')
    op.drop_index(op.f('ix_dms_document_tags_name'), table_name='dms_document_tags')
    op.drop_index(op.f('ix_dms_document_categories_name'), table_name='dms_document_categories')
    op.drop_index(op.f('ix_dms_document_types_name'), table_name='dms_document_types')

    # Drop tables
    op.drop_table('dms_document_tags')
    op.drop_table('dms_document_approvals')
    op.drop_table('dms_document_workflows')
    op.drop_table('dms_documents')
    op.drop_table('dms_file_attachments')
    op.drop_table('dms_document_tags')
    op.drop_table('dms_document_categories')
    op.drop_table('dms_document_types')

    # Drop enums
    op.execute("DROP TYPE IF EXISTS documentstate")
    op.execute("DROP TYPE IF EXISTS confidentialitylevel")

