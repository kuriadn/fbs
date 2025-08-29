"""
FBS DMS Workflow Service

Core business logic for document approval workflows.
"""

import logging
from typing import Dict, Any, List, Optional
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q, QuerySet
from django.conf import settings

from ..models import DMSDocument, DMSDocumentWorkflow, DMSDocumentApproval

logger = logging.getLogger('fbs_dms')


class WorkflowService:
    """Service for workflow management"""
    
    def __init__(self, company_id: str):
        self.company_id = company_id
    
    def start_document_workflow(self, document: DMSDocument, user: User) -> DMSDocumentWorkflow:
        """Start approval workflow for a document"""
        try:
            with transaction.atomic():
                # Check if document already has a workflow
                if hasattr(document, 'workflow') and document.workflow:
                    raise ValidationError("Document already has a workflow")
                
                # Create workflow
                workflow = DMSDocumentWorkflow.objects.create(
                    document=document,
                    status='active',
                    workflow_data={
                        'started_by': user.username,
                        'started_at': timezone.now().isoformat()
                    }
                )
                
                # Create approval steps if required
                if document.document_type.requires_approval:
                    self._create_approval_steps(workflow, document, user)
                
                # Update document state
                if document.document_type.requires_approval:
                    document.state = 'pending'
                    document.save()
                
                logger.info(f"Workflow started for document: {document.name}")
                return workflow
                
        except Exception as e:
            logger.error(f"Failed to start workflow: {str(e)}")
            raise
    
    def approve_step(self, approval_id: int, user: User, comments: str = '') -> DMSDocumentApproval:
        """Approve a workflow step"""
        try:
            approval = self._get_approval(approval_id)
            if not approval:
                raise ValidationError("Approval step not found")
            
            # Check if user can approve
            if not self._can_approve_step(approval, user):
                raise ValidationError("Cannot approve this step")
            
            with transaction.atomic():
                # Approve the step
                approval.approve(comments)
                
                # Check if workflow is complete
                if self._is_workflow_complete(approval.workflow):
                    self._complete_workflow(approval.workflow, 'completed')
                    approval.workflow.document.state = 'approved'
                    approval.workflow.document.approved_by = user
                    approval.workflow.document.save()
                
                logger.info(f"Step approved: {approval.workflow.document.name} by {user.username}")
                return approval
                
        except Exception as e:
            logger.error(f"Failed to approve step: {str(e)}")
            raise
    
    def reject_step(self, approval_id: int, user: User, comments: str = '') -> DMSDocumentApproval:
        """Reject a workflow step"""
        try:
            approval = self._get_approval(approval_id)
            if not approval:
                raise ValidationError("Approval step not found")
            
            # Check if user can reject
            if not self._can_reject_step(approval, user):
                raise ValidationError("Cannot reject this step")
            
            with transaction.atomic():
                # Reject the step
                approval.reject(comments)
                
                # Mark workflow as failed
                self._complete_workflow(approval.workflow, 'failed')
                approval.workflow.document.state = 'rejected'
                approval.workflow.document.save()
                
                logger.info(f"Step rejected: {approval.workflow.document.name} by {user.username}")
                return approval
                
        except Exception as e:
            logger.error(f"Failed to reject step: {str(e)}")
            raise
    
    def skip_step(self, approval_id: int, user: User, comments: str = '') -> DocumentApproval:
        """Skip a workflow step"""
        try:
            approval = self._get_approval(approval_id)
            if not approval:
                raise ValidationError("Approval step not found")
            
            # Check if step can be skipped
            if not approval.can_skip():
                raise ValidationError("This step cannot be skipped")
            
            with transaction.atomic():
                # Skip the step
                approval.skip(comments)
                
                # Check if workflow is complete
                if self._is_workflow_complete(approval.workflow):
                    self._complete_workflow(approval.workflow, 'completed')
                    approval.workflow.document.state = 'approved'
                    approval.workflow.document.save()
                
                logger.info(f"Step skipped: {approval.workflow.document.name} by {user.username}")
                return approval
                
        except Exception as e:
            logger.error(f"Failed to skip step: {str(e)}")
            raise
    
    def get_workflow_status(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get workflow status for a document"""
        try:
            document = self._get_document(document_id)
            if not document or not hasattr(document, 'workflow'):
                return None
            
            workflow = document.workflow
            if not workflow:
                return None
            
            # Get approval steps
            approval_steps = workflow.approval_steps.all().order_by('sequence')
            
            return {
                'workflow_id': workflow.id,
                'status': workflow.status,
                'started_at': workflow.started_at.isoformat(),
                'completed_at': workflow.completed_at.isoformat() if workflow.completed_at else None,
                'current_step': workflow.current_step.id if workflow.current_step else None,
                'steps': [
                    {
                        'id': step.id,
                        'sequence': step.sequence,
                        'approver': step.approver.username,
                        'status': step.status,
                        'required': step.required,
                        'comments': step.comments,
                        'approved_at': step.approved_at.isoformat() if step.approved_at else None,
                        'rejected_at': step.rejected_at.isoformat() if step.rejected_at else None
                    }
                    for step in approval_steps
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            return None
    
    def get_pending_approvals(self, user: User) -> QuerySet[DMSDocumentApproval]:
        """Get pending approvals for a user"""
        try:
            return DMSDocumentApproval.objects.filter(
                workflow__document__company_id=self.company_id,
                approver=user,
                status='pending'
            ).order_by('workflow__document__created_at')
            
        except Exception as e:
            logger.error(f"Failed to get pending approvals: {str(e)}")
            return DMSDocumentApproval.objects.none()
    
    def cancel_workflow(self, document_id: int, user: User) -> bool:
        """Cancel a workflow"""
        try:
            document = self._get_document(document_id)
            if not document:
                raise ValidationError("Document not found")
            
            if not hasattr(document, 'workflow') or not document.workflow:
                raise ValidationError("Document has no workflow")
            
            workflow = document.workflow
            
            # Check if user can cancel workflow
            if not self._can_cancel_workflow(workflow, user):
                raise ValidationError("Cannot cancel workflow")
            
            with transaction.atomic():
                # Cancel workflow
                self._complete_workflow(workflow, 'cancelled')
                
                # Reset document state
                document.state = 'draft'
                document.save()
                
                logger.info(f"Workflow cancelled: {document.name} by {user.username}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to cancel workflow: {str(e)}")
            raise
    
    def _create_approval_steps(self, workflow: DMSDocumentWorkflow, document: DMSDocument, user: User):
        """Create approval steps for workflow"""
        # For now, create a simple single-step approval
        # In a real implementation, this could be configurable
        DMSDocumentApproval.objects.create(
            workflow=workflow,
            approver=user,  # For now, creator is also approver
            sequence=1,
            status='pending',
            required=True
        )
        
        # Set current step
        workflow.current_step = workflow.approval_steps.first()
        workflow.save()
    
    def _is_workflow_complete(self, workflow: DMSDocumentWorkflow) -> bool:
        """Check if workflow is complete"""
        # Check if all required steps are approved
        required_steps = workflow.approval_steps.filter(required=True)
        approved_steps = required_steps.filter(status='approved')
        
        return required_steps.count() == approved_steps.count()
    
    def _complete_workflow(self, workflow: DMSDocumentWorkflow, status: str):
        """Mark workflow as complete"""
        workflow.complete_workflow(status)
    
    def _get_document(self, document_id: int) -> Optional[DMSDocument]:
        """Get document by ID with company check"""
        try:
            return DMSDocument.objects.get(
                id=document_id,
                company_id=self.company_id
            )
        except DMSDocument.DoesNotExist:
            return None
    
    def _get_approval(self, approval_id: int) -> Optional[DMSDocumentApproval]:
        """Get approval step by ID with company check"""
        try:
            return DMSDocumentApproval.objects.get(
                id=approval_id,
                workflow__document__company_id=self.company_id
            )
        except DMSDocumentApproval.DoesNotExist:
            return None
    
    def _can_approve_step(self, approval: DMSDocumentApproval, user: User) -> bool:
        """Check if user can approve step"""
        # Step approver can approve
        if approval.approver == user:
            return True
        
        # Staff users can approve
        if user.is_staff:
            return True
        
        return False
    
    def _can_reject_step(self, approval: DMSDocumentApproval, user: User) -> bool:
        """Check if user can reject step"""
        # Step approver can reject
        if approval.approver == user:
            return True
        
        # Staff users can reject
        if user.is_staff:
            return True
        
        return False
    
    def _can_cancel_workflow(self, workflow: DMSDocumentWorkflow, user: User) -> bool:
        """Check if user can cancel workflow"""
        # Document creator can cancel
        if workflow.document.created_by == user:
            return True
        
        # Staff users can cancel
        if user.is_staff:
            return True
        
        return False
