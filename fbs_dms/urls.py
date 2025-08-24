"""
FBS DMS URL Configuration

URL patterns for document management REST API following DRY and KISS principles.
"""

from django.urls import path
from .views import (
    # Document views
    document_list,
    document_detail,
    document_approve,
    document_reject,
    document_types,
    document_categories,
    
    # File views
    file_upload,
    file_download,
    file_delete,
    file_info,
    file_validate,
    
    # Workflow views
    workflow_start,
    workflow_approve,
    workflow_reject,
    workflow_skip,
    workflow_status,
    pending_approvals,
    workflow_cancel,
    
    # Search views
    search_documents,
    search_suggestions,
    search_statistics
)

app_name = 'fbs_dms'

urlpatterns = [
    # Document management
    path('documents/', document_list, name='document_list'),
    path('documents/<int:document_id>/', document_detail, name='document_detail'),
    path('documents/<int:document_id>/approve/', document_approve, name='document_approve'),
    path('documents/<int:document_id>/reject/', document_reject, name='document_reject'),
    
    # Metadata
    path('document-types/', document_types, name='document_types'),
    path('document-categories/', document_categories, name='document_categories'),
    
    # File management
    path('files/upload/', file_upload, name='file_upload'),
    path('files/<int:file_id>/download/', file_download, name='file_download'),
    path('files/<int:file_id>/', file_delete, name='file_delete'),
    path('files/<int:file_id>/info/', file_info, name='file_info'),
    path('files/validate/', file_validate, name='file_validate'),
    
    # Workflow management
    path('workflows/<int:document_id>/start/', workflow_start, name='workflow_start'),
    path('workflows/approvals/<int:approval_id>/approve/', workflow_approve, name='workflow_approve'),
    path('workflows/approvals/<int:approval_id>/reject/', workflow_reject, name='workflow_reject'),
    path('workflows/approvals/<int:approval_id>/skip/', workflow_skip, name='workflow_skip'),
    path('workflows/<int:document_id>/status/', workflow_status, name='workflow_status'),
    path('workflows/pending-approvals/', pending_approvals, name='pending_approvals'),
    path('workflows/<int:document_id>/cancel/', workflow_cancel, name='workflow_cancel'),
    
    # Search
    path('search/', search_documents, name='search_documents'),
    path('search/suggestions/', search_suggestions, name='search_suggestions'),
    path('search/statistics/', search_statistics, name='search_statistics'),
]
