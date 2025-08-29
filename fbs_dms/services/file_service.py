"""
FBS DMS File Service

File handling and storage operations following DRY and KISS principles.
"""

import logging
import os
from typing import Dict, Any, Optional, BinaryIO
from django.core.files import File
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.auth.models import User

from ..models import DMSFileAttachment, DMSDocumentType

logger = logging.getLogger('fbs_dms')


class FileService:
    """Service for file operations"""
    
    def __init__(self, company_id: str):
        self.company_id = company_id
    
    def upload_file(
        self, 
        file_obj: File, 
        user: User, 
        original_filename: str = None
    ) -> DMSFileAttachment:
        """Upload a file and create attachment"""
        try:
            # Validate file
            self._validate_file(file_obj)
            
            # Create file attachment
            attachment = DMSFileAttachment.objects.create(
                file=file_obj,
                uploaded_by=user,
                company_id=self.company_id
            )
            
            logger.info(f"File uploaded: {attachment.original_filename} by {user.username}")
            return attachment
            
        except Exception as e:
            logger.error(f"Failed to upload file: {str(e)}")
            raise
    
    def download_file(self, file_id: int, user: User) -> Optional[DMSFileAttachment]:
        """Get file attachment for download"""
        try:
            attachment = self._get_file_attachment(file_id)
            if not attachment:
                return None
            
            # Check access permissions
            if not self._can_access_file(attachment, user):
                raise ValidationError("Access denied to file")
            
            return attachment
            
        except Exception as e:
            logger.error(f"Failed to get file for download: {str(e)}")
            raise
    
    def delete_file(self, file_id: int, user: User) -> bool:
        """Delete a file attachment"""
        try:
            attachment = self._get_file_attachment(file_id)
            if not attachment:
                raise ValidationError("File not found")
            
            # Check delete permissions
            if not self._can_delete_file(attachment, user):
                raise ValidationError("Cannot delete file")
            
            # Delete file
            attachment.delete()
            
            logger.info(f"File deleted: {attachment.original_filename} by {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            raise
    
    def validate_file_for_document_type(
        self, 
        file_obj: File, 
        document_type: DMSDocumentType
    ) -> Dict[str, Any]:
        """Validate file against document type requirements"""
        try:
            # Basic file validation
            self._validate_file(file_obj)
            
            # Check file extension
            filename = file_obj.name if hasattr(file_obj, 'name') else 'unknown'
            if not document_type.is_extension_allowed(filename):
                raise ValidationError(f"File extension not allowed for document type: {document_type.name}")
            
            # Check file size
            file_size_mb = file_obj.size / (1024 * 1024)
            if file_size_mb > document_type.max_file_size:
                raise ValidationError(f"File size exceeds limit: {file_size_mb:.1f}MB > {document_type.max_file_size}MB")
            
            return {
                'valid': True,
                'file_size_mb': file_size_mb,
                'extension': os.path.splitext(filename)[1].lower(),
                'mime_type': self._get_mime_type(filename)
            }
            
        except Exception as e:
            logger.error(f"File validation failed: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    def get_file_info(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            attachment = self._get_file_attachment(file_id)
            if not attachment:
                return None
            
            return {
                'id': attachment.id,
                'filename': attachment.original_filename,
                'file_size_mb': attachment.get_file_size_mb(),
                'file_size_kb': attachment.get_file_size_kb(),
                'mime_type': attachment.mime_type,
                'extension': attachment.get_file_extension(),
                'uploaded_by': attachment.uploaded_by.username,
                'uploaded_at': attachment.created_at.isoformat(),
                'checksum': attachment.checksum,
                'can_preview': attachment.can_generate_preview(),
                'is_image': attachment.is_image(),
                'is_pdf': attachment.is_pdf(),
                'is_office_document': attachment.is_office_document()
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info: {str(e)}")
            return None
    
    def _get_file_attachment(self, file_id: int) -> Optional[FileAttachment]:
        """Get file attachment by ID with company check"""
        try:
            return DMSFileAttachment.objects.get(
                id=file_id,
                company_id=self.company_id
            )
        except DMSFileAttachment.DoesNotExist:
            return None
    
    def _validate_file(self, file_obj: File):
        """Basic file validation"""
        if not file_obj:
            raise ValidationError("No file provided")
        
        if not hasattr(file_obj, 'size') or file_obj.size <= 0:
            raise ValidationError("Invalid file size")
        
        # Check against global file size limit
        max_size_mb = getattr(settings, 'FBS_DMS_MAX_FILE_SIZE', 100)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_obj.size > max_size_bytes:
            raise ValidationError(f"File size exceeds global limit: {max_size_mb}MB")
    
    def _can_access_file(self, attachment: FileAttachment, user: User) -> bool:
        """Check if user can access file"""
        # File owner can always access
        if attachment.uploaded_by == user:
            return True
        
        # Public files can be accessed by anyone
        if attachment.is_public:
            return True
        
        # Staff users can access all files
        if user.is_staff:
            return True
        
        # Check if user has access through document ownership
        if hasattr(attachment, 'documents'):
            for document in attachment.documents.all():
                if document.created_by == user:
                    return True
        
        return False
    
    def _can_delete_file(self, attachment: FileAttachment, user: User) -> bool:
        """Check if user can delete file"""
        # File owner can delete
        if attachment.uploaded_by == user:
            return True
        
        # Staff users can delete
        if user.is_staff:
            return True
        
        return False
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename"""
        if not filename:
            return 'application/octet-stream'
        
        ext = os.path.splitext(filename)[1].lower()
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
