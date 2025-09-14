"""
FBS DMS Service - FastAPI

Document Management System service migrated from Django to FastAPI.
Provides complete document CRUD operations with workflow management.
"""

import os
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

from sqlalchemy import and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.base_service import BaseService, AsyncServiceMixin
from ..models.dms_models import (
    DMSDocument, DMSDocumentType, DMSDocumentCategory, DMSDocumentTag,
    DMSFileAttachment, DMSDocumentWorkflow, DMSDocumentApproval,
    DocumentState, ConfidentialityLevel
)


class DocumentService(BaseService, AsyncServiceMixin):
    """Document management service - migrated from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)
        self.upload_path = Path("uploads") / solution_name / "dms"
        self.upload_path.mkdir(parents=True, exist_ok=True)

    async def create_document(
        self,
        document_data: Dict[str, Any],
        created_by: str,
        file_obj: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Create a new document - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Validate document type
                doc_type = await db.query(DMSDocumentType).filter(
                    and_(
                        DMSDocumentType.id == document_data['document_type_id'],
                        DMSDocumentType.is_active == True
                    )
                ).first()

                if not doc_type:
                    return {
                        'success': False,
                        'error': 'Invalid document type'
                    }

                # Validate category
                category = await db.query(DMSDocumentCategory).filter(
                    and_(
                        DMSDocumentCategory.id == document_data['category_id'],
                        DMSDocumentCategory.is_active == True
                    )
                ).first()

                if not category:
                    return {
                        'success': False,
                        'error': 'Invalid document category'
                    }

                # Handle file upload if provided
                attachment = None
                if file_obj:
                    attachment_result = await self._handle_file_upload(file_obj, created_by)
                    if attachment_result['success']:
                        attachment = attachment_result['attachment']
                    else:
                        return attachment_result

                # Create document
                document = DMSDocument(
                    name=document_data['name'],
                    title=document_data['title'],
                    document_type_id=document_data['document_type_id'],
                    category_id=document_data['category_id'],
                    attachment_id=attachment.id if attachment else None,
                    state=DocumentState.DRAFT,
                    created_by=created_by,
                    company_id=document_data.get('company_id', 'default'),
                    solution_name=self.solution_name,
                    confidentiality_level=document_data.get('confidentiality_level', ConfidentialityLevel.INTERNAL),
                    description=document_data.get('description', ''),
                    metadata=document_data.get('metadata', {}),
                    expiry_date=document_data.get('expiry_date')
                )

                db.add(document)

                # Handle tags if provided
                if 'tags' in document_data:
                    await self._add_document_tags(db, document, document_data['tags'])

                # Create workflow if document type requires approval
                if doc_type.requires_approval:
                    await self._create_approval_workflow(db, document, created_by)

                await db.commit()
                await db.refresh(document)

                return {
                    'success': True,
                    'document': {
                        'id': document.id,
                        'name': document.name,
                        'title': document.title,
                        'state': document.state.value,
                        'created_by': document.created_by,
                        'created_at': document.created_at.isoformat(),
                        'requires_approval': doc_type.requires_approval
                    },
                    'message': 'Document created successfully'
                }

        except Exception as e:
            await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))
            return {
                'success': False,
                'error': f'Failed to create document: {str(e)}'
            }

    async def get_document(self, document_id: int, user_id: str) -> Dict[str, Any]:
        """Get document by ID - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                document = await db.query(DMSDocument).filter(
                    and_(
                        DMSDocument.id == document_id,
                        DMSDocument.solution_name == self.solution_name,
                        DMSDocument.is_active == True
                    )
                ).first()

                if not document:
                    return {
                        'success': False,
                        'error': 'Document not found'
                    }

                # Check permissions
                if not await self._check_document_access(db, document, user_id):
                    return {
                        'success': False,
                        'error': 'Access denied'
                    }

                return {
                    'success': True,
                    'document': await self._serialize_document(document)
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get document: {str(e)}'
            }

    async def update_document(
        self,
        document_id: int,
        update_data: Dict[str, Any],
        updated_by: str
    ) -> Dict[str, Any]:
        """Update document - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                document = await db.query(DMSDocument).filter(
                    and_(
                        DMSDocument.id == document_id,
                        DMSDocument.solution_name == self.solution_name,
                        DMSDocument.is_active == True
                    )
                ).first()

                if not document:
                    return {
                        'success': False,
                        'error': 'Document not found'
                    }

                # Check if user can edit this document
                if not await self._can_edit_document(db, document, updated_by):
                    return {
                        'success': False,
                        'error': 'Cannot edit document'
                    }

                # Update fields
                for field, value in update_data.items():
                    if hasattr(document, field):
                        setattr(document, field, value)

                document.updated_at = datetime.utcnow()
                await db.commit()

                return {
                    'success': True,
                    'document': await self._serialize_document(document),
                    'message': 'Document updated successfully'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to update document: {str(e)}'
            }

    async def delete_document(self, document_id: int, deleted_by: str) -> Dict[str, Any]:
        """Soft delete document - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                document = await db.query(DMSDocument).filter(
                    and_(
                        DMSDocument.id == document_id,
                        DMSDocument.solution_name == self.solution_name,
                        DMSDocument.is_active == True
                    )
                ).first()

                if not document:
                    return {
                        'success': False,
                        'error': 'Document not found'
                    }

                # Check permissions
                if not await self._can_delete_document(db, document, deleted_by):
                    return {
                        'success': False,
                        'error': 'Cannot delete document'
                    }

                # Soft delete
                document.is_active = False
                document.updated_at = datetime.utcnow()
                await db.commit()

                return {
                    'success': True,
                    'message': 'Document deleted successfully'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to delete document: {str(e)}'
            }

    async def list_documents(
        self,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """List documents with filtering and pagination - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                query = db.query(DMSDocument).filter(
                    and_(
                        DMSDocument.solution_name == self.solution_name,
                        DMSDocument.is_active == True
                    )
                )

                # Apply filters
                if filters:
                    if 'state' in filters:
                        query = query.filter(DMSDocument.state == filters['state'])
                    if 'document_type_id' in filters:
                        query = query.filter(DMSDocument.document_type_id == filters['document_type_id'])
                    if 'category_id' in filters:
                        query = query.filter(DMSDocument.category_id == filters['category_id'])
                    if 'created_by' in filters:
                        query = query.filter(DMSDocument.created_by == filters['created_by'])
                    if 'search' in filters:
                        search_term = f"%{filters['search']}%"
                        query = query.filter(
                            or_(
                                DMSDocument.name.ilike(search_term),
                                DMSDocument.title.ilike(search_term),
                                DMSDocument.description.ilike(search_term)
                            )
                        )

                # Get total count
                total = await db.scalar(
                    query.with_entities(func.count(DMSDocument.id))
                )

                # Apply pagination
                offset = (page - 1) * limit
                documents = await db.execute(
                    query.offset(offset).limit(limit)
                )
                documents = documents.scalars().all()

                # Serialize documents
                document_list = []
                for doc in documents:
                    document_list.append(await self._serialize_document(doc))

                return {
                    'success': True,
                    'documents': document_list,
                    'pagination': {
                        'page': page,
                        'limit': limit,
                        'total': total,
                        'pages': (total + limit - 1) // limit
                    }
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to list documents: {str(e)}'
            }

    async def approve_document(
        self,
        document_id: int,
        approved_by: str,
        comments: Optional[str] = None
    ) -> Dict[str, Any]:
        """Approve document - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                document = await db.query(DMSDocument).filter(
                    and_(
                        DMSDocument.id == document_id,
                        DMSDocument.solution_name == self.solution_name,
                        DMSDocument.is_active == True
                    )
                ).first()

                if not document:
                    return {
                        'success': False,
                        'error': 'Document not found'
                    }

                # Check if document can be approved
                if document.state != DocumentState.PENDING:
                    return {
                        'success': False,
                        'error': 'Document is not in pending state'
                    }

                # Update document
                document.state = DocumentState.APPROVED
                document.approved_by = approved_by
                document.approved_at = datetime.utcnow()
                document.updated_at = datetime.utcnow()

                # Update workflow if exists
                workflow = await db.query(DMSDocumentWorkflow).filter(
                    and_(
                        DMSDocumentWorkflow.document_id == document_id,
                        DMSDocumentWorkflow.status == 'active'
                    )
                ).first()

                if workflow:
                    workflow.status = 'completed'
                    workflow.completed_at = datetime.utcnow()

                    # Update approval steps
                    await db.execute(
                        DMSDocumentApproval.__table__.update().where(
                            DMSDocumentApproval.workflow_id == workflow.id
                        ).values(
                            status='approved',
                            approved_at=datetime.utcnow()
                        )
                    )

                await db.commit()

                return {
                    'success': True,
                    'document': await self._serialize_document(document),
                    'message': 'Document approved successfully'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to approve document: {str(e)}'
            }

    async def reject_document(
        self,
        document_id: int,
        rejected_by: str,
        comments: str
    ) -> Dict[str, Any]:
        """Reject document - migrated from Django"""
        try:
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                document = await db.query(DMSDocument).filter(
                    and_(
                        DMSDocument.id == document_id,
                        DMSDocument.solution_name == self.solution_name,
                        DMSDocument.is_active == True
                    )
                ).first()

                if not document:
                    return {
                        'success': False,
                        'error': 'Document not found'
                    }

                # Update document
                document.state = DocumentState.REJECTED
                document.updated_at = datetime.utcnow()

                # Update workflow if exists
                workflow = await db.query(DMSDocumentWorkflow).filter(
                    and_(
                        DMSDocumentWorkflow.document_id == document_id,
                        DMSDocumentWorkflow.status == 'active'
                    )
                ).first()

                if workflow:
                    workflow.status = 'completed'
                    workflow.completed_at = datetime.utcnow()

                    # Update approval steps
                    await db.execute(
                        DMSDocumentApproval.__table__.update().where(
                            DMSDocumentApproval.workflow_id == workflow.id
                        ).values(
                            status='rejected',
                            comments=comments,
                            approved_at=datetime.utcnow()
                        )
                    )

                await db.commit()

                return {
                    'success': True,
                    'document': await self._serialize_document(document),
                    'message': 'Document rejected successfully'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to reject document: {str(e)}'
            }

    # Private helper methods

    async def _handle_file_upload(self, file_obj: Any, uploaded_by: str) -> Dict[str, Any]:
        """Handle file upload and create attachment record"""
        try:
            from ..core.dependencies import get_db_session_for_request
            import aiofiles
            import hashlib

            # Generate unique filename
            file_ext = Path(file_obj.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = self.upload_path / unique_filename

            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file_obj.read()
                await f.write(content)

            # Calculate checksum
            checksum = hashlib.sha256(content).hexdigest()

            # Create attachment record
            async for db in get_db_session_for_request(None):
                attachment = DMSFileAttachment(
                    filename=unique_filename,
                    original_filename=file_obj.filename,
                    file_path=str(file_path),
                    file_size=len(content),
                    mime_type=file_obj.content_type or 'application/octet-stream',
                    checksum=checksum,
                    uploaded_by=uploaded_by,
                    solution_name=self.solution_name
                )

                db.add(attachment)
                await db.commit()
                await db.refresh(attachment)

                return {
                    'success': True,
                    'attachment': attachment
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'File upload failed: {str(e)}'
            }

    async def _add_document_tags(
        self,
        db: AsyncSession,
        document: DMSDocument,
        tag_ids: List[int]
    ):
        """Add tags to document"""
        for tag_id in tag_ids:
            tag = await db.query(DMSDocumentTag).filter(
                and_(
                    DMSDocumentTag.id == tag_id,
                    DMSDocumentTag.is_active == True
                )
            ).first()
            if tag:
                document.tags.append(tag)

    async def _create_approval_workflow(
        self,
        db: AsyncSession,
        document: DMSDocument,
        created_by: str
    ):
        """Create approval workflow for document"""
        # Create workflow
        workflow = DMSDocumentWorkflow(
            document_id=document.id,
            workflow_type='approval',
            current_step='draft',
            status='active',
            created_by=created_by,
            solution_name=self.solution_name
        )

        db.add(workflow)
        await db.flush()  # Get workflow ID

        # Create approval steps (simplified - in real implementation, this would be configurable)
        approval_step = DMSDocumentApproval(
            workflow_id=workflow.id,
            step_name='Document Review',
            step_order=1,
            assigned_to=created_by,  # In real implementation, this would be assigned to reviewers
            status='pending',
            is_required=True
        )

        db.add(approval_step)

        # Update document state
        document.state = DocumentState.PENDING

    async def _check_document_access(
        self,
        db: AsyncSession,
        document: DMSDocument,
        user_id: str
    ) -> bool:
        """Check if user has access to document"""
        # Simplified access control - in real implementation, this would check permissions
        return True

    async def _can_edit_document(
        self,
        db: AsyncSession,
        document: DMSDocument,
        user_id: str
    ) -> bool:
        """Check if user can edit document"""
        # Can edit if user created it and it's in draft state
        return document.created_by == user_id and document.state == DocumentState.DRAFT

    async def _can_delete_document(
        self,
        db: AsyncSession,
        document: DMSDocument,
        user_id: str
    ) -> bool:
        """Check if user can delete document"""
        # Can delete if user created it and it's in draft state
        return document.created_by == user_id and document.state == DocumentState.DRAFT

    async def _serialize_document(self, document: DMSDocument) -> Dict[str, Any]:
        """Serialize document for API response"""
        return {
            'id': document.id,
            'name': document.name,
            'title': document.title,
            'state': document.state.value,
            'document_type': {
                'id': document.document_type.id,
                'name': document.document_type.name,
                'code': document.document_type.code
            } if document.document_type else None,
            'category': {
                'id': document.category.id,
                'name': document.category.name
            } if document.category else None,
            'tags': [{'id': tag.id, 'name': tag.name} for tag in document.tags],
            'created_by': document.created_by,
            'approved_by': document.approved_by,
            'confidentiality_level': document.confidentiality_level.value,
            'description': document.description,
            'expiry_date': document.expiry_date.isoformat() if document.expiry_date else None,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat(),
            'approved_at': document.approved_at.isoformat() if document.approved_at else None,
            'download_url': document.get_download_url()
        }

