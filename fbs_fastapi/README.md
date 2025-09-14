# FBS FastAPI v3.1.0 - Fayvad Business Suite

[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](https://github.com/kuriadn/fbs)
[![Docker](https://img.shields.io/badge/docker-v2+-blue.svg)](https://docs.docker.com/compose/compose-file/compose-versioning/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**FBS FastAPI v3.0.0** is a modern, production-ready business suite built with FastAPI, featuring revolutionary module generation capabilities for Odoo integration.

## 🚀 Key Features

### ✨ Revolutionary Module Generation
- **Automated Odoo Module Creation**: Generate complete Odoo modules from specifications
- **Field Type Mappings**: Automatic conversion between data types
- **Workflow States**: Dynamic state management and transitions
- **Security Rules**: Automated access control and permissions
- **View Generation**: Complete form, list, and search views
- **ZIP Packaging**: Ready-to-install module packages

### 🏗️ Modern Architecture
- **FastAPI Framework**: Latest stable (0.115.6) with async support
- **Pydantic v2**: Modern data validation and configuration
- **SQLAlchemy 2.0**: Latest ORM with DeclarativeBase patterns
- **Async/Await**: Full asynchronous operations
- **Type Safety**: Complete type annotations throughout

### 📊 Business Intelligence
- **Comprehensive Dashboard**: Real-time business metrics
- **Multi-tenant Support**: Isolated solution environments
- **Compliance Management**: Tax and regulatory compliance
- **Accounting Integration**: Financial tracking and reporting
- **Workflow Automation**: Business process automation

## 🐳 Docker v2+ Setup (Recommended)

### Prerequisites
- Docker Engine v2+
- Docker Compose v2+
- At least 4GB RAM available
- PostgreSQL database access

### Quick Start with Docker

**Architecture: FBS FastAPI in Docker → Host Services (PostgreSQL, Redis, Odoo)**

1. **Prerequisites: Host Services**
```bash
# Ensure these services are running on host:
# - PostgreSQL on localhost:5432
# - Redis on localhost:6379
# - Odoo on localhost:8069 (optional)
```

2. **Clone and Setup**
```bash
git clone https://github.com/kuriadn/fbs.git
cd fbs
```

3. **Environment Configuration**
```bash
cp env_template.txt .env
# Edit .env with your host database and service configurations
# Docker will use host.docker.internal to access host services
```

4. **Docker Compose (Host Services Architecture)**
```yaml
# docker-compose.yml - FBS in Docker, Services on Host
version: '3.8'
services:
  fbs-fastapi:
    build:
      context: ./fbs_fastapi
      dockerfile: Dockerfile
    container_name: fbs-fastapi-app
    ports:
      - "8000:8000"
    environment:
      # Connect to host services via host.docker.internal
      - DATABASE_URL=postgresql+asyncpg://fbs_user:fbs_password@host.docker.internal:5432/fbs_system_db
      - REDIS_URL=redis://host.docker.internal:6379/0
      - ODOO_BASE_URL=http://host.docker.internal:8069
      - ENABLE_MODULE_GENERATION=true
    volumes:
      - ./fbs_fastapi/generated_modules:/app/generated_modules
    network_mode: host  # Access host services directly
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

5. **Build and Run**
```bash
# Build FBS FastAPI container
docker-compose build

# Start FBS (connects to host services)
docker-compose up -d

# View logs
docker-compose logs -f fbs-fastapi
```

6. **Access the Application**
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Module Generation**: http://localhost:8000/docs#/module_generation

**Note**: FBS FastAPI runs in Docker but connects to PostgreSQL, Redis, and Odoo running on the host machine via `host.docker.internal`.

## 🗄️ **Database Access Architecture**

FBS FastAPI uses `network_mode: host` in Docker to access host-based services:

### **Connection Details**
```yaml
# docker-compose.yml
services:
  fbs-fastapi:
    network_mode: host  # Direct host network access
    environment:
      - DATABASE_URL=postgresql+asyncpg://fbs_user:password@host.docker.internal:5432/fbs_system_db
      - REDIS_URL=redis://host.docker.internal:6379/0
      - ODOO_BASE_URL=http://host.docker.internal:8069
```

### **Host Service Requirements**
- **PostgreSQL**: Running on `localhost:5432`
- **Redis**: Running on `localhost:6379`
- **Odoo**: Running on `localhost:8069` (optional)
- **Nginx**: Running on `localhost:80/443` (optional)

### **Benefits**
- **Zero Network Overhead**: Direct access to host services
- **Data Persistence**: Database remains on host
- **Service Flexibility**: Easy management of host services
- **Performance**: No Docker networking latency

## 🛠️ Manual Installation

### Prerequisites
- Python 3.10+
- PostgreSQL database
- Redis server
- Odoo instance (optional, for module deployment)

### Installation Steps

1. **Clone Repository**
```bash
git clone https://github.com/kuriadn/fbs.git
cd fbs/fbs_fastapi
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r ../requirements.txt
pip install -r ../requirements-dev.txt
```

4. **Environment Configuration**
```bash
cp ../env_template.txt .env
# Edit .env with your configurations
```

5. **Database Setup**
```bash
# Create database
createdb fbs_system_db

# Run database migrations
alembic upgrade head
```

6. **Start the Application**
```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📖 Usage Guide

### 🔧 Module Generation

#### Create a Basic Module
```python
from fbs_fastapi.services.module_generation_service import ModuleSpec

# Define module specification
spec = ModuleSpec(
    name="custom_module",
    description="Custom business module",
    author="Your Organization",
    models=[
        {
            "name": "custom.model",
            "description": "Custom Model",
            "fields": [
                {"name": "name", "type": "char", "string": "Name", "required": True},
                {"name": "description", "type": "text", "string": "Description"},
                {"name": "amount", "type": "float", "string": "Amount"}
            ]
        }
    ],
    views=[
        {
            "name": "custom.model.form",
            "type": "form",
            "model": "custom.model",
            "fields": ["name", "description", "amount"]
        }
    ]
)

# Generate module
from fbs_fastapi.services.module_generation_service import FBSModuleGeneratorEngine

generator = FBSModuleGeneratorEngine()
module_path = generator.generate_module(spec)
print(f"Module generated at: {module_path}")
```

#### API Endpoint Usage
```bash
# Generate module via API
curl -X POST "http://localhost:8000/api/module-gen/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_module",
    "description": "My Custom Module",
    "author": "Developer",
    "models": [...],
    "workflows": [...],
    "security": {...}
  }'

# List available templates
curl "http://localhost:8000/api/module-gen/templates"

# Validate module specification
curl -X POST "http://localhost:8000/api/module-gen/validate" \
  -H "Content-Type: application/json" \
  -d '{"module_spec": {...}}'
```

### 🔐 Authentication

#### JWT Token Generation
```python
from fbs_fastapi.services.auth_service import AuthService

auth_service = AuthService("your_solution_name")
token = await auth_service.create_access_token(
    data={"sub": "user@example.com", "role": "admin"}
)
```

#### API Authentication
```bash
# Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "http://localhost:8000/api/protected/endpoint"
```

### 📊 Business Intelligence

#### Dashboard Data
```bash
# Get business metrics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/bi/dashboard"

# Generate reports
curl -X POST "http://localhost:8000/api/bi/reports" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"report_type": "financial", "date_range": {...}}'
```

### 📋 Document Management System (DMS)

#### Upload Document
```bash
curl -X POST "http://localhost:8000/api/dms/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "metadata={\"title\": \"Important Document\", \"tags\": [\"important\"]}"
```

#### Search Documents
```bash
curl "http://localhost:8000/api/dms/documents/search?q=important&tags=urgent"
```

### 🏢 License Management

#### Check License Status
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/license/status"
```

#### Validate Feature Access
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/license/features/module_generation"
```

## 🧪 Testing

### Run All Tests
```bash
# Activate virtual environment
source venv/bin/activate

# Run comprehensive test suite
python tests/run_all_tests.py

# Run specific test categories
pytest tests/unit/ -v
pytest tests/functional/ -v
pytest tests/integration/ -v
```

### Test Module Generation
```bash
# Run module generation tests
python tests/unit/test_module_generation_simple.py

# Run with pytest
pytest tests/unit/test_module_generation.py -v
```

## ⚙️ Configuration

### Environment Variables
```bash
# Application
APP_NAME="FBS - Fayvad Business Suite"
APP_VERSION="3.0.0"
DEBUG=false
SECRET_KEY="your-secret-key-here"

# Database
DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/fbs_db"
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Odoo Integration
ODOO_BASE_URL="http://localhost:8069"
ODOO_TIMEOUT=30
ODOO_USER="odoo"
ODOO_PASSWORD="your-odoo-password"

# Caching
REDIS_URL="redis://localhost:6379/0"
CACHE_TIMEOUT=300
CACHE_ENABLED=true

# Module Generation
ENABLE_MODULE_GENERATION=true
MODULE_OUTPUT_DIR="./generated_modules"
MODULE_TEMPLATE_DIR="./templates"

# CORS
CORS_ORIGINS="http://localhost:3000,http://localhost:8000"
```

### Advanced Configuration

#### Custom Module Templates
```python
# Create custom templates in templates/ directory
# Structure:
# templates/
#   ├── __manifest__.py.jinja
#   ├── models/
#   │   └── model.py.jinja
#   ├── views/
#   │   └── form.xml.jinja
#   └── security/
#       └── ir.model.access.csv.jinja
```

#### Database Configuration
```python
# Custom database configuration
from fbs_fastapi.core.database import create_engine

engine = create_engine(
    "postgresql+asyncpg://user:pass@host:port/db",
    pool_size=20,
    max_overflow=30,
    echo=False
)
```

## 🔌 API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `GET /openapi.json` - OpenAPI specification

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Token refresh
- `POST /api/auth/logout` - User logout

### Module Generation (v3.0.0)
- `GET /api/module-gen/templates` - List templates
- `POST /api/module-gen/validate` - Validate specification
- `POST /api/module-gen/generate` - Generate module
- `POST /api/module-gen/generate-and-install` - Generate and install
- `GET /api/module-gen/generated` - List generated modules
- `GET /api/module-gen/history` - Generation history

### Business Intelligence
- `GET /api/bi/dashboard` - Dashboard data
- `POST /api/bi/reports` - Generate reports
- `GET /api/bi/analytics` - Analytics data

### Document Management
- `POST /api/dms/documents` - Upload document
- `GET /api/dms/documents` - List documents
- `GET /api/dms/documents/{id}` - Get document
- `DELETE /api/dms/documents/{id}` - Delete document

### License Management
- `GET /api/license/status` - License status
- `POST /api/license/validate` - Validate license
- `GET /api/license/features/{feature}` - Check feature access

## 🏗️ Architecture

### Service Layer Pattern
```
fbs_fastapi/
├── core/           # Core functionality
│   ├── config.py   # Configuration management
│   ├── database.py # Database connections
│   └── middleware.py # Request middleware
├── services/       # Business logic
│   ├── auth_service.py
│   ├── module_generation_service.py
│   ├── dms_service.py
│   └── license_service.py
├── models/         # Data models
├── routers/        # API endpoints
├── templates/      # Module templates
└── tests/          # Test suite
```

### Key Components
- **FBSConfig**: Pydantic-based configuration
- **DeclarativeBase**: SQLAlchemy 2.0 models
- **FBSModuleGeneratorEngine**: Module generation engine
- **Service Interfaces**: Clean business logic separation
- **Async Dependencies**: Modern async patterns

## 📈 Performance

### Optimization Features
- **Async Database Operations**: SQLAlchemy 2.0 async support
- **Connection Pooling**: Efficient database connections
- **Redis Caching**: Fast data caching
- **Background Tasks**: Non-blocking operations
- **Pagination**: Efficient data retrieval

### Docker Performance
```yaml
# Optimized Docker configuration
services:
  fbs-fastapi:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

## 🔒 Security

### Security Features
- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Cross-origin request protection
- **Input Validation**: Pydantic data validation
- **SQL Injection Protection**: Parameterized queries
- **Rate Limiting**: Request rate protection
- **HTTPS Enforcement**: Secure connections

### Best Practices
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Regular security updates
- Monitor for vulnerabilities
- Implement proper logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python tests/run_all_tests.py`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: https://fbs-fastapi.readthedocs.io/
- **Issues**: https://github.com/kuriadn/fbs/issues
- **Discussions**: https://github.com/kuriadn/fbs/discussions

## 🎯 Roadmap

### v3.1.0 (Upcoming)
- Enhanced module templates
- Advanced workflow engine
- Multi-language support
- API rate limiting improvements

### v3.2.0 (Future)
- GraphQL API support
- Real-time notifications
- Advanced analytics
- Mobile app integration

---

**FBS FastAPI v3.0.0** - Revolutionizing business suite development with automated module generation! 🚀