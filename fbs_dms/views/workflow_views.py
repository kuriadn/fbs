"""
FBS DMS Workflow Views

REST API views for workflow management following DRY and KISS principles.
"""

import logging
from typing import Dict, Any
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
import json

from ..services.workflow_service import WorkflowService

logger = logging.getLogger('fbs_dms')


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def workflow_start(request, document_id):
    """Start a workflow for a document"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Initialize service
        service = WorkflowService(company_id)
        
        # Get document
        from ..models import Document
        try:
            document = Document.objects.get(id=document_id, company_id=company_id)
        except Document.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Document not found'
            }, status=404)
        
        # Start workflow
        workflow = service.start_document_workflow(document, request.user)
        
        return JsonResponse({
            'success': True,
            'data': {
                'workflow_id': workflow.id,
                'status': workflow.status,
                'document_id': document.id,
                'document_name': document.name
            }
        }, status=201)
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to start workflow: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def workflow_approve(request, approval_id):
    """Approve a workflow step"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Parse request data
        data = json.loads(request.body) if request.body else {}
        comments = data.get('comments', '')
        
        # Initialize service
        service = WorkflowService(company_id)
        
        # Approve step
        approval = service.approve_step(approval_id, request.user, comments)
        
        return JsonResponse({
            'success': True,
            'data': {
                'approval_id': approval.id,
                'status': approval.status,
                'workflow_id': approval.workflow.id,
                'document_name': approval.workflow.document.name
            }
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to approve workflow step: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def workflow_reject(request, approval_id):
    """Reject a workflow step"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Parse request data
        data = json.loads(request.body) if request.body else {}
        comments = data.get('comments', '')
        
        # Initialize service
        service = WorkflowService(company_id)
        
        # Reject step
        approval = service.reject_step(approval_id, request.user, comments)
        
        return JsonResponse({
            'success': True,
            'data': {
                'approval_id': approval.id,
                'status': approval.status,
                'workflow_id': approval.workflow.id,
                'document_name': approval.workflow.document.name
            }
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to reject workflow step: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def workflow_skip(request, approval_id):
    """Skip a workflow step"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Parse request data
        data = json.loads(request.body) if request.body else {}
        comments = data.get('comments', '')
        
        # Initialize service
        service = WorkflowService(company_id)
        
        # Skip step
        approval = service.skip_step(approval_id, request.user, comments)
        
        return JsonResponse({
            'success': True,
            'data': {
                'approval_id': approval.id,
                'status': approval.status,
                'workflow_id': approval.workflow.id,
                'document_name': approval.workflow.document.name
            }
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to skip workflow step: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def workflow_status(request, document_id):
    """Get workflow status for a document"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Initialize service
        service = WorkflowService(company_id)
        
        # Get workflow status
        workflow_status = service.get_workflow_status(document_id)
        
        if not workflow_status:
            return JsonResponse({
                'success': False,
                'error': 'No workflow found for document'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'data': workflow_status
        })
        
    except Exception as e:
        logger.error(f"Failed to get workflow status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
@login_required
def pending_approvals(request):
    """Get pending approvals for the current user"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Initialize service
        service = WorkflowService(company_id)
        
        # Get pending approvals
        approvals = service.get_pending_approvals(request.user)
        
        approval_data = []
        for approval in approvals:
            approval_data.append({
                'id': approval.id,
                'workflow_id': approval.workflow.id,
                'document_id': approval.workflow.document.id,
                'document_name': approval.workflow.document.name,
                'document_title': approval.workflow.document.title,
                'sequence': approval.sequence,
                'required': approval.required,
                'created_at': approval.workflow.document.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': approval_data
        })
        
    except Exception as e:
        logger.error(f"Failed to get pending approvals: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def workflow_cancel(request, document_id):
    """Cancel a workflow"""
    try:
        company_id = request.GET.get('company_id') or getattr(request.user, 'company_id', 'default')
        
        # Initialize service
        service = WorkflowService(company_id)
        
        # Cancel workflow
        service.cancel_workflow(document_id, request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Workflow cancelled successfully'
        })
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    except Exception as e:
        logger.error(f"Failed to cancel workflow: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
