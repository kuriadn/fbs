"""
FBS DMS Router - FastAPI

Document Management System API endpoints migrated from Django.
Provides complete document CRUD operations with workflow management.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_db_session_for_request, get_current_user
from ..services.dms_service import DocumentService

router = APIRouter(prefix="/api/dms", tags=["dms"])

# ============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/documents", response_model=Dict[str, Any])
async def create_document(
    name: str,
    title: str,
    document_type_id: int,
    category_id: int,
    file: Optional[UploadFile] = File(None),
    description: Optional[str] = None,
    confidentiality_level: Optional[str] = "internal",
    expiry_date: Optional[str] = None,
    tags: Optional[List[int]] = None,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Create a new document"""
    try:
        # Get solution name from request context or current user
        solution_name = current_user.get('solution_name', 'default')

        document_service = DocumentService(solution_name)

        document_data = {
            'name': name,
            'title': title,
            'document_type_id': document_type_id,
            'category_id': category_id,
            'description': description,
            'confidentiality_level': confidentiality_level,
            'expiry_date': expiry_date,
            'tags': tags or []
        }

        result = await document_service.create_document(
            document_data=document_data,
            created_by=current_user['user_id'],
            file_obj=file
        )

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create document'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=Dict[str, Any])
async def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    state: Optional[str] = None,
    document_type_id: Optional[int] = None,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """List documents with filtering and pagination"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        document_service = DocumentService(solution_name)

        filters = {}
        if state:
            filters['state'] = state
        if document_type_id:
            filters['document_type_id'] = document_type_id
        if category_id:
            filters['category_id'] = category_id
        if search:
            filters['search'] = search

        result = await document_service.list_documents(
            filters=filters,
            page=page,
            limit=limit
        )

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to list documents'))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}", response_model=Dict[str, Any])
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get document by ID"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        document_service = DocumentService(solution_name)

        result = await document_service.get_document(
            document_id=document_id,
            user_id=current_user['user_id']
        )

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result.get('error', 'Document not found'))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/documents/{document_id}", response_model=Dict[str, Any])
async def update_document(
    document_id: int,
    name: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    expiry_date: Optional[str] = None,
    tags: Optional[List[int]] = None,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Update document"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        document_service = DocumentService(solution_name)

        update_data = {}
        if name is not None:
            update_data['name'] = name
        if title is not None:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if expiry_date is not None:
            update_data['expiry_date'] = expiry_date
        if tags is not None:
            update_data['tags'] = tags

        result = await document_service.update_document(
            document_id=document_id,
            update_data=update_data,
            updated_by=current_user['user_id']
        )

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to update document'))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}", response_model=Dict[str, Any])
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Delete document (soft delete)"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        document_service = DocumentService(solution_name)

        result = await document_service.delete_document(
            document_id=document_id,
            deleted_by=current_user['user_id']
        )

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to delete document'))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/approve", response_model=Dict[str, Any])
async def approve_document(
    document_id: int,
    comments: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Approve document"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        document_service = DocumentService(solution_name)

        result = await document_service.approve_document(
            document_id=document_id,
            approved_by=current_user['user_id']
        )

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to approve document'))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documents/{document_id}/reject", response_model=Dict[str, Any])
async def reject_document(
    document_id: int,
    comments: str,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Reject document"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        document_service = DocumentService(solution_name)

        result = await document_service.reject_document(
            document_id=document_id,
            rejected_by=current_user['user_id'],
            comments=comments
        )

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to reject document'))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# FILE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/files/upload", response_model=Dict[str, Any])
async def upload_file(
    file: UploadFile = File(...),
    document_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Upload file"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        document_service = DocumentService(solution_name)

        # For now, just acknowledge upload - actual implementation would handle file storage
        return {
            'success': True,
            'filename': file.filename,
            'content_type': file.content_type,
            'file_size': 0,  # Would be calculated from actual upload
            'message': 'File upload endpoint ready'
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}/download")
async def download_file(
    file_id: int,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Download file"""
    try:
        # Placeholder for file download implementation
        raise HTTPException(status_code=501, detail="File download not yet implemented")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# METADATA ENDPOINTS
# ============================================================================

@router.get("/document-types", response_model=List[Dict[str, Any]])
async def list_document_types(
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """List document types"""
    try:
        from ..models.dms_models import DMSDocumentType

        solution_name = current_user.get('solution_name', 'default')

        async for db_session in get_db_session_for_request(None):
            types = await db_session.query(DMSDocumentType).filter(
                DMSDocumentType.is_active == True
            ).all()

            return [{
                'id': t.id,
                'name': t.name,
                'code': t.code,
                'description': t.description,
                'requires_approval': t.requires_approval,
                'allowed_extensions': t.allowed_extensions,
                'max_file_size': t.max_file_size
            } for t in types]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories", response_model=List[Dict[str, Any]])
async def list_categories(
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """List document categories"""
    try:
        from ..models.dms_models import DMSDocumentCategory

        solution_name = current_user.get('solution_name', 'default')

        async for db_session in get_db_session_for_request(None):
            categories = await db_session.query(DMSDocumentCategory).filter(
                DMSDocumentCategory.is_active == True
            ).all()

            return [{
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'parent_id': c.parent_id,
                'sequence': c.sequence
            } for c in categories]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tags", response_model=List[Dict[str, Any]])
async def list_tags(
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """List document tags"""
    try:
        from ..models.dms_models import DMSDocumentTag

        solution_name = current_user.get('solution_name', 'default')

        async for db_session in get_db_session_for_request(None):
            tags = await db_session.query(DMSDocumentTag).filter(
                DMSDocumentTag.is_active == True
            ).all()

            return [{
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'color': t.color
            } for t in tags]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=Dict[str, Any])
async def search_documents(
    query: str,
    document_type_id: Optional[int] = None,
    category_id: Optional[int] = None,
    state: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Search documents"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        document_service = DocumentService(solution_name)

        filters = {'search': query}
        if document_type_id:
            filters['document_type_id'] = document_type_id
        if category_id:
            filters['category_id'] = category_id
        if state:
            filters['state'] = state

        result = await document_service.list_documents(
            filters=filters,
            page=page,
            limit=limit
        )

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Search failed'))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

