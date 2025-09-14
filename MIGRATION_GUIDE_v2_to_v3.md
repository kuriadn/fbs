# FBS Suite Migration Guide: v2.0.4 (Django) → v3.0.0 (FastAPI)

## 📋 Overview

This guide helps existing FBS v2.0.4 (Django) users migrate to FBS v3.0.0 (FastAPI). The migration involves a complete architectural shift from Django to FastAPI with modern async patterns, but maintains all core business functionality.

## 🔄 What's Changed

### Architecture Changes
- **Framework**: Django → FastAPI
- **ORM**: Django ORM → SQLAlchemy 2.0
- **Configuration**: Django settings → Pydantic v2
- **Authentication**: Django auth → JWT tokens
- **API**: Django REST → FastAPI automatic docs
- **Deployment**: Manual → Docker v2+ recommended

### New Features (v3.0.0)
- **Module Generation**: Automated Odoo module creation
- **Async Operations**: Full async/await support
- **Modern Patterns**: Pydantic v2, SQLAlchemy 2.0
- **Docker Native**: Container-ready deployment

### Preserved Functionality
- ✅ Odoo integration (CRUD, discovery, modules)
- ✅ Business intelligence dashboards
- ✅ Workflow engine
- ✅ Document management
- ✅ License management
- ✅ Multi-tenant architecture

---

## 🚀 Migration Steps

### Step 1: Environment Setup

#### Before (v2.0.4)
```bash
# Django setup
pip install django djangorestframework
python manage.py migrate
python manage.py runserver
```

#### After (v3.0.0)
```bash
# FastAPI setup with Docker (recommended)
git clone https://github.com/kuriadn/fbs.git
cd fbs
docker-compose up -d

# Or manual setup
cd fbs_fastapi
pip install -r ../requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Configuration Migration

#### Django Settings → Pydantic Config

**Before (settings.py):**
```python
# Django settings
INSTALLED_APPS = ['fbs_app', 'fbs_dms', 'fbs_license_manager']
FBS_APP = {
    'ODOO_BASE_URL': 'http://localhost:8069',
    'DATABASE_USER': 'odoo',
    'DATABASE_PASSWORD': 'password',
}
```

**After (.env file):**
```bash
# FastAPI environment
APP_NAME="FBS FastAPI v3.0.0"
APP_VERSION="3.0.0"
DEBUG=false
SECRET_KEY="your-secret-key"
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/fbs_db"
REDIS_URL="redis://localhost:6379/0"
ODOO_BASE_URL="http://localhost:8069"
ODOO_USER="odoo"
ODOO_PASSWORD="password"
ENABLE_MODULE_GENERATION=true
```

### Step 3: Code Migration

#### Interface Usage Migration

**Before (Django):**
```python
from fbs_app.interfaces import FBSInterface

fbs = FBSInterface('solution_name')

# Odoo operations
models = fbs.odoo.discover_models()
records = fbs.odoo.get_records('res.partner')

# Business operations
dashboard = fbs.msme.get_dashboard()
```

**After (FastAPI):**
```python
import httpx

# Direct API calls (recommended)
async with httpx.AsyncClient() as client:
    # Odoo operations via API
    response = await client.get("http://localhost:8000/api/odoo/models")
    models = response.json()

    response = await client.get("http://localhost:8000/api/odoo/res.partner")
    records = response.json()

    # Business intelligence
    response = await client.get("http://localhost:8000/api/bi/dashboard")
    dashboard = response.json()
