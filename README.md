# FBS FastAPI v3.1.0 - Fayvad Business Suite

**Copyright © 2025 Fayvad Digital. All rights reserved.**

[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](https://github.com/kuriadn/fbs)
[![Docker](https://img.shields.io/badge/docker-v2+-blue.svg)](https://docs.docker.com/compose/compose-file/compose-versioning/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green.svg)](https://fastapi.tiangolo.com)

## 🎯 Overview

**FBS FastAPI v3.1.0** is a revolutionary, production-ready business suite built with modern FastAPI, featuring automated module generation capabilities for seamless Odoo integration. This is a complete modernization of the FBS platform with cutting-edge technology and enhanced business intelligence.

**Version 3.1.0** introduces groundbreaking module generation technology that automates Odoo module creation, along with a complete migration to modern FastAPI architecture with async support, Pydantic v2, and SQLAlchemy 2.0. This release includes enhanced embeddability patterns and comprehensive Docker support.

**FBS is designed as a modern business platform** - providing both standalone capabilities and seamless Odoo integration through automated module generation. When deployed, it serves as a powerful foundation for custom business solutions with **automated Odoo module creation and deployment**.

## 🗄️ **Database Architecture**

**FBS FastAPI v3.1.0 uses a hybrid deployment model:**

### **Containerized Application + Host Services**
```
┌─────────────────┐     ┌─────────────────┐
│   Host Machine  │     │   Docker        │
│   (Services)    │◄────┤   Container     │
├─────────────────┤     ├─────────────────┤
│ • PostgreSQL    │     │ • FBS FastAPI   │
│   (localhost)   │     │   (Container)   │
│ • Redis         │     │                 │
│   (localhost)   │     │ • Module Gen    │
│ • Odoo          │     │ • Static Files  │
│   (localhost)   │     │ • API Endpoints │
│ • Nginx         │     └─────────────────┘
│   (localhost)   │
└─────────────────┘
```

**Why this architecture?**
- **Database Persistence**: PostgreSQL runs on host for data persistence
- **Service Flexibility**: Redis, Odoo, Nginx on host for easy management
- **Application Isolation**: FBS FastAPI in Docker for easy deployment
- **Network Access**: Uses `host.docker.internal` for seamless connectivity

## ✨ Core Capabilities

### 🚀 **Revolutionary Module Generation (v3.0.0)**
- **Automated Odoo Module Creation**: Generate complete modules from specifications
- **Field Type Mappings**: Automatic conversion between data types
- **Workflow States**: Dynamic state management and transitions
- **Security Rules**: Automated access control and permissions
- **View Generation**: Complete form, list, and search views
- **ZIP Packaging**: Ready-to-install module packages

### 🏗️ **Modern FastAPI Architecture**
- **FastAPI Framework**: Latest stable (0.115.6) with async support
- **Pydantic v2**: Modern data validation and configuration
- **SQLAlchemy 2.0**: Latest ORM with DeclarativeBase patterns
- **Async/Await**: Full asynchronous operations
- **Type Safety**: Complete type annotations throughout

### 🔗 **Advanced Odoo Integration**
- **Complete CRUD Operations**: Full create, read, update, delete for any Odoo model
- **Dynamic Model Discovery**: Automatically discovers and maps Odoo models, fields, and modules
- **Module Management**: Install, uninstall, and manage Odoo modules programmatically
- **Automated Module Deployment**: Generate and deploy modules via API
- **XML-RPC Client**: Robust, error-handling Odoo communication layer

### ⚡ **Sophisticated Workflow Engine**
- **State Machine Workflows**: Complete workflow definitions with steps, transitions, and conditions
- **Approval Systems**: Multi-level approval workflows with request/response tracking
- **Business Rule Engine**: Configurable business rules with conditions and actions
- **Workflow Analytics**: Track performance, bottlenecks, and completion rates

### 📊 **Enterprise Business Intelligence**
- **Interactive Dashboards**: Configurable dashboard layouts with multiple chart types
- **Dynamic Reporting**: Scheduled reports in multiple formats (PDF, Excel, CSV, JSON, HTML)
- **Advanced KPI Management**: Real-time KPI tracking with thresholds and alerting
- **Business Analytics**: Deep insights into business performance and trends

### 🏢 **Complete MSME Management**
- **Setup Wizard**: Guided business configuration and onboarding
- **Industry Templates**: Pre-configured setups for retail, manufacturing, services
- **Marketing Management**: Campaign tracking and customer engagement tools
- **Compliance Tracking**: Automated compliance monitoring and deadline management

### 💰 **Comprehensive Accounting**
- **Cash Basis Accounting**: Complete income/expense tracking with categorization
- **Basic Ledger**: Double-entry bookkeeping with account management
- **Tax Calculations**: Automated tax computation with multiple tax types
- **Recurring Transactions**: Automated recurring income/expense handling
- **Financial Health Indicators**: Real-time financial position analysis

### 🔐 **Enterprise Security & Authentication**
- **JWT Authentication**: Secure token-based authentication with expiry management
- **Handshake Authentication**: Secure token-based authentication with expiry management
- **Request Logging**: Comprehensive audit trails with performance metrics
- **Role-Based Access**: Fine-grained permission control

### 📱 **Multi-Tenant Architecture**
- **Solution Isolation**: Complete data separation between different business solutions
- **Dynamic Database Creation**: Automatic database provisioning for new solutions
- **Middleware Routing**: Intelligent request routing based on solution context
- **Cache Management**: Solution-specific caching with automatic cleanup

## 🏗️ Architecture

FBS FastAPI v3.0.0 follows a **modern, service-oriented architecture** with **automated module generation and Odoo integration**:

### **Project Structure**
```
┌─────────────────────────────────────────────────────────────┐
│              FBS FastAPI v3.0.0 Project                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   FastAPI Core  │  │  FBS Services   │  │  Templates  │ │
│  │                 │  │                 │  │             │ │
│  │ • Main App      │  │ • Auth Service  │  │ • Module     │ │
│  │ • Routing       │  │ • Module Gen    │  │ • Templates  │ │
│  │ • Middleware    │  │ • DMS Service   │  │ • Views      │ │
│  │ └─────────────────┘  │ • BI Service   │  └─────────────┘ │
│                        │ • License Mgmt  │                 │
│                        └─────────────────┘                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   SQLAlchemy    │  │   Pydantic v2   │  │   Redis     │ │
│  │   2.0 Models    │  │   Config        │  │   Cache     │ │
│  │                 │  │                 │  │             │ │
│  │ • DeclarativeBase│  │ • ConfigDict   │  │ • Sessions  │ │
│  │ • Async Support  │  │ • Validation   │  │ • TTL       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Odoo ERP      │
                       │ (Primary Data)  │
                       │                 │
                       │ • Auto-generated│
                       │   Modules       │
                       │ • Custom Models │
                       │ • Workflows     │
                       │ • Views         │
                       └─────────────────┘
```

### **Key Components**
- **FastAPI Core**: Main application with routing and middleware
- **Service Layer**: Business logic encapsulated in async service classes
- **Module Generation Engine**: Automated Odoo module creation system
- **SQLAlchemy 2.0 Models**: DeclarativeBase with async support
- **Pydantic v2 Config**: Modern configuration with ConfigDict patterns
- **Template System**: Jinja2-based module generation templates
- **Redis Cache**: High-performance caching layer
- **JWT Authentication**: Secure token-based authentication

## 🚀 Quick Start

### **Option 1: Docker v2+ Setup (Recommended)**

**Architecture: FBS in Docker → Host Services (PostgreSQL, Redis, Odoo, Nginx)**

```bash
# Prerequisites: Ensure host services are running
# PostgreSQL on host:5432, Redis on host:6379, Odoo on host:8069

# Clone the repository
git clone https://github.com/kuriadn/fbs.git
cd fbs

# Start FBS FastAPI in Docker (connects to host services)
docker-compose up -d

# View logs
docker-compose logs -f fbs-fastapi

# Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

**Host Services Setup:**
```bash
# PostgreSQL (host)
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser fbs_user
sudo -u postgres createdb fbs_system_db -O fbs_user

# Redis (host)
sudo apt install redis-server

# Odoo (host) - if needed
# Install and configure Odoo on host:8069

# Nginx (host) - optional reverse proxy
sudo apt install nginx
```

**📖 For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

### **Option 2: Manual Installation**

#### **Prerequisites**
- Python 3.10+
- PostgreSQL database
- Redis server
- Odoo instance (optional, for module deployment)

### **Installation**

```bash
# Clone the repository
git clone https://github.com/kuriadn/fbs.git
cd fbs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt
pip install -r ../requirements-dev.txt
```

### **Basic Usage**

```python
from fbs_fastapi.services.module_generation_service import ModuleSpec, FBSModuleGeneratorEngine

# Create module specification
spec = ModuleSpec(
    name="my_custom_module",
    description="Custom business module",
    author="Your Organization",
    models=[
        {
            "name": "my.model",
            "description": "Custom Model",
            "fields": [
                {"name": "name", "type": "char", "string": "Name", "required": True},
                {"name": "amount", "type": "float", "string": "Amount"}
            ]
        }
    ]
)

# Generate module
generator = FBSModuleGeneratorEngine()
module_path = generator.generate_module(spec)
print(f"Module generated: {module_path}")
```

### **API Usage**

```python
import httpx

# Generate module via API
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/module-gen/generate",
        json={
            "name": "api_module",
            "description": "API Generated Module",
            "author": "API User",
            "models": [...]
        }
    )
    result = response.json()
    print(f"Module created: {result['module_path']}")
```

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - How to install and configure FBS
- **[Integration Guide](docs/INTEGRATION.md)** - How to embed FBS in your Django projects
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)** - Service interfaces and usage patterns
- **[Odoo Integration](docs/ODOO_INTEGRATION.md)** - Odoo + Virtual Fields usage
- **[API Reference](docs/API_REFERENCE.md)** - Current service interfaces

## 🔧 Configuration

### **Django Settings**

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # FBS Apps
    'fbs_app',                    # Core business suite
    'fbs_dms',                    # Document management
    'fbs_license_manager',        # License management
]

# FBS Configuration
FBS_APP = {
    'ODOO_BASE_URL': 'http://your-odoo-server:8069',
    'ODOO_TIMEOUT': 30,
    'ODOO_MAX_RETRIES': 3,
    'DATABASE_USER': 'your_odoo_user',
    'DATABASE_PASSWORD': 'your_odoo_password',
}
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
pytest --cov=fbs_app --cov=fbs_dms --cov=fbs_license_manager

# Run specific app tests
python manage.py test fbs_app
python manage.py test fbs_dms
python manage.py test fbs_license_manager
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is proprietary software. All rights reserved by Fayvad Digital.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team
- Check the documentation for common solutions

---

**FBS: Transform your Django projects into Odoo-powered business solutions with FBS Virtual Fields technology.**
