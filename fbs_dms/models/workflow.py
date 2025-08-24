"""
FBS DMS Workflow Models

Document workflow and approval management models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DocumentWorkflow(models.Model):
    """Document workflow instance"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    document = models.OneToOneField(
        'Document',
        on_delete=models.CASCADE,
        related_name='workflow'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_step = models.ForeignKey(
        'DocumentApproval',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_workflow'
    )
    workflow_data = models.JSONField(default=dict, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        app_label = 'fbs_dms'
        db_table = 'fbs_dms_document_workflow'
        verbose_name = 'Document Workflow'
        verbose_name_plural = 'Document Workflows'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Workflow for {self.document.name}"
    
    def is_completed(self):
        """Check if workflow is completed"""
        return self.status == 'completed'
    
    def is_active(self):
        """Check if workflow is active"""
        return self.status == 'active'
    
    def complete_workflow(self, status='completed'):
        """Mark workflow as completed"""
        self.status = status
        self.completed_at = timezone.now()
        self.save()
    
    def get_next_approval_step(self):
        """Get the next approval step"""
        if not self.current_step:
            return None
        
        # Get next step in sequence
        next_step = DocumentApproval.objects.filter(
            workflow=self,
            sequence__gt=self.current_step.sequence
        ).order_by('sequence').first()
        
        return next_step


class DocumentApproval(models.Model):
    """Document approval step"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('skipped', 'Skipped'),
    ]
    
    workflow = models.ForeignKey(
        DocumentWorkflow,
        on_delete=models.CASCADE,
        related_name='approval_steps'
    )
    approver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_approvals'
    )
    sequence = models.IntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    required = models.BooleanField(default=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_dms'
        db_table = 'fbs_dms_document_approval'
        verbose_name = 'Document Approval'
        verbose_name_plural = 'Document Approvals'
        ordering = ['sequence']
        unique_together = ['workflow', 'sequence']
    
    def __str__(self):
        return f"Approval {self.sequence} for {self.workflow.document.name}"
    
    def approve(self, comments=''):
        """Approve this step"""
        self.status = 'approved'
        self.approved_at = timezone.now()
        self.comments = comments
        self.save()
        
        # Update workflow current step
        self.workflow.current_step = self
        self.workflow.save()
    
    def reject(self, comments=''):
        """Reject this step"""
        self.status = 'rejected'
        self.rejected_at = timezone.now()
        self.comments = comments
        self.save()
        
        # Mark workflow as failed
        self.workflow.complete_workflow('failed')
    
    def skip(self, comments=''):
        """Skip this step"""
        self.status = 'skipped'
        self.comments = comments
        self.save()
        
        # Move to next step
        next_step = self.workflow.get_next_approval_step()
        if next_step:
            self.workflow.current_step = next_step
            self.workflow.save()
        else:
            # No more steps, workflow is complete
            self.workflow.complete_workflow()
    
    def is_pending(self):
        """Check if step is pending"""
        return self.status == 'pending'
    
    def is_approved(self):
        """Check if step is approved"""
        return self.status == 'approved'
    
    def is_rejected(self):
        """Check if step is rejected"""
        return self.status == 'rejected'
    
    def can_approve(self):
        """Check if step can be approved"""
        return self.is_pending() and self.required
    
    def can_reject(self):
        """Check if step can be rejected"""
        return self.is_pending() and self.required
    
    def can_skip(self):
        """Check if step can be skipped"""
        return self.is_pending() and not self.required