```

#### Service Integration Migration

**Before (Django views/models):**
```python
# Django model
class BusinessModel(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Custom business logic
        super().save(*args, **kwargs)

# Django view
def business_view(request):
    data = BusinessModel.objects.all()
    return JsonResponse({'data': list(data.values())})
```

**After (FastAPI routers):**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fbs_fastapi.core.database import get_db

router = APIRouter()

@router.get("/business")
async def get_business_data(db: AsyncSession = Depends(get_db)):
    # Use SQLAlchemy async queries
    result = await db.execute("SELECT * FROM business_model")
    data = result.fetchall()
    return {"data": data}
```

### Step 4: API Endpoint Migration

#### URL Pattern Changes

| Django (v2.0.4) | FastAPI (v3.0.0) | Change |
|----------------|------------------|---------|
| `/api/fbs/models/` | `/api/odoo/models` | Simplified |
| `/api/fbs/dashboard/` | `/api/bi/dashboard` | Reorganized |
| `/api/fbs/documents/` | `/api/dms/documents` | Consistent naming |
| `/api/auth/login/` | `/api/auth/login` | Same |
| `/api/workflows/` | `/api/workflows/` | Same |

#### Authentication Migration

**Before (Django):**
```python
# Django authentication
from django.contrib.auth import authenticate, login

user = authenticate(username=username, password=password)
if user:
    login(request, user)
```

**After (FastAPI):**
```python
# JWT token authentication
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post("/api/auth/login", json={
        "username": username,
        "password": password
    })
    token = response.json()["access_token"]

    # Use token in subsequent requests
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/protected/endpoint", headers=headers)
```

### Step 5: Database Migration

#### Model Migration

**Before (Django):**
```python
class CustomModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'custom_app'
```

**After (FastAPI):**
```python
from sqlalchemy import Column, String, DateTime
from fbs_fastapi.core.database import Base

class CustomModel(Base):
    __tablename__ = "custom_model"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    created_at = Column(DateTime, server_default="NOW()")
```

### Step 6: Testing Migration

#### Test Structure Changes

**Before (Django):**
```python
from django.test import TestCase
from fbs_app.models import BusinessModel

class BusinessModelTest(TestCase):
    def test_model_creation(self):
        obj = BusinessModel.objects.create(name="test")
        self.assertEqual(obj.name, "test")
```

**After (FastAPI):**
```python
import pytest
from httpx import AsyncClient
from fbs_fastapi.main import app

@pytest.mark.asyncio
async def test_business_endpoint():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/api/business")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
```

### Step 7: Module Generation Setup

#### New Feature (v3.0.0)
```python
from fbs_fastapi.services.module_generation_service import ModuleSpec

# Create Odoo module specification
spec = ModuleSpec(
    name="custom_module",
    description="Custom business module",
    author="Your Organization",
    models=[{
        "name": "custom.model",
        "fields": [
            {"name": "name", "type": "char", "required": True},
            {"name": "amount", "type": "float"}
        ]
    }]
)

# Generate and deploy module
generator = FBSModuleGeneratorEngine()
module_path = await generator.generate_module(spec)
await generator.deploy_to_odoo(module_path)
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. Import Errors
**Problem**: `ModuleNotFoundError` for FBS modules
**Solution**: Update imports to use new module structure
```python
# Wrong
from fbs_app.services import BusinessService

# Correct
from fbs_fastapi.services.business_service import BusinessService
```

#### 2. Authentication Issues
**Problem**: Old Django auth patterns don't work
**Solution**: Use JWT tokens for all API calls
```python
# Get token first
token_response = await client.post("/api/auth/login", json=credentials)
token = token_response.json()["access_token"]

# Use in all requests
headers = {"Authorization": f"Bearer {token}"}
```

#### 3. Database Connection Issues
**Problem**: SQLAlchemy connection strings
**Solution**: Use async PostgreSQL URLs
```python
# Correct format
DATABASE_URL="postgresql+asyncpg://user:password@host:5432/database"
```

#### 4. Async/Await Errors
**Problem**: Synchronous code in async context
**Solution**: Use async database operations
```python
# Wrong
result = db.execute(query)

# Correct
result = await db.execute(query)
data = await result.fetchall()
```

---

## 📋 Migration Checklist

### Pre-Migration
- [ ] Backup existing Django database
- [ ] Export current configurations
- [ ] Document custom business logic
- [ ] Test current functionality

### Environment Setup
- [ ] Clone FBS v3.0.0 repository
- [ ] Setup Docker environment
- [ ] Configure environment variables
- [ ] Start services with docker-compose

### Code Migration
- [ ] Update all FBS imports
- [ ] Convert Django models to SQLAlchemy
- [ ] Update API endpoint URLs
- [ ] Implement JWT authentication
- [ ] Convert synchronous to asynchronous code

### Testing & Validation
- [ ] Run existing test suites
- [ ] Test all business workflows
- [ ] Validate Odoo integration
- [ ] Test module generation features
- [ ] Performance testing

### Production Deployment
- [ ] Update production Docker configurations
- [ ] Migrate production database
- [ ] Update monitoring and logging
- [ ] Test production environment
- [ ] Gradual rollout with rollback plan

---

## 🎯 Benefits of Migration

### Performance Improvements
- **Async Operations**: Better concurrency handling
- **Modern Framework**: FastAPI's high performance
- **Optimized ORM**: SQLAlchemy 2.0 efficiency

### Developer Experience
- **Auto-generated Docs**: Interactive API documentation
- **Type Safety**: Full type annotations
- **Modern Patterns**: Current best practices

### Operational Benefits
- **Docker Native**: Easy deployment and scaling
- **Module Generation**: Automated Odoo module creation
- **Better Monitoring**: Health checks and metrics

---

## 🆘 Support & Resources

### Documentation
- [FBS FastAPI README](fbs_fastapi/README.md)
- [API Documentation](http://localhost:8000/docs)
- [Docker Setup Guide](docker-compose.yml)

### Getting Help
- GitHub Issues: Report migration issues
- Documentation: Check README files
- Examples: Review test files for patterns

### Rollback Plan
- Keep Django v2.0.4 environment running
- Gradual migration of services
- Database backup before migration
- Test rollback procedures

---

**This migration transforms your FBS deployment from Django-based to modern FastAPI architecture while preserving all business functionality and adding powerful new module generation capabilities.**

**Need help? Check the [FBS FastAPI README](fbs_fastapi/README.md) or create a GitHub issue for specific migration questions.**
