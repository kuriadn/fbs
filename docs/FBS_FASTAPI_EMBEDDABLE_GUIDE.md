# FBS FastAPI Embeddable Framework Guide

## 📋 Overview

**FBS FastAPI v3.1.0** is a comprehensive business suite framework designed as an **embeddable library** for FastAPI applications. It provides production-ready business functionality that can be seamlessly integrated into any FastAPI-based solution.

## 🎯 What FBS FastAPI Provides

### Core Capabilities

#### 1. **Business Management (MSME)**
- **Business Setup Wizard**: Guided business configuration with templates
- **Dashboard Analytics**: Real-time KPIs and business metrics
- **Profile Management**: Complete business profile and settings
- **Marketing Data**: Business intelligence and market insights
- **Custom Fields**: Extensible business data structures

#### 2. **Document Management System (DMS)**
- **Document Upload**: Secure file handling with type validation
- **Workflow Integration**: Document approval processes
- **Version Control**: Document versioning and history
- **Access Control**: Role-based document permissions
- **Search & Indexing**: Full-text document search

#### 3. **License Management**
- **Feature Control**: Runtime feature enablement/disablement
- **Usage Limits**: Configurable resource limits per solution
- **License Validation**: Real-time license verification
- **Upgrade Prompts**: Seamless upgrade workflows

#### 4. **Odoo ERP Integration**
- **Model Discovery**: Automatic Odoo model introspection
- **Field Mapping**: Dynamic field type conversion
- **Workflow Execution**: Odoo business process integration
- **Security Rules**: Automated access control
- **Module Installation**: Runtime module deployment

#### 5. **Module Generation Engine**
- **Automated Odoo Modules**: Generate complete modules from specifications
- **View Generation**: Forms, lists, and search views
- **Security Configuration**: Access rights and rules
- **Workflow States**: Dynamic state management
- **ZIP Packaging**: Ready-to-deploy packages

## 🏗️ Architecture

### Embeddable Design Pattern

FBS FastAPI follows the **Service Interface Pattern** where:

1. **FBSInterface** - Main entry point for all functionality
2. **Protocol-based Services** - Clean interfaces for each capability
3. **Lazy Loading** - Services loaded on-demand for performance
4. **Configuration-driven** - Runtime feature control via environment

### Multi-Tenant Architecture

```
Solution-specific databases:
├── fpi_{solution_name}_db     # FastAPI business data
├── fbs_{solution_name}_db     # Odoo ERP data
└── fbs_system_db             # Shared system data
```

### Service Interface Hierarchy

```
FBSInterface
├── msme: MSMEInterfaceProtocol
├── bi: BusinessIntelligenceInterfaceProtocol
├── workflows: WorkflowInterfaceProtocol
├── compliance: ComplianceInterfaceProtocol
├── accounting: AccountingInterfaceProtocol
├── auth: AuthInterfaceProtocol
├── onboarding: OnboardingInterfaceProtocol
├── discovery: DiscoveryInterfaceProtocol
├── odoo: OdooInterfaceProtocol
├── notifications: NotificationInterfaceProtocol
├── cache: CacheService
└── signals: SignalsInterfaceProtocol
```

## 🚀 Implementation Guide

### 1. Basic Setup

#### Install FBS FastAPI

```bash
# Add to your requirements.txt or pyproject.toml
fbs-fastapi>=3.1.0

# Or install directly
pip install fbs-fastapi
```

#### Initialize in Your FastAPI App

```python
from fastapi import FastAPI
from fbs_fastapi.services.service_interfaces import FBSInterface
from fbs_fastapi.core.config import config

app = FastAPI(title="Your Solution", version="1.0.0")

# Initialize FBS for your solution
fbs = FBSInterface(
    solution_name="your_solution_name",
    license_key="your_license_key"  # Optional
)

# Include FBS routers
from fbs_fastapi.routers.business import router as business_router
app.include_router(business_router, prefix="/api/business")

# Optional: Include other FBS routers based on needs
if config.enable_dms_features:
    from fbs_fastapi.routers.dms import router as dms_router
    app.include_router(dms_router, prefix="/api/dms")

if config.enable_licensing_features:
    from fbs_fastapi.routers.license import router as license_router
    app.include_router(license_router, prefix="/api/license")
```

### 2. Configuration

#### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/fbs_system_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Odoo Integration
ODOO_BASE_URL=http://localhost:8069
ODOO_USER=odoo
ODOO_PASSWORD=your_password

# Caching
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true

