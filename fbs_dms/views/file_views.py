"""
FBS DMS File Views

REST API views for file management following DRY and KISS principles.
"""

import logging
from typing import Dict, Any
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import json

from ..services.file_service import FileService

logger = logging.getLogger('fbs_dms')


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def file_upload(request):
    """Upload a file"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file provided'
            }, status=400)
        
        file_obj = request.FILES['file']
        original_filename = request.POST.get('original_filename')
        
        # Initialize service
        service = FileService(company_id)
        
        # Upload file
        attachment = service.upload_file(file_obj, request.user, original_filename)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': attachment.id,
                'filename': attachment.original_filename,
                'file_size_mb': attachment.get_file_size_mb(),
                'mime_type': attachment.mime_type
            }
        }, status=201)
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def file_download(request, file_id):
    """Download a file"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Initialize service
        service = FileService(company_id)
        
        # Get file for download
        attachment = service.download_file(file_id, request.user)
        if not attachment:
            return JsonResponse({
                'success': False,
                'error': 'File not found'
            }, status=404)
        
        # Return file response
        response = HttpResponse(attachment.file, content_type=attachment.mime_type)
        response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}"'
        return response
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to download file: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def file_delete(request, file_id):
    """Delete a file"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Initialize service
        service = FileService(company_id)
        
        # Delete file
        service.delete_file(file_id, request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'File deleted successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to delete file: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def file_info(request, file_id):
    """Get file information"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Initialize service
        service = FileService(company_id)
        
        # Get file info
        file_info = service.get_file_info(file_id)
        if not file_info:
            return JsonResponse({
                'success': False,
                'error': 'File not found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'data': file_info
        })
        
    except Exception as e:
        logger.error(f"Failed to get file info: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def file_validate(request):
    """Validate a file against document type"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file provided'
            }, status=400)
        
        file_obj = request.FILES['file']
        
        # Parse request data
        data = json.loads(request.body) if request.body else {}
        document_type_id = data.get('document_type_id')
        
        if not document_type_id:
            return JsonResponse({
                'success': False,
                'error': 'Document type ID required'
            }, status=400)
        
        # Initialize service
        service = FileService(company_id)
        
        # Get document type
        from ..models import DMSDocumentType
        try:
            document_type = DMSDocumentType.objects.get(id=document_type_id)
        except DMSDocumentType.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Invalid document type'
            }, status=400)
        
        # Validate file
        validation_result = service.validate_file_for_document_type(file_obj, document_type)
        
        return JsonResponse({
            'success': True,
            'data': validation_result
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to validate file: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
