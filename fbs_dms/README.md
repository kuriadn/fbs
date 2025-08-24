# 📄 FBS DMS - Document Management System

A standalone, embeddable document management solution for Django applications that provides enterprise-grade document storage, workflow management, and Odoo integration.

## ✨ Features

- **📁 Document Management**: Complete CRUD operations for documents
- **🏷️ Classification System**: Document types, categories, and tags
- **📋 Workflow Engine**: Approval workflows with multi-step processes
- **🔒 Security**: Role-based access control and confidentiality levels
- **🔍 Search**: Full-text search with advanced filtering
- **📊 Metadata**: Rich document metadata and version tracking
- **🔗 Odoo Integration**: Seamless integration with Odoo ERP
- **🏢 Multi-tenant**: Company-based data isolation
- **📱 Admin Interface**: Professional Django admin interface

## 🚀 Quick Start

### Installation

```bash
# Install the package
pip install fbs-dms

# Or install from source
git clone https://github.com/fayvad/fbs-dms.git
cd fbs-dms
pip install -e .
```

### Django Setup

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'fbs_dms.apps.FBSDMSConfig',
]

# DMS Configuration
FBS_DMS = {
    'MAX_FILE_SIZE': 50,  # MB
    'ALLOWED_EXTENSIONS': ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'png'],
    'STORAGE_BACKEND': 'local',  # or 's3'
    'ENABLE_PREVIEW': True,
}
```

### Basic Usage

```python
from fbs_dms.services import DocumentService

# Initialize service
dms_service = DocumentService('company_123')

# Create document
document_data = {
    'name': 'INV-001',
    'title': 'Invoice for Client ABC',
    'document_type_id': 1,
    'category_id': 1,
    'description': 'Monthly invoice for consulting services',
    'confidentiality_level': 'internal'
}

document = dms_service.create_document(document_data, user, file_obj)
print(f"Document created: {document.name}")

# Search documents
results = dms_service.search_documents('invoice', {'state': 'approved'})
for doc in results:
    print(f"Found: {doc.title}")

# Automatic Odoo Integration
# The document is automatically synced to Odoo through FBS app
# No additional code needed - it's handled transparently
```

## 🏗️ Architecture

### Core Models

1. **Document**: Main document entity with metadata
2. **DocumentType**: Document classification and rules
3. **DocumentCategory**: Hierarchical categorization
4. **DocumentTag**: Flexible tagging system
5. **FileAttachment**: File storage and metadata
6. **DocumentWorkflow**: Workflow instances
7. **DocumentApproval**: Approval steps and status

### Services

1. **DocumentService**: Core document operations
2. **FileService**: File handling and storage
3. **WorkflowService**: Workflow management
4. **SearchService**: Document search and filtering

## 📋 API Endpoints

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

## 🔐 Security & Permissions

### Roles
- **Document User**: Read, Write, Create
- **Document Reviewer**: Read, Write, Create + Approve/Reject
- **Document Manager**: Full access + Delete
- **Document Admin**: Full system access
- **Portal User**: Read only

### Confidentiality Levels
- **Public**: Accessible to all users
- **Internal**: Company-wide access
- **Confidential**: Restricted access

## 🔄 Workflow Engine

### Approval Workflow
1. **Draft**: Document created, editable
2. **Pending**: Submitted for approval
3. **Approved**: Approved by reviewers
4. **Rejected**: Rejected with comments
5. **Archived**: Completed or expired

### Multi-step Approval
- Sequential approval steps
- Required vs. optional approvals
- Skip non-required steps
- Automatic workflow progression

## 🔍 Search & Filtering

### Full-text Search
- Document name, title, description
- PostgreSQL tsvector optimization
- Relevance scoring

### Advanced Filters
- Document type and category
- Date ranges and status
- Creator and approver
- Confidentiality level
- File size and type

## 💾 File Storage

### Supported Formats
- **Documents**: PDF, DOC, DOCX, XLS, XLSX
- **Images**: JPG, PNG, GIF, BMP, WebP
- **Text**: TXT, CSV
- **Archives**: ZIP, RAR

### Storage Options
- **Local Filesystem**: Default storage
- **S3 Compatible**: Cloud storage support
- **Custom Backends**: Extensible storage

### File Validation
- Extension validation
- Size limits per document type
- Virus scanning hooks
- Checksum verification

## 🔗 Odoo Integration (Through FBS App)

### Integration Architecture
```
DMS App → FBS App → Odoo ERP
```

The DMS integrates with Odoo **through the FBS app**, not directly. This maintains proper separation of concerns and leverages FBS's existing Odoo integration capabilities.

### FBS App Integration
- **Service Discovery**: DMS automatically detects FBS app availability
- **Interface Usage**: Uses FBS's `FBSInterface.odoo` methods
- **Data Mapping**: Converts Django models to Odoo format
- **Error Handling**: Graceful fallback if FBS app unavailable

### Data Synchronization
- **Automatic Sync**: Document changes automatically sync to Odoo
- **Bidirectional**: Ready for Odoo → DMS sync through FBS
- **Real-time**: Immediate synchronization on CRUD operations
- **Conflict Resolution**: Handled through FBS app's conflict resolution

### Odoo Model Registration
```xml
<!-- allowed_models.xml (in Odoo) -->
<record id="model_fayvad_document" model="ir.model">
    <field name="name">Document</field>
    <field name="model">fayvad.document</field>
</record>
```

### Permission Mapping
- **FBS Role Mapping**: DMS permissions map to FBS roles
- **Company-based Access**: Leverages FBS's multi-tenant architecture
- **Record-level Security**: Inherits FBS's security model

## 📊 Performance Targets

- **Document List**: < 500ms
- **File Upload**: < 2s (10MB)
- **Search**: < 300ms
- **File Download**: Immediate stream
- **Workflow Processing**: < 1s

## 🧪 Testing

```bash
# Run tests
python manage.py test fbs_dms

# Run with coverage
python -m pytest fbs_dms/tests/ --cov=fbs_dms --cov-report=html

# Run specific test
python -m pytest fbs_dms/tests/test_document_service.py
```

## 📚 Documentation

- **[API Reference](docs/api.md)** - Complete API documentation
- **[User Guide](docs/user_guide.md)** - End-user documentation
- **[Developer Guide](docs/developer.md)** - Integration guide
- **[Deployment Guide](docs/deployment.md)** - Production setup

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://fbs-dms.readthedocs.io/](https://fbs-dms.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/fayvad/fbs-dms/issues)
- **Email**: support@fayvad.com

---

**Built with ❤️ by the Fayvad Team**
