# FBS DMS Integration Guide

## Overview

The **FBS DMS** (`fbs_dms`) is a Document Management System that provides document storage, workflow approvals, and Odoo integration through the FBS app.

## Installation

```python
# settings.py
INSTALLED_APPS = [
    'fbs_dms',
]

FBS_DMS = {
    'UPLOAD_PATH': 'documents/',
    'MAX_FILE_SIZE': 10485760,  # 10MB
    'ALLOWED_EXTENSIONS': ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
    'ENABLE_VERSIONING': True,
    'ENABLE_WORKFLOWS': True,
}
```

## Core Usage

```python
from fbs_dms.services import DocumentService, FileService, WorkflowService
from fbs_dms.models import Document, DocumentType, DocumentCategory

# Initialize services with company context
doc_service = DocumentService(company_id='your_company_id')
file_service = FileService(company_id='your_company_id')
workflow_service = WorkflowService(company_id='your_company_id')
```

## Document Management

### Create Documents

```python
# Create document
document_data = {
    'name': 'Business Plan 2025',
    'title': 'Strategic Business Plan',
    'document_type_id': doc_type.id,
    'category_id': category.id,
    'description': 'Annual business strategy document',
    'confidentiality_level': 'internal',
    'metadata': {'department': 'Strategy', 'priority': 'high'}
}

document = doc_service.create_document(document_data, user, file_obj)
```

### Document Operations

```python
# Get document
doc = doc_service.get_document(document_id=123)

# Update document
update_result = doc_service.update_document(
    document_id=123,
    update_data={'description': 'Updated description'},
    user=user
)

# Delete document
delete_result = doc_service.delete_document(document_id=123, user=user)

# List documents
documents = doc_service.list_documents(
    filters={'category': 'Strategy'},
    ordering='-created_at',
    limit=50
)
```

### Document Search

```python
# Search documents
results = doc_service.search_documents(
    query='business plan',
    filters={'category': 'Strategy', 'status': 'active'},
    limit=50
)
```

## File Management

### File Upload

```python
# Upload file
attachment = file_service.upload_file(file_obj, user)

# Download file
download_result = file_service.download_file(attachment.id)

# Delete file
delete_result = file_service.delete_file(attachment.id)
```

### File Validation

```python
# Check file type
is_valid = file_service.validate_file_type(file_obj)

# Check file size
size_ok = file_service.validate_file_size(file_obj)

# Get file metadata
metadata = file_service.get_file_metadata(file_obj)
```

## Workflow Management

### Document Workflows

```python
# Create document workflow
workflow_data = {
    'document': document,
    'workflow_type': 'approval',
    'steps': ['submit', 'review', 'approve'],
    'approvers': [manager1.id, manager2.id]
}

workflow = workflow_service.create_workflow(workflow_data)

# Get workflow status
status = workflow_service.get_workflow_status(workflow.id)

# Execute workflow step
step_result = workflow_service.execute_workflow_step(
    workflow_id=workflow.id,
    step_name='review',
    step_data={'approved': True, 'comments': 'Looks good'}
)
```

### Approval Management

```python
# Create approval request
approval_data = {
    'document': document,
    'request_type': 'document_approval',
    'title': 'Approve Business Plan',
    'description': 'Please review and approve the business plan',
    'approvers': [manager1.id, manager2.id],
    'due_date': '2024-02-01'
}

approval = workflow_service.create_approval_request(approval_data)

# Get approval status
approval_status = workflow_service.get_approval_status(approval.id)

# Respond to approval
response = workflow_service.respond_to_approval(
    approval_id=approval.id,
    response='approve',
    comments='Plan looks comprehensive and well-thought-out'
)
```

## Document Types and Categories

### Create Document Types

```python
# Create document type
doc_type = DocumentType.objects.create(
    name='Business Plan',
    description='Strategic business planning documents',
    requires_approval=True,
    max_file_size=10485760,
    allowed_extensions=['.pdf', '.doc', '.docx']
)

# Create document category
category = DocumentCategory.objects.create(
    name='Strategy',
    description='Strategic planning documents',
    parent=None
)
```

### Document Tagging

```python
# Create document tag
tag = DocumentTag.objects.create(
    name='High Priority',
    description='High priority documents',
    color='#ff0000',
    is_active=True
)

# Add tags to document
document.tags.add(tag)
```

## Odoo Integration

### Sync with Odoo

```python
# Sync document to Odoo
sync_result = doc_service._sync_to_odoo(document, 'create')

# Get Odoo data format
odoo_data = doc_service._map_to_odoo_format(document)
```

### Odoo Data Mapping

```python
# Map document to Odoo format
odoo_format = {
    'name': document.name,
    'title': document.title,
    'description': document.description,
    'category_id': document.category.id,
    'tag_ids': [(6, 0, [tag.id for tag in document.tags.all()])],
    'metadata': document.metadata
}
```

## Search and Filtering

### Advanced Search

```python
# Search by multiple criteria
results = doc_service.search_documents(
    query='business plan',
    filters={
        'category': 'Strategy',
        'status': 'active',
        'created_by': user.id,
        'date_from': '2024-01-01',
        'date_to': '2024-01-31'
    }
)
```

### Search Service

```python
from fbs_dms.services import SearchService

search_service = SearchService(company_id='your_company_id')

# Full-text search
search_results = search_service.full_text_search(
    query='business strategy',
    filters={'category': 'Strategy'},
    limit=100
)

# Search by metadata
metadata_results = search_service.search_by_metadata(
    metadata={'department': 'Strategy', 'priority': 'high'}
)
```

## Security and Permissions

### Access Control

```python
# Check document access
can_access = doc_service._can_access_document(document, user)

# Check update permissions
can_update = doc_service._can_update_document(document, user)

# Check delete permissions
can_delete = doc_service._can_delete_document(document, user)
```

### Confidentiality Levels

```python
# Set confidentiality level
document.confidentiality_level = 'confidential'
document.save()

# Check access based on confidentiality
if document.confidentiality_level == 'confidential':
    # Only authorized users can access
    if not user.has_perm('fbs_dms.view_confidential_documents'):
        raise PermissionDenied
```

## Error Handling

```python
try:
    document = doc_service.create_document(document_data, user, file_obj)
    print(f"Document created: {document.name}")
except ValidationError as e:
    print(f"Validation error: {e}")
except PermissionDenied:
    print("Permission denied")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

### File Storage

- Use appropriate file storage backend (local, S3, etc.)
- Implement file compression for large documents
- Use CDN for frequently accessed files

### Database Optimization

- Index frequently searched fields
- Use select_related for foreign key relationships
- Implement pagination for large result sets

### Caching

- Cache document metadata
- Cache search results
- Cache workflow status

## Testing

```bash
# Run DMS tests
python -m pytest fbs_dms/tests/

# Run specific test categories
python -m pytest fbs_dms/tests/test_models.py
python -m pytest fbs_dms/tests/test_services.py
python -m pytest fbs_dms/tests/test_fbs_integration.py
```

## Troubleshooting

### Common Issues

1. **Missing company_id parameter**
   ```
   TypeError: DocumentService.__init__() missing 1 required positional argument: 'company_id'
   ```
   **Solution**: Always provide company_id when initializing services

2. **File upload errors**
   ```
   ValidationError: File type not allowed
   ```
   **Solution**: Check allowed file extensions in FBS_DMS settings

3. **Permission errors**
   ```
   PermissionDenied: You do not have permission to access this document
   ```
   **Solution**: Check user permissions and document confidentiality level
