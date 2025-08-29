"""
FBS DMS File Attachment Models

File storage and attachment management models.
"""

import os
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import hashlib


class DMSFileAttachment(models.Model):
    """File attachment model for document storage"""
    
    file = models.FileField(
        upload_to='dms/documents/%Y/%m/%d/',
        help_text='Uploaded file'
    )
    original_filename = models.CharField(max_length=255)
    description = models.TextField(blank=True, help_text='Description of the file attachment')
    file_size = models.BigIntegerField(
        validators=[MinValueValidator(1)],
        help_text='File size in bytes'
    )
    mime_type = models.CharField(max_length=100)
    checksum = models.CharField(max_length=64, help_text='SHA-256 checksum')
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='uploaded_files'
    )
    company_id = models.CharField(max_length=100)
    solution_db = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Solution-specific database for isolation (optional)'
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'fbs_dms'
        db_table = 'dms_file_attachment'
        verbose_name = 'File Attachment'
        verbose_name_plural = 'File Attachments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company_id', 'created_at']),
            models.Index(fields=['company_id', 'solution_db']),
            models.Index(fields=['uploaded_by', 'created_at']),
            models.Index(fields=['mime_type']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.get_file_size_mb():.1f} MB)"
    
    def save(self, *args, **kwargs):
        """Override save to calculate file size and checksum"""
        if self.file and not self.pk:
            # New file being uploaded
            self.file_size = self.file.size
            self.original_filename = os.path.basename(self.file.name)
            self.mime_type = self._get_mime_type()
            self.checksum = self._calculate_checksum()
        
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to remove file from storage"""
        if self.file:
            # Remove file from storage
            if default_storage.exists(self.file.name):
                default_storage.delete(self.file.name)
        
        super().delete(*args, **kwargs)
    
    def get_file_size_mb(self):
        """Get file size in MB"""
        return self.file_size / (1024 * 1024)
    
    def get_file_size_kb(self):
        """Get file size in KB"""
        return self.file_size / 1024
    
    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.original_filename)[1].lower()
    
    def is_image(self):
        """Check if file is an image"""
        image_types = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
        return self.mime_type in image_types
    
    def is_pdf(self):
        """Check if file is a PDF"""
        return self.mime_type == 'application/pdf'
    
    def is_office_document(self):
        """Check if file is an Office document"""
        office_types = [
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        ]
        return self.mime_type in office_types
    
    def can_generate_preview(self):
        """Check if file can generate a preview"""
        return self.is_image() or self.is_pdf() or self.is_office_document()
    
    def _get_mime_type(self):
        """Get MIME type from file extension"""
        ext = self.get_file_extension()
        mime_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
        }
        return mime_map.get(ext, 'application/octet-stream')
    
    def _calculate_checksum(self):
        """Calculate SHA-256 checksum of file"""
        if not self.file:
            return ''
        
        sha256_hash = hashlib.sha256()
        try:
            for chunk in self.file.chunks():
                sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return ''
    
    def verify_checksum(self):
        """Verify file checksum integrity"""
        if not self.file or not self.checksum:
            return False
        
        current_checksum = self._calculate_checksum()
        return current_checksum == self.checksum
