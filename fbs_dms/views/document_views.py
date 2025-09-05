"""
FBS DMS Document Views

REST API views for document management following DRY and KISS principles.
"""

import logging
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
import json

from ..models import DMSDocument, DMSDocumentType, DMSDocumentCategory, DMSDocumentTag
from ..services.document_service import DocumentService
from ..services.file_service import FileService

logger = logging.getLogger('fbs_dms')


@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required
def document_list(request):
    """List documents or create new document"""
    
    company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
    
    if request.method == 'GET':
        return _get_document_list(request, company_id)
    elif request.method == 'POST':
        return _create_document(request, company_id)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
@login_required
def document_detail(request, document_id):
    """Get, update, or delete a specific document"""
    
    company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
    
    if request.method == 'GET':
        return _get_document_detail(request, document_id, company_id)
    elif request.method == 'PUT':
        return _update_document(request, document_id, company_id)
    elif request.method == 'DELETE':
        return _delete_document(request, document_id, company_id)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def document_approve(request, document_id):
    """Approve a document"""
    company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
    return _approve_document(request, document_id, company_id)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def document_reject(request, document_id):
    """Reject a document"""
    company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
    return _reject_document(request, document_id, company_id)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def document_types(request):
    """Get available document types"""
    company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
    return _get_document_types(request, company_id)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def document_categories(request):
    """Get available document categories"""
    company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
    return _get_document_categories(request, company_id)


def _get_document_list(request, company_id: str):
    """Get list of documents with optional filtering"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        limit = min(int(request.GET.get('limit', 50)), 100)
        document_type = request.GET.get('document_type')
        category = request.GET.get('category')
        state = request.GET.get('state')
        search = request.GET.get('search')
        
        # Initialize service
        service = DocumentService(company_id)
        
        # Get documents
        documents = service.get_documents(
            document_type=document_type,
            category=category,
            state=state,
            search=search,
            limit=limit
        )
        
        # Prepare response data
        document_data = []
        for doc in documents:
            document_data.append({
                'id': doc.id,
                'name': doc.name,
                'title': doc.title,
                'state': doc.state,
                'document_type': doc.document_type.name if doc.document_type else None,
                'category': doc.category.name if doc.category else None,
                'created_by': doc.created_by.username,
                'created_at': doc.created_at.isoformat(),
                'expiry_date': doc.expiry_date.isoformat() if doc.expiry_date else None,
                'has_attachment': bool(doc.attachment)
            })
        
        return JsonResponse({
            'success': True,
            'data': document_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': len(document_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to get document list: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _create_document(request, company_id: str):
    """Create a new document"""
    try:
        # Parse request data
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'title', 'document_type_id']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)
        
        # Initialize service
        service = DocumentService(company_id)
        
        # Create document
        document = service.create_document(
            name=data['name'],
            title=data['title'],
            document_type_id=data['document_type_id'],
            category_id=data.get('category_id'),
            description=data.get('description'),
            expiry_date=data.get('expiry_date'),
            confidentiality_level=data.get('confidentiality_level', 'internal'),
            metadata=data.get('metadata', {}),
            created_by=request.user
        )
        
        # Handle file attachment if provided
        if 'file' in request.FILES:
            file_service = FileService(company_id)
            attachment = file_service.upload_file(
                request.FILES['file'],
                request.user
            )
            document.attachment = attachment
            document.save()
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': document.id,
                'name': document.name,
                'title': document.title,
                'state': document.state
            }
        }, status=201)
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to create document: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _get_document_detail(request, document_id: int, company_id: str):
    """Get a specific document"""
    try:
        # Initialize service
        service = DocumentService(company_id)
        
        # Get document
        document = service.get_document(document_id)
        if not document:
            return JsonResponse({
                'success': False,
                'error': 'Document not found'
            }, status=404)
        
        # Prepare response data
        document_data = {
            'id': document.id,
            'name': document.name,
            'title': document.title,
            'description': document.description,
            'state': document.state,
            'document_type': {
                'id': document.document_type.id,
                'name': document.document_type.name
            } if document.document_type else None,
            'category': {
                'id': document.category.id,
                'name': document.category.name
            } if document.category else None,
            'tags': [{'id': tag.id, 'name': tag.name} for tag in document.tags.all()],
            'created_by': document.created_by.username,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat(),
            'expiry_date': document.expiry_date.isoformat() if document.expiry_date else None,
            'confidentiality_level': document.confidentiality_level,
            'metadata': document.metadata,
            'attachment': {
                'id': document.attachment.id,
                'filename': document.attachment.original_filename,
                'file_size_mb': document.attachment.get_file_size_mb()
            } if document.attachment else None
        }
        
        return JsonResponse({
            'success': True,
            'data': document_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get document detail: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _update_document(request, document_id: int, company_id: str):
    """Update a document"""
    try:
        # Parse request data
        data = json.loads(request.body)
        
        # Initialize service
        service = DocumentService(company_id)
        
        # Update document
        document = service.update_document(
            document_id=document_id,
            **data
        )
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': document.id,
                'name': document.name,
                'title': document.title,
                'state': document.state
            }
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to update document: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _delete_document(request, document_id: int, company_id: str):
    """Delete a document"""
    try:
        # Initialize service
        service = DocumentService(company_id)
        
        # Delete document
        service.delete_document(document_id, request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Document deleted successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _approve_document(request, document_id: int, company_id: str):
    """Approve a document"""
    try:
        # Parse request data
        data = json.loads(request.body)
        comments = data.get('comments', '')
        
        # Initialize service
        service = DocumentService(company_id)
        
        # Approve document
        document = service.approve_document(document_id, request.user, comments)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': document.id,
                'name': document.name,
                'state': document.state
            }
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to approve document: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _reject_document(request, document_id: int, company_id: str):
    """Reject a document"""
    try:
        # Parse request data
        data = json.loads(request.body)
        comments = data.get('comments', '')
        
        # Initialize service
        service = DocumentService(company_id)
        
        # Reject document
        document = service.reject_document(document_id, request.user, comments)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': document.id,
                'name': document.name,
                'state': document.state
            }
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to reject document: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _get_document_types(request, company_id: str):
    """Get available document types"""
    try:
        types = DMSDocumentType.objects.filter(company_id=company_id).order_by('name')
        
        type_data = [{
            'id': doc_type.id,
            'name': doc_type.name,
            'description': doc_type.description,
            'requires_approval': doc_type.requires_approval,
            'max_file_size': doc_type.max_file_size,
            'allowed_extensions': doc_type.allowed_extensions
        } for doc_type in types]
        
        return JsonResponse({
            'success': True,
            'data': type_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get document types: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _get_document_categories(request, company_id: str):
    """Get available document categories"""
    try:
        categories = DMSDocumentCategory.objects.filter(company_id=company_id).order_by('name')
        
        category_data = [{
            'id': category.id,
            'name': category.name,
            'description': category.description,
            'color': category.color
        } for category in categories]
        
        return JsonResponse({
            'success': True,
            'data': category_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get document categories: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
