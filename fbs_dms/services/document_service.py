"""
FBS DMS Document Service

Core business logic for document management operations.
"""

import logging
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, QuerySet
from django.conf import settings

from ..models import Document, DocumentType, DocumentCategory, DocumentTag, FileAttachment

logger = logging.getLogger('fbs_dms')


class DocumentService:
    """Service for managing documents with Odoo integration through FBS app"""
    
    def __init__(self, company_id: str, solution_db: str = None):
        self.company_id = company_id
        self.solution_db = solution_db or f"djo_{company_id}_db"
    
    def create_document(
        self, 
        document_data: Dict[str, Any], 
        user: User,
        file_obj=None
    ) -> Document:
        """Create a new document"""
        try:
            with transaction.atomic():
                # Validate document type
                doc_type = self._get_document_type(document_data.get('document_type_id'))
                if not doc_type:
                    raise ValidationError("Invalid document type")
                
                # Validate category
                category = self._get_document_category(document_data.get('category_id'))
                if not category:
                    raise ValidationError("Invalid document category")
                
                # Create file attachment if file provided
                attachment = None
                if file_obj:
                    attachment = self._create_file_attachment(file_obj, user)
                    
                    # Validate file against document type
                    if not self._validate_file_for_type(attachment, doc_type):
                        attachment.delete()
                        raise ValidationError("File does not meet document type requirements")
                
                # Create document
                document = Document.objects.create(
                    name=document_data['name'],
                    title=document_data['title'],
                    document_type=doc_type,
                    category=category,
                    attachment=attachment,
                    created_by=user,
                    company_id=self.company_id,
                    description=document_data.get('description', ''),
                    confidentiality_level=document_data.get('confidentiality_level', 'internal'),
                    expiry_date=document_data.get('expiry_date'),
                    metadata=document_data.get('metadata', {})
                )
                
                # Add tags if provided
                if 'tag_ids' in document_data:
                    tags = DocumentTag.objects.filter(
                        id__in=document_data['tag_ids'],
                        is_active=True
                    )
                    document.tags.set(tags)
                
                # Start workflow if approval required
                if doc_type.requires_approval:
                    self._start_approval_workflow(document, user)
                
                # Sync to Odoo through FBS app
                self._sync_to_odoo(document, 'create')
                
                logger.info(f"Document created: {document.name} by {user.username}")
                return document
                
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise
    
    def update_document(
        self, 
        document_id: int, 
        update_data: Dict[str, Any], 
        user: User
    ) -> Document:
        """Update an existing document"""
        try:
            document = self._get_document(document_id)
            if not document:
                raise ValidationError("Document not found")
            
            # Check if document can be updated
            if not self._can_update_document(document, user):
                raise ValidationError("Document cannot be updated")
            
            with transaction.atomic():
                # Update basic fields
                for field, value in update_data.items():
                    if hasattr(document, field) and field not in ['id', 'created_at', 'created_by']:
                        setattr(document, field, value)
                
                # Update tags if provided
                if 'tag_ids' in update_data:
                    tags = DocumentTag.objects.filter(
                        id__in=update_data['tag_ids'],
                        is_active=True
                    )
                    document.tags.set(tags)
                
                document.save()
                
                # Sync to Odoo through FBS app
                self._sync_to_odoo(document, 'update')
                
                logger.info(f"Document updated: {document.name} by {user.username}")
                return document
                
        except Exception as e:
            logger.error(f"Failed to update document: {str(e)}")
            raise
    
    def delete_document(self, document_id: int, user: User) -> bool:
        """Delete a document"""
        try:
            document = self._get_document(document_id)
            if not document:
                raise ValidationError("Document not found")
            
            # Check if document can be deleted
            if not self._can_delete_document(document, user):
                raise ValidationError("Document cannot be deleted")
            
            with transaction.atomic():
                # Sync deletion to Odoo through FBS app
                self._sync_to_odoo(document, 'delete')
                
                # Delete file attachment
                if document.attachment:
                    document.attachment.delete()
                
                # Delete document
                document.delete()
                
                logger.info(f"Document deleted: {document.name} by {user.username}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise
    
    def get_document(self, document_id: int) -> Optional[Document]:
        """Get a document by ID"""
        return self._get_document(document_id)
    
    def list_documents(
        self,
        filters: Dict[str, Any] = None,
        ordering: str = '-created_at',
        limit: int = None
    ) -> QuerySet[Document]:
        """List documents with optional filtering"""
        queryset = Document.objects.filter(company_id=self.company_id)
        
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        queryset = queryset.order_by(ordering)
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    def search_documents(
        self, 
        query: str, 
        filters: Dict[str, Any] = None,
        limit: int = 50
    ) -> QuerySet[Document]:
        """Search documents by text query"""
        queryset = Document.objects.filter(company_id=self.company_id)
        
        # Text search
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        
        # Apply additional filters
        if filters:
            queryset = self._apply_filters(queryset, filters)
        
        return queryset.order_by('-created_at')[:limit]
    
    def get_document_types(self) -> QuerySet[DocumentType]:
        """Get all active document types"""
        return DocumentType.objects.filter(is_active=True).order_by('name')
    
    def get_document_categories(self) -> QuerySet[DocumentCategory]:
        """Get all active document categories"""
        return DocumentCategory.objects.filter(is_active=True).order_by('sequence', 'name')
    
    def get_document_tags(self) -> QuerySet[DocumentTag]:
        """Get all active document tags"""
        return DocumentTag.objects.filter(is_active=True).order_by('name')
    
    def _get_document(self, document_id: int) -> Optional[Document]:
        """Get document by ID with company check"""
        try:
            return Document.objects.get(
                id=document_id,
                company_id=self.company_id
            )
        except Document.DoesNotExist:
            return None
    
    def _get_document_type(self, type_id: int) -> Optional[DocumentType]:
        """Get document type by ID"""
        try:
            return DocumentType.objects.get(id=type_id, is_active=True)
        except DocumentType.DoesNotExist:
            return None
    
    def _get_document_category(self, category_id: int) -> Optional[DocumentCategory]:
        """Get document category by ID"""
        try:
            return DocumentCategory.objects.get(id=category_id, is_active=True)
        except DocumentCategory.DoesNotExist:
            return None
    
    def _create_file_attachment(self, file_obj, user: User) -> FileAttachment:
        """Create file attachment"""
        from ..models import FileAttachment
        
        return FileAttachment.objects.create(
            file=file_obj,
            uploaded_by=user,
            company_id=self.company_id
        )
    
    def _validate_file_for_type(self, attachment: FileAttachment, doc_type: DocumentType) -> bool:
        """Validate file against document type requirements"""
        # Check file extension
        if not doc_type.is_extension_allowed(attachment.original_filename):
            return False
        
        # Check file size
        max_size_bytes = doc_type.max_file_size * 1024 * 1024  # Convert MB to bytes
        if attachment.file_size > max_size_bytes:
            return False
        
        return True
    
    def _can_update_document(self, document: Document, user: User) -> bool:
        """Check if user can update document"""
        # Document creator can always update
        if document.created_by == user:
            return True
        
        # Check if user has admin permissions
        if user.is_staff:
            return True
        
        # Check if document is in editable state
        return document.state in ['draft', 'pending']
    
    def _can_delete_document(self, document: Document, user: User) -> bool:
        """Check if user can delete document"""
        # Document creator can delete if in draft state
        if document.created_by == user and document.state == 'draft':
            return True
        
        # Staff users can delete
        if user.is_staff:
            return True
        
        return False
    
    def _apply_filters(self, queryset: QuerySet, filters: Dict[str, Any]) -> QuerySet:
        """Apply filters to document queryset"""
        if 'state' in filters:
            queryset = queryset.filter(state=filters['state'])
        
        if 'document_type_id' in filters:
            queryset = queryset.filter(document_type_id=filters['document_type_id'])
        
        if 'category_id' in filters:
            queryset = queryset.filter(category_id=filters['category_id'])
        
        if 'created_by_id' in filters:
            queryset = queryset.filter(created_by_id=filters['created_by_id'])
        
        if 'confidentiality_level' in filters:
            queryset = queryset.filter(confidentiality_level=filters['confidentiality_level'])
        
        if 'date_from' in filters:
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        
        if 'date_to' in filters:
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        return queryset
    
    def _start_approval_workflow(self, document: Document, user: User):
        """Start approval workflow for document"""
        from .workflow_service import WorkflowService
        
        workflow_service = WorkflowService(self.company_id)
        workflow_service.start_document_workflow(document, user)
    
    def _sync_to_odoo(self, document: Document, operation: str):
        """Sync document changes to Odoo through FBS app"""
        try:
            # Check if FBS app is available
            if not self._is_fbs_available():
                logger.warning("FBS app not available, skipping Odoo sync")
                return
            
            # Use FBS app's Odoo integration
            fbs_interface = self._get_fbs_interface()
            if fbs_interface:
                # Map document to Odoo format
                odoo_data = self._map_to_odoo_format(document)
                
                if operation == 'create':
                    fbs_interface.odoo.create_record('fayvad.document', odoo_data)
                elif operation == 'update':
                    fbs_interface.odoo.update_record('fayvad.document', document.id, odoo_data)
                elif operation == 'delete':
                    fbs_interface.odoo.delete_record('fayvad.document', document.id)
                
                logger.info(f"Document {operation} synced to Odoo: {document.name}")
            
        except Exception as e:
            logger.error(f"Failed to sync document to Odoo: {str(e)}")
            # Don't fail the main operation if Odoo sync fails
    
    def _is_fbs_available(self) -> bool:
        """Check if FBS app is available"""
        try:
            import fbs_app
            return True
        except ImportError:
            return False
    
    def _get_fbs_interface(self):
        """Get FBS interface for Odoo integration"""
        try:
            from fbs_app.interfaces import FBSInterface
            # Use company_id as solution_name for FBS integration
            return FBSInterface(self.company_id)
        except ImportError:
            logger.warning("FBS app interfaces not available")
            return None
    
    def _map_to_odoo_format(self, document: Document) -> Dict[str, Any]:
        """Map Django document to Odoo format"""
        return {
            'name': document.name,
            'title': document.title,
            'document_type_id': document.document_type.id if document.document_type else False,
            'document_category_id': document.category.id if document.category else False,
            'tag_ids': [(6, 0, [tag.id for tag in document.tags.all()])],
            'attachment_id': document.attachment.id if document.attachment else False,
            'state': document.state,
            'created_by': document.created_by.id if document.created_by else False,
            'approved_by': document.approved_by.id if document.approved_by else False,
            'expiry_date': document.expiry_date.isoformat() if document.expiry_date else False,
            'company_id': document.company_id,
            'confidentiality_level': document.confidentiality_level,
            'description': document.description,
            'metadata': document.metadata,
        }
    
    def create_document_simple(
        self,
        name: str,
        title: str,
        document_type_id: int,
        category_id: int = None,
        description: str = '',
        expiry_date = None,
        confidentiality_level: str = 'internal',
        metadata: Dict[str, Any] = None,
        created_by: User = None
    ) -> Document:
        """Create a document with simple parameters"""
        document_data = {
            'name': name,
            'title': title,
            'document_type_id': document_type_id,
            'category_id': category_id,
            'description': description,
            'expiry_date': expiry_date,
            'confidentiality_level': confidentiality_level,
            'metadata': metadata or {}
        }
        
        return self.create_document(document_data, created_by)
    
    def approve_document(self, document_id: int, user: User, comments: str = '') -> Document:
        """Approve a document"""
        try:
            document = self._get_document(document_id)
            if not document:
                raise ValidationError("Document not found")
            
            # Check approval permissions
            if not self._can_approve_document(document, user):
                raise ValidationError("Cannot approve document")
            
            # Update document state
            document.state = 'approved'
            document.approved_by = user
            document.save()
            
            # Sync to Odoo
            self._sync_to_odoo(document, 'update')
            
            logger.info(f"Document approved: {document.name} by {user.username}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to approve document: {str(e)}")
            raise
    
    def reject_document(self, document_id: int, user: User, comments: str = '') -> Document:
        """Reject a document"""
        try:
            document = self._get_document(document_id)
            if not document:
                raise ValidationError("Document not found")
            
            # Check rejection permissions
            if not self._can_reject_document(document, user):
                raise ValidationError("Cannot reject document")
            
            # Update document state
            document.state = 'rejected'
            document.save()
            
            # Sync to Odoo
            self._sync_to_odoo(document, 'update')
            
            logger.info(f"Document rejected: {document.name} by {user.username}")
            return document
            
        except Exception as e:
            logger.error(f"Failed to reject document: {str(e)}")
            raise
    
    def get_documents(
        self,
        document_type: str = None,
        category: str = None,
        state: str = None,
        search: str = None,
        limit: int = 50
    ) -> QuerySet[Document]:
        """Get documents with optional filtering"""
        try:
            queryset = Document.objects.using(self.solution_db).filter(company_id=self.company_id)
            
            if document_type:
                queryset = queryset.filter(document_type__name=document_type)
            
            if category:
                queryset = queryset.filter(category__name=category)
            
            if state:
                queryset = queryset.filter(state=state)
            
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(title__icontains=search) |
                    Q(description__icontains=search)
                )
            
            return queryset.order_by('-created_at')[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get documents: {str(e)}")
            return Document.objects.none()
    
    def _can_approve_document(self, document: Document, user: User) -> bool:
        """Check if user can approve document"""
        # Document creator can approve
        if document.created_by == user:
            return True
        
        # Staff users can approve
        if user.is_staff:
            return True
        
        # Check if user is in approval workflow
        if hasattr(document, 'workflow') and document.workflow:
            return document.workflow.approval_steps.filter(
                approver=user,
                status='pending'
            ).exists()
        
        return False
    
    def _can_reject_document(self, document: Document, user: User) -> bool:
        """Check if user can approve document"""
        # Document creator can approve
        if document.created_by == user:
            return True
        
        # Staff users can approve
        if user.is_staff:
            return True
        
        # Check if user is in approval workflow
        if hasattr(document, 'workflow') and document.workflow:
            return document.workflow.approval_steps.filter(
                approver=user,
                status='pending'
            ).exists()
        
        return False
