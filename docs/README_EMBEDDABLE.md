# FBS FastAPI v3.1.0 - Embeddable Business Suite

[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](https://github.com/kuriadn/fbs)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🎯 What is FBS FastAPI?

**FBS FastAPI** is a comprehensive, production-ready business suite designed as an **embeddable framework** for FastAPI applications. It provides enterprise-grade business functionality that seamlessly integrates into your existing FastAPI projects.

## ✨ Key Features

### 🚀 Revolutionary Module Generation
- **Automated Odoo Module Creation** from specifications
- **Field Type Mappings** with automatic data conversion
- **Workflow States** and dynamic state management
- **Security Rules** and access control
- **View Generation** (forms, lists, search views)
- **ZIP Packaging** for ready-to-deploy modules

### 🏢 Business Management (MSME)
- **Business Setup Wizard** with guided configuration
- **Real-time Dashboard** with KPIs and analytics
- **Profile Management** with extensible custom fields
- **Marketing Data** and business intelligence
- **Compliance Management** and regulatory reporting

### 📄 Document Management System (DMS)
- **Secure File Upload** with type validation
- **Workflow Integration** for document approvals
- **Version Control** with history tracking
- **Access Control** with role-based permissions
- **Search & Indexing** with full-text search

### 🔐 Advanced Features
- **Multi-tenant Architecture** with isolated databases
- **License Management** with feature control
- **Odoo ERP Integration** with model discovery
- **Async/Await Support** throughout
- **Type Safety** with complete annotations

## 🏗️ Architecture

### Embeddable Design Pattern

```python
from fbs_fastapi.services.service_interfaces import FBSInterface

# Initialize FBS in your FastAPI app
fbs = FBSInterface(
    solution_name="your_solution",
    license_key=None  # Optional licensing
)

# Use any FBS service
dashboard = await fbs.msme.get_dashboard()
models = await fbs.discovery.discover_models("your_solution")
```

### Service Interface Architecture

```
FBSInterface
├── msme: MSMEInterfaceProtocol          # Business management
├── bi: BusinessIntelligenceInterfaceProtocol  # Analytics & reporting
├── workflows: WorkflowInterfaceProtocol       # Process automation
├── compliance: ComplianceInterfaceProtocol     # Regulatory compliance
├── accounting: AccountingInterfaceProtocol     # Financial operations
├── auth: AuthInterfaceProtocol               # Authentication
├── onboarding: OnboardingInterfaceProtocol    # Client setup
├── discovery: DiscoveryInterfaceProtocol      # Odoo integration
├── odoo: OdooInterfaceProtocol              # ERP operations
├── notifications: NotificationInterfaceProtocol  # Alerts & messaging
└── cache: CacheService                       # Performance caching
```

## 🚀 Quick Start

### 1. Install FBS FastAPI

```bash
pip install fbs-fastapi>=3.1.0
```

### 2. Basic Integration

```python
from fastapi import FastAPI
from fbs_fastapi.services.service_interfaces import FBSInterface

app = FastAPI()
fbs = FBSInterface(solution_name="my_business")

@app.get("/dashboard")
async def get_dashboard():
    return await fbs.msme.get_dashboard()
```

### 3. Docker Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  your-app:
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@host.docker.internal:5432/fpi_your_db
      - REDIS_URL=redis://host.docker.internal:6379/0
      - ODOO_BASE_URL=http://host.docker.internal:8069
    network_mode: host
```

## 📚 Documentation

### 📖 Comprehensive Guides

| Guide | Description |
|-------|-------------|
| [`FBS_FASTAPI_EMBEDDABLE_GUIDE.md`](./FBS_FASTAPI_EMBEDDABLE_GUIDE.md) | Complete implementation guide |
| [`FBS_IMPLEMENTATION_EXAMPLE.py`](./FBS_IMPLEMENTATION_EXAMPLE.py) | Working code examples |
| [`DOCKER_INTEGRATION_EXAMPLE.py`](./DOCKER_INTEGRATION_EXAMPLE.py) | Docker deployment patterns |

### 🎯 Implementation Examples

#### Business Setup
```python
business_data = await fbs.msme.setup_business(
    business_type="retail",
    config={"name": "My Store", "industry": "retail"}
)
```

#### Odoo Integration
```python
# Discover available models
models = await fbs.discovery.discover_models("your_solution")

# Create records
customer = await fbs.odoo.create_record(
    model_name="res.partner",
    data={"name": "New Customer", "customer": True}
)
```

#### Module Generation
```python
module = await fbs.module_gen.generate_module({
    "name": "custom_inventory",
    "description": "Custom inventory management",
    "models": [{
        "name": "custom.inventory",
        "fields": [
            {"name": "product_name", "type": "char", "required": True},
            {"name": "quantity", "type": "integer", "default": 0}
        ]
    }]
})
```

## 🐳 Production Deployment

### Host Services Architecture

```
Host Machine:
├── PostgreSQL (localhost:5432)     # Database server
├── Redis (localhost:6379)         # Cache server
├── Odoo (localhost:8069)          # ERP system
└── Nginx (localhost:80)           # Web server

Docker Container:
└── FBS FastAPI App (port 8000)    # Your application
    └── Connects via host.docker.internal
```

### Database Schema

```sql
-- Required databases
CREATE DATABASE fbs_system_db;           -- Shared system data
CREATE DATABASE fpi_your_solution_db;   -- FastAPI business data
CREATE DATABASE fbs_your_solution_db;   -- Odoo ERP data
```

## 🔧 Configuration

### Environment Variables

```bash
# Application
APP_NAME="Your Solution"
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/fpi_your_db"
REDIS_URL="redis://localhost:6379/0"
ODOO_BASE_URL="http://localhost:8069"

# Features
ENABLE_MSME_FEATURES=true
ENABLE_DMS_FEATURES=true
ENABLE_MODULE_GENERATION=true

# Security
SECRET_KEY="your-secret-key"
JWT_SECRET_KEY="your-jwt-secret"
```

### Feature Flags

| Feature | Description | Environment Variable |
|---------|-------------|---------------------|
| MSME | Business management | `ENABLE_MSME_FEATURES` |
| DMS | Document management | `ENABLE_DMS_FEATURES` |
| BI | Business intelligence | `ENABLE_BI_FEATURES` |
| Workflows | Process automation | `ENABLE_WORKFLOW_FEATURES` |
| Compliance | Regulatory compliance | `ENABLE_COMPLIANCE_FEATURES` |
| Accounting | Financial operations | `ENABLE_ACCOUNTING_FEATURES` |
| Module Gen | Odoo module generation | `ENABLE_MODULE_GENERATION` |

## 🔌 API Endpoints

### Core Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive documentation

### Business Management
- `POST /api/business/setup` - Setup business
- `GET /api/business/dashboard` - Get dashboard
- `POST /api/business/profile` - Update profile

### Document Management
- `POST /api/dms/upload` - Upload document
- `GET /api/dms/documents` - List documents
- `POST /api/dms/workflow` - Start workflow

### Module Generation
- `POST /api/module/generate` - Generate module
- `GET /api/module/templates` - Get templates

## 🧪 Testing

### Health Checks
```python
# Basic health
response = await client.get("/health")

# Detailed health with components
response = await client.get("/health/detailed")
```

### Service Testing
```python
# Test FBS services
dashboard = await fbs.msme.get_dashboard()
assert dashboard["status"] == "success"

# Test Odoo integration
models = await fbs.discovery.discover_models("test")
assert len(models) > 0
```

## 🔒 Security

### Authentication
```python
# FBS provides authentication patterns
handshake = await fbs.auth.create_handshake()
token_valid = await fbs.auth.validate_token_mapping(token, database)
```

### CORS Configuration
```python
# Configure for your frontend
CORS_ORIGINS="https://yourdomain.com,https://app.yourdomain.com"
CORS_ALLOW_CREDENTIALS=true
```

### File Upload Security
```python
# Configurable upload limits
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_FILE_TYPES="pdf,doc,docx,xls,xlsx,txt,jpg,jpeg,png"
```

## 📊 Monitoring

### Built-in Health Checks
- Database connectivity
- Redis cache status
- Odoo integration
- Service availability

### Logging Configuration
```python
LOG_LEVEL=INFO
LOG_REQUESTS=true
LOG_RESPONSES=false
```

## 🚦 Performance

### Optimization Settings
```python
# Database connection pooling
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=100

# Caching
CACHE_TIMEOUT=3600
CACHE_ENABLED=true

# Rate limiting
REQUEST_RATE_LIMIT=5000  # per hour
REQUEST_BURST_LIMIT=500  # per minute
```

## 🐛 Troubleshooting

### Common Issues

**Database Connection**
```bash
# Test connectivity
psql -h localhost -U user -d database
```

**Odoo Integration**
```python
# Test Odoo connection
import xmlrpc.client
common = xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common')
print(common.version())
```

**Docker Networking**
```bash
# Test host connectivity
docker exec -it container ping host.docker.internal
```

## 📈 Migration Guide

### From FBS Django v2.x

1. **Install FBS FastAPI**: `pip install fbs-fastapi`
2. **Update Database URLs**: Change `djo_` to `fpi_` prefixes
3. **Migrate Environment Variables**: Update configuration
4. **Update Service Calls**: Use new async interface
5. **Test Integration**: Verify all functionality

### Breaking Changes
- All methods are now `async`
- Database naming convention changed
- Service interface updated
- Configuration moved to Pydantic v2

## 🤝 Support

### Resources
- 📖 [Complete Implementation Guide](./FBS_FASTAPI_EMBEDDABLE_GUIDE.md)
- 💻 [Working Examples](./FBS_IMPLEMENTATION_EXAMPLE.py)
- 🐳 [Docker Integration](./DOCKER_INTEGRATION_EXAMPLE.py)
- 🔧 [Troubleshooting Guide](./DOCKER_INTEGRATION_EXAMPLE.py)

### Getting Help
1. Check the comprehensive guides
2. Review example implementations
3. Test with provided examples
4. Check GitHub issues for similar problems

## 📋 Requirements

- **Python**: 3.10+
- **FastAPI**: 0.115.6+
- **PostgreSQL**: 12+
- **Redis**: 6+
- **Odoo**: 16+ (optional)

## 📄 License

MIT License - see LICENSE file for details.

---

**FBS FastAPI v3.1.0** - Production-ready, embeddable business suite for modern FastAPI applications.
