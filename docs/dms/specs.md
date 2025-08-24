# DMS Backend Implementation Specs

## Core Models

### fayvad.document
- `name` (Char): Document reference  
- `title` (Char): Document title
- `document_type_id` (Many2one): Link to type
- `document_category_id` (Many2one): Link to category  
- `tag_ids` (Many2many): Document tags
- `attachment_id` (Many2one): File attachment
- `state` (Selection): draft, pending, approved, rejected, archived
- `created_by` (Many2one): Creator user
- `approved_by` (Many2one): Approver user
- `expiry_date` (Date): Document expiry
- `company_id` (Many2one): Multi-company support
- `confidentiality_level` (Selection): public, internal, confidential

### fayvad.document.type  
- `name` (Char): Type name
- `code` (Char): Unique code
- `requires_approval` (Boolean): Needs approval workflow
- `allowed_extensions` (Char): csv of file extensions
- `max_file_size` (Integer): Max size in MB

### fayvad.document.category
- `name` (Char): Category name
- `parent_id` (Many2one): Parent category
- `sequence` (Integer): Display order

### fayvad.document.tag
- `name` (Char): Tag name
- `color` (Integer): Display color

## API Endpoints

### Documents
```
GET    /api/v1/documents           # List documents
POST   /api/v1/documents           # Create document  
GET    /api/v1/documents/{id}      # Get document
PUT    /api/v1/documents/{id}      # Update document
DELETE /api/v1/documents/{id}      # Delete document
POST   /api/v1/documents/{id}/approve    # Approve
POST   /api/v1/documents/{id}/reject     # Reject
```

### Files
```
POST   /api/v1/files/upload        # Upload file
GET    /api/v1/files/{id}/download  # Download file
GET    /api/v1/files/{id}/preview   # Preview file
```

### Metadata
```
GET    /api/v1/document-types      # List types
GET    /api/v1/categories          # List categories
GET    /api/v1/tags               # List tags
GET    /api/v1/search             # Search documents
```

## Permissions (from CSV)

### Roles
- `group_document_user`: Read, Write, Create
- `group_document_reviewer`: Read, Write, Create + Approve/Reject
- `group_document_manager`: Full access + Delete
- `group_document_admin`: Full system access
- `group_portal_document_user`: Read only

### Model Access
- `model_fayvad_document`: Main document model
- `model_fayvad_document_type`: Type configuration  
- `model_fayvad_document_category`: Category management
- `model_fayvad_document_tag`: Tag management

## File Handling
- **Allowed Extensions**: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG
- **Max File Size**: 50MB default
- **Storage**: ir.attachment (Odoo standard)
- **Validation**: File type, size, virus scanning hooks

## Workflow Engine
- **States**: Draft → Pending → Approved/Rejected → Archived
- **Approvals**: Single approver workflow
- **Notifications**: Email on state changes
- **Bulk Operations**: Approve/reject multiple documents

## Search Features
- **Full-text Search**: PostgreSQL tsvector
- **Filters**: Type, category, date range, status, owner
- **Ordering**: Name, date, type, status

## Security
- **Authentication**: JWT tokens via FBS
- **Authorization**: Odoo groups and record rules
- **Multi-tenant**: Company-based data isolation
- **Audit Trail**: Track all document operations

## Performance Targets  
- Document list: < 500ms
- File upload: < 2s (10MB)
- Search: < 300ms
- File download: Immediate stream

## Database Schema
```sql
-- Core tables (Odoo managed)
fayvad_document
fayvad_document_type  
fayvad_document_category
fayvad_document_tag
ir_attachment (files)
ir_model_access (permissions)
```

## Integration Points

### FBS Integration
- **Model Registration**: Add to allowed_models.xml
- **Permission Mapping**: Map 5 DMS roles to 3 FBS roles
- **API Pattern**: Follow existing sales/hr controller patterns
- **Authentication**: Use FBS JWT middleware

### File Storage
- **Backend**: Local filesystem or S3-compatible
- **Preview**: Generate thumbnails for images/PDFs
- **Backup**: Automated file backup with retention

## Configuration
- **File Size Limits**: Per document type
- **Retention Policies**: Auto-archive after X days
- **Email Templates**: Approval notifications
- **Workflow Rules**: Approval requirements by type

## Error Handling
- **Upload Failures**: Retry mechanism, partial upload recovery
- **Storage Quota**: Prevent exceeding limits
- **File Corruption**: Checksum validation
- **Access Denied**: Clear error messages

## Monitoring
- **Health Check**: /api/v1/health endpoint
- **Usage Stats**: Storage, user activity, approval times
- **Error Rates**: Track API failures
- **Performance**: Response time monitoring