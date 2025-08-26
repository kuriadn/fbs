"""
FBS DMS Document Models

Core document management models following the DMS specifications.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import json


class DocumentType(models.Model):
    """Document type configuration"""
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, help_text='Description of this document type')
    requires_approval = models.BooleanField(default=False)
    allowed_extensions = models.CharField(
        max_length=500, 
        default='pdf,doc,docx,xls,xlsx,jpg,png',
        help_text='Comma-separated list of allowed file extensions'
    )
    max_file_size = models.IntegerField(
        default=50,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text='Maximum file size in MB'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_dms'
        db_table = 'fbs_dms_document_type'
        verbose_name = 'Document Type'
        verbose_name_plural = 'Document Types'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_allowed_extensions_list(self):
        """Get allowed extensions as a list"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(',') if ext.strip()]
    
    def is_extension_allowed(self, filename):
        """Check if file extension is allowed"""
        if not filename:
            return False
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        return ext in self.get_allowed_extensions_list()


class DocumentCategory(models.Model):
    """Document category hierarchy"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, help_text='Description of this category')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    sequence = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_dms'
        db_table = 'fbs_dms_document_category'
        verbose_name = 'Document Category'
        verbose_name_plural = 'Document Categories'
        ordering = ['sequence', 'name']
        unique_together = ['name', 'parent']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class DocumentTag(models.Model):
    """Document tags for organization"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text='Description of this tag')
    color = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text='Tag color (1-12)'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'fbs_dms'
        db_table = 'fbs_dms_document_tag'
        verbose_name = 'Document Tag'
        verbose_name_plural = 'Document Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Document(models.Model):
    """Main document model"""
    
    STATE_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('archived', 'Archived'),
    ]
    
    CONFIDENTIALITY_CHOICES = [
        ('public', 'Public'),
        ('internal', 'Internal'),
        ('confidential', 'Confidential'),
    ]
    
    name = models.CharField(max_length=255, help_text='Document reference')
    title = models.CharField(max_length=255, help_text='Document title')
    document_type = models.ForeignKey(
        DocumentType, 
        on_delete=models.CASCADE,
        related_name='documents'
    )
    category = models.ForeignKey(
        DocumentCategory, 
        on_delete=models.CASCADE,
        related_name='documents'
    )
    tags = models.ManyToManyField(
        DocumentTag, 
        blank=True,
        related_name='documents'
    )
    attachment = models.ForeignKey(
        'FileAttachment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default='draft'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='created_documents'
    )
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_documents'
    )
    expiry_date = models.DateField(null=True, blank=True)
    company_id = models.CharField(
        max_length=100,
        help_text='Multi-company support'
    )
    solution_db = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Solution-specific database for isolation (optional)'
    )
    confidentiality_level = models.CharField(
        max_length=20,
        choices=CONFIDENTIALITY_CHOICES,
        default='internal'
    )
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_dms'
        db_table = 'fbs_dms_document'
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company_id', 'state']),
            models.Index(fields=['company_id', 'created_at']),
            models.Index(fields=['created_by', 'created_at']),
            models.Index(fields=['document_type', 'category']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['solution_db', 'company_id']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.title}"
    
    def is_expired(self):
        """Check if document is expired"""
        if not self.expiry_date:
            return False
        return timezone.now().date() > self.expiry_date
    
    def can_be_approved(self):
        """Check if document can be approved"""
        return self.state == 'pending' and self.document_type.requires_approval
    
    def can_be_rejected(self):
        """Check if document can be rejected"""
        return self.state == 'pending' and self.document_type.requires_approval
    
    def get_file_size(self):
        """Get document file size in MB"""
        if self.attachment:
            return self.attachment.file_size
        return 0
    
    def get_file_extension(self):
        """Get document file extension"""
        if self.attachment and self.attachment.file:
            filename = self.attachment.file.name
            return filename.split('.')[-1].lower() if '.' in filename else ''
        return ''
