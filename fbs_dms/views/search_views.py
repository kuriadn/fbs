"""
FBS DMS Search Views

REST API views for document search following DRY and KISS principles.
"""

import logging
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json

from ..services.search_service import SearchService

logger = logging.getLogger('fbs_dms')


@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required
def search_documents(request):
    """Search documents with various criteria"""
    
    company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
    
    if request.method == 'GET':
        return _search_documents_get(request, company_id)
    elif request.method == 'POST':
        return _search_documents_post(request, company_id)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def search_suggestions(request):
    """Get search suggestions"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        query = request.GET.get('query', '')
        limit = min(int(request.GET.get('limit', 10)), 20)
        
        if not query:
            return JsonResponse({
                'success': True,
                'data': []
            })
        
        # Initialize service
        service = SearchService(company_id)
        
        # Get suggestions
        suggestions = service.get_search_suggestions(query, limit)
        
        return JsonResponse({
            'success': True,
            'data': suggestions
        })
        
    except Exception as e:
        logger.error(f"Failed to get search suggestions: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def search_statistics(request):
    """Get search statistics"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Initialize service
        service = SearchService(company_id)
        
        # Get statistics
        stats = service.get_search_statistics()
        
        return JsonResponse({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Failed to get search statistics: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _search_documents_get(request, company_id: str):
    """Search documents using GET parameters"""
    try:
        # Get query parameters
        query = request.GET.get('query', '')
        document_type = request.GET.get('document_type')
        category = request.GET.get('category')
        state = request.GET.get('state')
        search_type = request.GET.get('search_type', 'full_text')
        limit = min(int(request.GET.get('limit', 50)), 100)
        
        # Initialize service
        service = SearchService(company_id)
        
        # Perform search based on type
        if search_type == 'metadata':
            filters = {}
            if document_type:
                filters['document_type'] = document_type
            if category:
                filters['category'] = category
            if state:
                filters['state'] = state
            
            documents = service.search_by_metadata(filters, limit)
        elif search_type == 'workflow':
            filters = {}
            if state:
                filters['workflow_status'] = state
            
            documents = service.search_by_workflow_status(filters, limit)
        else:
            # Full text search
            filters = {}
            if document_type:
                filters['document_type'] = document_type
            if category:
                filters['category'] = category
            if state:
                filters['state'] = state
            
            documents = service.full_text_search(query, filters, limit)
        
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
            'search_type': search_type,
            'query': query,
            'total': len(document_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to search documents: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def _search_documents_post(request, company_id: str):
    """Search documents using POST body"""
    try:
        # Parse request data
        data = json.loads(request.body)
        
        # Get search parameters
        search_type = data.get('search_type', 'advanced')
        limit = min(int(data.get('limit', 50)), 100)
        
        # Initialize service
        service = SearchService(company_id)
        
        # Perform search based on type
        if search_type == 'advanced':
            documents = service.advanced_search(data, limit)
        elif search_type == 'metadata':
            documents = service.search_by_metadata(data.get('metadata', {}), limit)
        elif search_type == 'workflow':
            documents = service.search_by_workflow_status(data.get('workflow', {}), limit)
        else:
            # Full text search
            query = data.get('query', '')
            filters = data.get('filters', {})
            documents = service.full_text_search(query, filters, limit)
        
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
                'has_attachment': bool(doc.attachment),
                'tags': [tag.name for tag in doc.tags.all()],
                'confidentiality_level': doc.confidentiality_level
            })
        
        return JsonResponse({
            'success': True,
            'data': document_data,
            'search_type': search_type,
            'total': len(document_data)
        })
        
    except Exception as e:
        logger.error(f"Failed to search documents: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
