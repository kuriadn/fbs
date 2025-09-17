# FBS FastAPI Developer Guide

## Overview

FBS FastAPI is a production-ready business suite that provides automated Odoo module generation, document management, and enterprise licensing. It serves as an embeddable framework for building business applications with Odoo integration.

## Architecture

### Core Components

1. **FBSInterface** - Main orchestration interface
2. **Module Generation Engine** - Automated Odoo module creation
3. **Document Management System (DMS)** - File and workflow management
4. **License Management** - Feature control and usage tracking
5. **Discovery Service** - Odoo model and field exploration

### Database Architecture

- **System Database**: `fbs_system_db` - Shared configuration
- **Solution Databases**:
  - `fpi_{solution}_db` - FastAPI-specific data
  - `fbs_{solution}_db` - Odoo integration data

## Getting Started

### Installation

```bash
git clone https://github.com/kuriadn/fbs.git
cd fbs
pip install -r fbs_fastapi/requirements.txt
```

### Configuration

```bash
# Copy and modify environment variables
cp fbs_fastapi/env.example fbs_fastapi/.env

# Required settings
APP_NAME="My Business Solution"
APP_VERSION="1.0.0"
SECRET_KEY="your-secret-key-here"
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/fbs_system_db"
ODOO_URL="http://localhost:8069"
ODOO_DB="odoo_db"
```

### Basic Usage

```python
from fbs_fastapi.services.service_interfaces import FBSInterface

# Initialize FBS for your solution
fbs = FBSInterface(solution_name="my_business", license_key="enterprise")

# Access services
discovery = fbs.discovery
module_gen = fbs.module_gen
```

## Module Generation

### Creating Module Specifications

```python
from fbs_fastapi.services.module_generation_service import ModuleSpec

spec = ModuleSpec(
    name="business_contacts",
    description="Custom business contact management",
    author="Your Team",
    inherit_from="res.partner",  # Inherit from existing Odoo model
    models=[{
        "name": "res.partner",
        "inherit_from": "res.partner",
        "fields": [
            {"name": "business_type", "type": "selection",
             "selection": "[('individual','Individual'),('company','Company')]"},
            {"name": "tax_id", "type": "char", "string": "Tax ID"},
            {"name": "credit_rating", "type": "float"}
        ]
    }],
    workflows=[{
        "model": "res.partner",
        "states": [
            {"name": "draft", "string": "Draft"},
            {"name": "approved", "string": "Approved"}
        ]
    }],
    security={
        "rules": [{
            "name": "Business Contact Access",
            "model": "res.partner",
            "groups": ["business_users"],
            "permissions": ["read", "write", "create"]
        }]
    }
)
```

### Generating and Installing Modules

```python
# Generate module
result = await fbs.module_gen.generate_and_install(spec, "admin", "my_business")

if result["success"]:
    print(f"Module generated: {result['module_name']}")
    print(f"Install path: {result['install_path']}")
```

### Supported Module Features

- **Model Inheritance** - Extend existing Odoo models
- **Custom Fields** - Add business-specific fields
- **Workflows** - Define approval processes
- **Security Rules** - Control access permissions
- **Views** - Generate forms and lists (optional)
- **ZIP Packaging** - Ready-to-install modules

## Document Management System (DMS)

### Document Types and Categories

```python
# Create document type
await fbs.dms.create_document_type({
    "name": "Contract",
    "description": "Business contracts",
    "allowed_extensions": ["pdf", "docx"],
    "max_file_size": 10485760,  # 10MB
    "requires_approval": True
})

# Create category
await fbs.dms.create_document_category({
    "name": "Legal",
    "description": "Legal documents",
    "sequence": 1
})
```

### Managing Documents

```python
# Upload document
with open("contract.pdf", "rb") as f:
    result = await fbs.dms.create_document({
        "name": "Service Contract",
        "title": "Master Service Agreement",
        "document_type_id": contract_type_id,
        "category_id": legal_category_id,
        "confidentiality_level": "confidential",
        "description": "2024 service agreement"
    }, "user_id", f)

# Link document to business record
await fbs.odoo.update_record("business.contract", record_id, {
    "document_id": result["document"]["id"]
})
```

## License Management

### Checking Feature Access

```python
# Check if feature is available
has_access = await fbs.license.check_feature_access("my_business", "module_generation")
if not has_access:
    raise HTTPException(403, "Feature not licensed")

# Check usage limits
usage_ok = await fbs.license.check_usage_limits("my_business", "documents", current_count=150)
```

### License Configuration

```python
# For enterprise license, all features are enabled
# Trial license provides basic access
# Professional/Business licenses provide tiered access
```

## Discovery Service

### Exploring Odoo Models

```python
# Discover all models
models = await fbs.discovery.discover_models("fbs_my_business_db")
print(f"Found {len(models['data']['models'])} models")

# Discover specific model fields
fields = await fbs.discovery.discover_fields("res.partner")
for field in fields["data"]["fields"]:
    print(f"{field['name']}: {field['type']}")
```