# Feature Flags
ENABLE_MSME_FEATURES=true
ENABLE_DMS_FEATURES=true
ENABLE_MODULE_GENERATION=true
ENABLE_LICENSING_FEATURES=true

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret
```

#### Programmatic Configuration

```python
from fbs_fastapi.core.config import FBSConfig

# Create custom config
config = FBSConfig(
    app_name="Your Custom Solution",
    database_url="postgresql+asyncpg://user:pass@host:5432/your_db",
    enable_msme_features=True,
    enable_dms_features=False,  # Disable if not needed
    enable_module_generation=True
)
```

### 3. Database Setup

#### Required Databases

```sql
-- System database (shared across solutions)
CREATE DATABASE fbs_system_db;

-- Solution-specific databases
CREATE DATABASE fpi_your_solution_db;  -- FastAPI data
CREATE DATABASE fbs_your_solution_db;   -- Odoo data
```

#### Auto-Migration

```python
# FBS handles migrations automatically
from fbs_fastapi.core.database import create_tables

# Run during app startup
await create_tables()
```

### 4. Service Usage Patterns

#### Business Management

```python
# Setup new business
business_data = await fbs.msme.setup_business(
    business_type="retail",
    config={
        "name": "My Retail Store",
        "industry": "retail",
        "size": "small"
    }
)

# Get dashboard data
dashboard = await fbs.msme.get_dashboard()

# Calculate KPIs
kpis = await fbs.msme.calculate_kpis()
```

#### Odoo Integration

```python
# Discover available models
models = await fbs.discovery.discover_models("your_solution")

# Get records from Odoo
records = await fbs.odoo.get_records(
    model_name="res.partner",
    domain=[["customer", "=", True]],
    fields=["name", "email", "phone"]
)

# Create new record
new_partner = await fbs.odoo.create_record(
    model_name="res.partner",
    data={
        "name": "New Customer",
        "email": "customer@example.com",
        "customer": True
    }
)
```

#### Document Management

```python
# Upload document
upload_result = await fbs.dms.upload_document(
    file=file_object,
    metadata={
        "title": "Invoice #123",
        "category": "finance",
        "tags": ["invoice", "2024"]
    }
)

# Search documents
documents = await fbs.dms.search_documents(
    query="invoice",
    filters={"category": "finance"}
)
```

#### Module Generation

```python
# Generate Odoo module
module_spec = {
    "name": "custom_inventory",
    "description": "Custom inventory management module",
    "version": "1.0.0",
    "models": [
        {
            "name": "custom.inventory",
            "fields": [
                {"name": "product_name", "type": "char", "required": True},
                {"name": "quantity", "type": "integer", "default": 0}
            ]
        }
    ]
}

module_zip = await fbs.module_gen.generate_module(module_spec)
```

## 🐳 Docker Integration

### Recommended Architecture

```
Host Machine:
├── PostgreSQL (localhost:5432)
├── Redis (localhost:6379)
├── Odoo (localhost:8069)
└── Nginx (localhost:80)

Docker Container:
└── FBS FastAPI App (port 8000)
    └── Connects to host services via host.docker.internal
```

### Docker Compose Setup

```yaml
version: '3.8'
services:
  your-solution:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      # Connect to host services
      - DATABASE_URL=postgresql+asyncpg://user:pass@host.docker.internal:5432/fpi_your_solution_db
      - REDIS_URL=redis://host.docker.internal:6379/0
      - ODOO_BASE_URL=http://host.docker.internal:8069
      - SECRET_KEY=your-secret-key
      - ENABLE_MODULE_GENERATION=true
    network_mode: host
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./generated_modules:/app/generated_modules
```

## 🔧 Custom Service Implementation

### Extending FBS Patterns

```python
from fbs_fastapi.services.service_interfaces import BaseService, AsyncServiceMixin
from typing import Dict, Any, Protocol

class CustomServiceProtocol(Protocol):
    async def custom_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Custom business operation"""
        ...

class CustomService(BaseService, AsyncServiceMixin):
    def __init__(self, solution_name: str):
        super().__init__(solution_name)

    async def custom_operation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Implement custom business logic"""
        # Your custom implementation here
        return {
            "success": True,
            "result": "Custom operation completed",
            "data": data
        }

# Use in your FBS interface
fbs.custom_service = CustomService("your_solution")
```

## 🔒 Security Considerations

### Authentication Integration

```python
# FBS provides authentication patterns
handshake = await fbs.auth.create_handshake()

