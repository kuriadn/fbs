"""
FBS DMS Admin Configuration

Django admin interface configuration for the DMS app.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    DMSDocument, DMSDocumentType, DMSDocumentCategory, DMSDocumentTag,
    DMSFileAttachment, DMSDocumentWorkflow, DMSDocumentApproval
)


@admin.register(DMSDocumentType)
class DMSDocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'requires_approval', 'max_file_size', 'is_active', 'created_at']
    list_filter = ['requires_approval', 'is_active', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'is_active')
        }),
        ('File Configuration', {
            'fields': ('allowed_extensions', 'max_file_size')
        }),
        ('Workflow', {
            'fields': ('requires_approval',)
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(DMSDocumentCategory)
class DMSDocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'sequence', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name']
    ordering = ['sequence', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'parent', 'sequence', 'is_active')
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(DMSDocumentTag)
class DMSDocumentTagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'color', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    
    def colored_name(self, obj):
        """Display tag name with color"""
        colors = {
            1: 'red', 2: 'blue', 3: 'green', 4: 'orange', 5: 'purple',
            6: 'pink', 7: 'brown', 8: 'gray', 9: 'black', 10: 'cyan',
            11: 'magenta', 12: 'yellow'
        }
        color = colors.get(obj.color, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.name
        )
    
    colored_name.short_description = 'Tag Name'


@admin.register(DMSFileAttachment)
class DMSFileAttachmentAdmin(admin.ModelAdmin):
    list_display = [
        'original_filename', 'file_size_mb', 'mime_type', 
        'uploaded_by', 'company_id', 'created_at'
    ]
    list_filter = ['mime_type', 'company_id', 'created_at']
    search_fields = ['original_filename', 'uploaded_by__username']
    readonly_fields = [
        'file_size', 'mime_type', 'checksum', 'created_at', 'updated_at'
    ]
    ordering = ['-created_at']
    
    def file_size_mb(self, obj):
        """Display file size in MB"""
        return f"{obj.get_file_size_mb():.1f} MB"
    
    file_size_mb.short_description = 'File Size'
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'original_filename', 'file_size', 'mime_type')
        }),
        ('Metadata', {
            'fields': ('checksum', 'is_public')
        }),
        ('Ownership', {
            'fields': ('uploaded_by', 'company_id')
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(DMSDocument)
class DMSDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'title', 'document_type', 'category', 'state', 
        'created_by', 'company_id', 'created_at'
    ]
    list_filter = [
        'state', 'document_type', 'category', 'confidentiality_level',
        'company_id', 'created_at'
    ]
    search_fields = ['name', 'title', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'title', 'description')
        }),
        ('Classification', {
            'fields': ('document_type', 'category', 'tags', 'confidentiality_level')
        }),
        ('File', {
            'fields': ('attachment',)
        }),
        ('Workflow', {
            'fields': ('state', 'created_by', 'approved_by')
        }),
        ('Business Rules', {
            'fields': ('expiry_date', 'company_id')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        })
    )
    
    def get_queryset(self, request):
        """Filter by company if user has company restriction"""
        qs = super().get_queryset(request)
        if hasattr(request.user, 'company_id') and request.user.company_id:
            qs = qs.filter(company_id=request.user.company_id)
        return qs


@admin.register(DMSDocumentWorkflow)
class DMSDocumentWorkflowAdmin(admin.ModelAdmin):
    list_display = [
        'document_name', 'status', 'current_step', 'started_at', 'completed_at'
    ]
    list_filter = ['status', 'started_at', 'completed_at']
    search_fields = ['document__name', 'document__title']
    readonly_fields = ['started_at', 'completed_at']
    ordering = ['-started_at']
    
    def document_name(self, obj):
        """Display document name"""
        return obj.document.name if obj.document else 'N/A'
    
    document_name.short_description = 'Document'
    
    fieldsets = (
        ('Workflow Information', {
            'fields': ('document', 'status', 'current_step')
        }),
        ('Workflow Data', {
            'fields': ('workflow_data', 'notes')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at')
        })
    )


@admin.register(DMSDocumentApproval)
class DMSDocumentApprovalAdmin(admin.ModelAdmin):
    list_display = [
        'workflow_document', 'sequence', 'approver', 'status', 
        'required', 'created_at'
    ]
    list_filter = ['status', 'required', 'sequence', 'created_at']
    search_fields = ['workflow__document__name', 'approver__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['workflow', 'sequence']
    
    def workflow_document(self, obj):
        """Display workflow document name"""
        if obj.workflow and obj.workflow.document:
            return obj.workflow.document.name
        return 'N/A'
    
    workflow_document.short_description = 'Document'
    
    fieldsets = (
        ('Approval Information', {
            'fields': ('workflow', 'sequence', 'approver', 'required')
        }),
        ('Status', {
            'fields': ('status', 'approved_at', 'rejected_at')
        }),
        ('Comments', {
            'fields': ('comments',)
        }),
        ('Timing', {
            'fields': ('created_at', 'updated_at')
        })
    )
