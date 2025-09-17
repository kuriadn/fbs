"""
FBS DMS Models - SQLAlchemy

Document Management System models migrated from Django to FastAPI.
Preserves all functionality while adapting to async SQLAlchemy patterns.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table, Float, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum
import uuid

# Import Base from core database module to avoid conflicts
from ..core.database import Base

# Document state choices
class DocumentState(PyEnum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

# Confidentiality choices
class ConfidentialityLevel(PyEnum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"

# Association table for many-to-many relationship between documents and tags
document_tags_association = Table(
    'dms_document_tags_association',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('dms_documents.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('dms_document_tags.id'), primary_key=True)
)

class DMSDocumentType(Base):
    """Document type configuration - migrated from Django"""

    __tablename__ = 'dms_document_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    requires_approval = Column(Boolean, default=False, nullable=False)
    allowed_extensions = Column(String(500), default='pdf,doc,docx,xls,xlsx,jpg,png', nullable=False)
    max_file_size = Column(Integer, default=50, nullable=False)  # MB
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    documents = relationship("DMSDocument", back_populates="document_type")

    def get_allowed_extensions_list(self):
        """Get allowed extensions as a list"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(',') if ext.strip()]

    def is_extension_allowed(self, filename):
        """Check if file extension is allowed"""
        if not filename:
            return False
        ext = filename.split('.')[-1].lower()
        return ext in self.get_allowed_extensions_list()

    def __repr__(self):
        return f"<DMSDocumentType(name='{self.name}', code='{self.code}')>"


class DMSDocumentCategory(Base):
    """Document category with hierarchical structure - migrated from Django"""

    __tablename__ = 'dms_document_categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey('dms_document_categories.id'), nullable=True)
    sequence = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    parent = relationship("DMSDocumentCategory", remote_side=[id], backref="children")
    documents = relationship("DMSDocument", back_populates="category")

    def __repr__(self):
        if self.parent:
            return f"<DMSDocumentCategory(name='{self.parent.name} > {self.name}')>"
        return f"<DMSDocumentCategory(name='{self.name}')>"


class DMSDocumentTag(Base):
    """Document tags for organization - migrated from Django"""

    __tablename__ = 'dms_document_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(Integer, default=1, nullable=False)  # 1-12
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    documents = relationship("DMSDocument", secondary=document_tags_association, back_populates="tags")

    def __repr__(self):
        return f"<DMSDocumentTag(name='{self.name}')>"


class DMSFileAttachment(Base):
    """File attachment model - migrated from Django"""

    __tablename__ = 'dms_file_attachments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    mime_type = Column(String(100), nullable=False)
    checksum = Column(String(128), nullable=True)  # SHA-256 hash
    uploaded_by = Column(String(100), nullable=False)  # user ID
    solution_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    documents = relationship("DMSDocument", back_populates="attachment")

    def get_file_url(self):
        """Generate file URL for download"""
        return f"/api/dms/files/{self.id}/download"

    def __repr__(self):
        return f"<DMSFileAttachment(filename='{self.filename}', size={self.file_size})>"


class DMSDocument(Base):
    """Main document model - migrated from Django"""

    __tablename__ = 'dms_documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Document reference
    title = Column(String(255), nullable=False)  # Document title
    document_type_id = Column(Integer, ForeignKey('dms_document_types.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('dms_document_categories.id'), nullable=False)
    attachment_id = Column(Integer, ForeignKey('dms_file_attachments.id'), nullable=True)
    state = Column(Enum(DocumentState), default=DocumentState.DRAFT, nullable=False)
    created_by = Column(String(100), nullable=False)  # user ID
    approved_by = Column(String(100), nullable=True)  # user ID
    expiry_date = Column(DateTime, nullable=True)
    company_id = Column(String(100), nullable=False)  # Multi-company support
    solution_name = Column(String(100), nullable=False)
    confidentiality_level = Column(Enum(ConfidentialityLevel), default=ConfidentialityLevel.INTERNAL, nullable=False)
    description = Column(Text, nullable=True)
    extra_metadata = Column(JSON, default=dict, nullable=False)
    version = Column(String(20), default='1.0', nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    document_type = relationship("DMSDocumentType", back_populates="documents")
    category = relationship("DMSDocumentCategory", back_populates="documents")
    attachment = relationship("DMSFileAttachment", back_populates="documents")
    tags = relationship("DMSDocumentTag", secondary=document_tags_association, back_populates="documents")
    workflows = relationship("DMSDocumentWorkflow", back_populates="document")

    def is_expired(self):
        """Check if document is expired"""
        if not self.expiry_date:
            return False
        return self.expiry_date < func.now()

    def can_be_approved_by(self, user_id):
        """Check if user can approve this document"""
        # Implementation would check user's permissions and workflow rules
        return True  # Simplified for now

    def get_download_url(self):
        """Get document download URL"""
        if self.attachment:
            return self.attachment.get_file_url()
        return None

    def __repr__(self):
        return f"<DMSDocument(name='{self.name}', state='{self.state.value}')>"


class DMSDocumentWorkflow(Base):
    """Document workflow instance - migrated from Django"""

    __tablename__ = 'dms_document_workflows'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey('dms_documents.id'), nullable=False)
    workflow_type = Column(String(50), default='approval', nullable=False)
    current_step = Column(String(100), default='draft', nullable=False)
    status = Column(String(20), default='active', nullable=False)  # active, completed, cancelled
    created_by = Column(String(100), nullable=False)
    solution_name = Column(String(100), nullable=False)
    extra_metadata = Column(JSON, default=dict, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    document = relationship("DMSDocument", back_populates="workflows")
    steps = relationship("DMSDocumentApproval", back_populates="workflow", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DMSDocumentWorkflow(document_id={self.document_id}, status='{self.status}')>"


class DMSDocumentApproval(Base):
    """Document approval step - migrated from Django"""

    __tablename__ = 'dms_document_approvals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey('dms_document_workflows.id'), nullable=False)
    step_name = Column(String(100), nullable=False)
    step_order = Column(Integer, nullable=False)
    assigned_to = Column(String(100), nullable=False)  # user ID
    status = Column(String(20), default='pending', nullable=False)  # pending, approved, rejected, skipped
    comments = Column(Text, nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    is_required = Column(Boolean, default=True, nullable=False)
    extra_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    workflow = relationship("DMSDocumentWorkflow", back_populates="steps")

    def is_overdue(self):
        """Check if approval step is overdue"""
        if not self.due_date:
            return False
        return self.due_date < func.now() and self.status == 'pending'

    def __repr__(self):
        return f"<DMSDocumentApproval(step='{self.step_name}', status='{self.status}')>"


# Export all models
__all__ = [
    'DMSDocumentType',
    'DMSDocumentCategory',
    'DMSDocumentTag',
    'DMSFileAttachment',
    'DMSDocument',
    'DMSDocumentWorkflow',
    'DMSDocumentApproval',
]