### Using Discovery for Module Generation

```python
# Discover existing structure
discovery_result = await fbs.discovery.discover_models(fbs.odoo_db_name)

# Generate extensions based on findings
extensions = await fbs.module_gen.generate_from_discovery(
    discovery_result, "developer", "my_business"
)
```

## API Endpoints

### Module Generation API

```bash
# Validate specification
POST /api/module-gen/validate
Content-Type: application/json
{
  "name": "test_module",
  "description": "Test module",
  "inherit_from": "res.partner",
  "models": [...]
}

# Generate module
POST /api/module-gen/generate
# Returns ZIP file

# Generate and install
POST /api/module-gen/generate-and-install
# Generates and installs in Odoo
```

### Document Management API

```bash
# List documents
GET /api/dms/documents

# Upload document
POST /api/dms/documents
Content-Type: multipart/form-data

# Get document
GET /api/dms/documents/{id}

# Download document
GET /api/dms/documents/{id}/download
```

### License Management API

```bash
# Get license info
GET /api/license/info

# Check feature access
POST /api/license/check-access
{
  "feature_name": "module_generation",
  "current_usage": 5
}
```

## Integration Patterns

### Complete Business Solution Workflow

```python
async def setup_business_solution(solution_name: str):
    # 1. Initialize FBS
    fbs = FBSInterface(solution_name, "enterprise")

    # 2. Discover existing Odoo structure
    existing_models = await fbs.discovery.discover_models(f"fbs_{solution_name}_db")

    # 3. Generate custom extensions
    extensions_spec = create_extension_specs(existing_models)
    result = await fbs.module_gen.generate_and_install(extensions_spec, "admin", solution_name)

    # 4. Set up document management
    await setup_document_types(fbs.dms, solution_name)

    # 5. Configure workflows
    await setup_business_workflows(fbs, solution_name)

    return {"status": "complete", "modules": result}
```

### Hybrid Development Approach

```python
# Use discovery + generation + virtual fields
async def extend_odoo_model(base_model: str, custom_fields: list):
    # 1. Generate structured extension module
    spec = ModuleSpec(
        name=f"{base_model}_extension",
        inherit_from=base_model,
        models=[{"name": base_model, "fields": custom_fields}]
    )
    await fbs.module_gen.generate_and_install(spec, "dev", "solution")

    # 2. Add immediate virtual fields for development
    for field in custom_fields:
        await fbs.fields.set_custom_field(
            base_model, record_id, field["name"], field_value
        )
```

## Deployment

### Docker Deployment

```bash
# Build the application
docker build -t fbs-fastapi:v3.1.1 fbs_fastapi/

# Run with environment variables
docker run -p 8000:8000 \
  -e SECRET_KEY="your-secret" \
  -e DATABASE_URL="postgresql+asyncpg://..." \
  -e ODOO_URL="http://odoo:8069" \
  fbs-fastapi:v3.1.1
```

### Production Configuration

```bash
# Use environment variables for production
export APP_NAME="Production Business Suite"
export DEBUG=false
export DATABASE_URL="postgresql+asyncpg://prod_user:prod_pass@prod_host:5432/fbs_system_db"
export REDIS_URL="redis://prod_redis:6379"
export ODOO_URL="http://prod_odoo:8069"
```

## Testing

### Running Tests

```bash
# Run all tests
python fbs_fastapi/tests/run_all_tests.py

# Run specific test categories
python -m pytest fbs_fastapi/tests/unit/ -v
python -m pytest fbs_fastapi/tests/functional/ -v
```

### Test Configuration

Tests require environment variables:
- `SECRET_KEY` - Test secret key
- `DATABASE_URL` - Test database connection
- `ODOO_URL` - Odoo test instance

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Database Connection**: Verify DATABASE_URL format
3. **Odoo Integration**: Check Odoo URL and credentials
4. **License Issues**: Verify license key format

### Debug Mode

Enable debug logging:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Health Checks

```python
# Check system health
health = await fbs.get_system_health()
print(f"Database: {health['database']['status']}")
print(f"Odoo: {health['odoo']['status']}")
```

## Contributing

### Development Setup

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes following existing patterns
4. Add tests for new functionality
5. Ensure all tests pass: `python fbs_fastapi/tests/run_all_tests.py`
6. Submit pull request

### Code Standards

- Use async/await for database operations
- Follow existing service interface patterns
- Add type hints for new functions
- Include comprehensive error handling
- Write tests for new features

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- GitHub Issues: https://github.com/kuriadn/fbs/issues
- Documentation: https://github.com/kuriadn/fbs/wiki
- Email: support@fbs-suite.com

---

**FBS FastAPI v3.1.1** - Revolutionizing business suite development with automated module generation!