# Validate tokens
token_valid = await fbs.auth.validate_token_mapping(
    token="user_token",
    database_name="your_solution"
)
```

### CORS Configuration

```python
# Configure CORS for your frontend
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS
```

## 📊 Monitoring & Health Checks

### Health Endpoints

```python
# Built-in health checks
@app.get("/health")
async def health():
    return await fbs.get_system_health()

@app.get("/health/detailed")
async def detailed_health():
    health_data = await fbs.get_system_health()

    # Add custom health checks
    custom_health = await your_custom_health_check()
    health_data["components"]["custom_service"] = custom_health

    return health_data
```

### Logging Configuration

```python
# Configure structured logging
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_REQUESTS=true
LOG_RESPONSES=false
```

## 🚀 Production Deployment

### Performance Optimization

```python
# Database connection pooling
DATABASE_POOL_SIZE=50
DATABASE_MAX_OVERFLOW=100

# Caching configuration
CACHE_TIMEOUT=3600
CACHE_ENABLED=true

# Rate limiting
REQUEST_RATE_LIMIT=5000  # requests per hour
REQUEST_BURST_LIMIT=500  # requests per minute
```

### Scaling Considerations

```python
# Multiple FBS instances can share the same databases
# Each instance gets its own Redis database number
REDIS_URL=redis://localhost:6379/1  # Instance 1
REDIS_URL=redis://localhost:6379/2  # Instance 2
```

## 📚 API Reference

### Core Endpoints

```
GET  /                        # API information
GET  /health                  # Basic health check
GET  /health/detailed         # Detailed health check
GET  /docs                    # Interactive API documentation
GET  /openapi.json            # OpenAPI specification
```

### Business Management

```
POST /api/business/setup      # Setup new business
GET  /api/business/dashboard  # Get business dashboard
POST /api/business/profile    # Update business profile
GET  /api/business/kpis       # Get business KPIs
```

### Document Management

```
POST /api/dms/upload          # Upload document
GET  /api/dms/documents       # List documents
GET  /api/dms/search          # Search documents
POST /api/dms/workflow        # Start document workflow
```

### Module Generation

```
POST /api/module/generate     # Generate Odoo module
GET  /api/module/templates    # Get module templates
POST /api/module/deploy       # Deploy generated module
```

## 🐛 Troubleshooting

### Common Issues

#### Database Connection
```python
# Test database connectivity
from fbs_fastapi.core.database import check_database_health
health = await check_database_health()
print(health)
```

#### Odoo Integration
```python
# Test Odoo connectivity
odoo_health = await fbs.odoo.health_check()
print(odoo_health)
```

#### License Issues
```python
# Check license status
license_info = await fbs.get_license_info()
print(license_info)
```

## 📝 Best Practices

### 1. Environment Management
- Use different databases for development/staging/production
- Store secrets securely (not in code)
- Use environment-specific configurations

### 2. Error Handling
```python
from fbs_fastapi.services.service_interfaces import AsyncServiceMixin

class SafeService(AsyncServiceMixin):
    async def safe_operation(self, data):
        return await self._safe_execute(self._actual_operation, data)
```

### 3. Performance Optimization
- Enable caching for frequently accessed data
- Use database connection pooling
- Implement proper indexing on custom fields

### 4. Security
- Regularly rotate JWT secrets
- Use HTTPS in production
- Implement proper CORS policies
- Validate file uploads thoroughly

## 🔄 Migration from Previous Versions

### From FBS Django v2.x

1. **Update Dependencies**: Replace Django dependencies with FBS FastAPI
2. **Database Migration**: Run FBS migration scripts
3. **Code Migration**: Update service calls to use new interface
4. **Configuration**: Migrate environment variables
5. **Testing**: Update tests to use FastAPI test client

### Migration Script Example

```python
from fbs_fastapi.core.database import migrate_from_django

# Migrate existing data
await migrate_from_django(
    django_db_url="postgresql://user:pass@localhost:5432/old_django_db",
    fastapi_db_url="postgresql://user:pass@localhost:5432/fpi_new_db"
)
```

## 🤝 Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/kuriadn/fbs.git
cd fbs/fbs_fastapi

# Install dependencies
pip install -e .

# Run tests
pytest tests/

# Start development server
uvicorn main:app --reload
```

### Adding New Services

1. Create service protocol in `service_interfaces.py`
2. Implement service class following BaseService pattern
3. Add to FBSInterface with lazy loading
4. Create router if needed
5. Add comprehensive tests
6. Update documentation

---

**FBS FastAPI v3.1.0** - Production-ready, embeddable business suite framework for modern FastAPI applications.
