# FBS (Fayvad Business Suite) - Odoo-Driven Business Platform

**Copyright © 2025 Fayvad Digital. All rights reserved.**

## 🎯 Overview

**FBS (Fayvad Business Suite)** is a sophisticated, embeddable Django application that serves as a comprehensive business management platform for MSMEs (Micro, Small, and Medium Enterprises). FBS is a **full-featured business intelligence and automation engine** that integrates seamlessly with Odoo ERP while providing extensive standalone capabilities.

**FBS is designed as an embedding engine** - not the final solution itself, but the powerful foundation that drives custom business solutions. When embedded into Django projects, it transforms them into feature-rich business management platforms with **Odoo as the primary data store**.

## ✨ Core Capabilities

### 🏗️ **Odoo-Driven Architecture**
- **Primary Data Storage**: Odoo ERP serves as the main data repository
- **FBS Virtual Fields**: Extend Odoo models with custom data without modifying Odoo
- **Django UI Layer**: Django models serve as UI references and business logic
- **Hybrid Data Model**: Odoo + Virtual Fields + Django UI for maximum flexibility

### 🔗 **Advanced Odoo Integration**
- **Complete CRUD Operations**: Full create, read, update, delete for any Odoo model
- **Dynamic Model Discovery**: Automatically discovers and maps Odoo models, fields, and modules
- **Module Management**: Install, uninstall, and manage Odoo modules programmatically
- **Field Merging**: Seamlessly merge Odoo data with FBS virtual fields
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
- **Handshake Authentication**: Secure token-based authentication with expiry management
- **Token Mapping**: Sophisticated user-database token management
- **Request Logging**: Comprehensive audit trails with performance metrics
- **Role-Based Access**: Fine-grained permission control

### 📱 **Multi-Tenant Architecture**
- **Solution Isolation**: Complete data separation between different business solutions
- **Dynamic Database Creation**: Automatic database provisioning for new solutions
- **Middleware Routing**: Intelligent request routing based on solution context
- **Cache Management**: Solution-specific caching with automatic cleanup

## 🏗️ Architecture

The FBS project follows a **clean, service-oriented architecture** with **Odoo as the primary data store**:

### **Project Structure**
```
┌─────────────────────────────────────────────────────────────┐
│                    FBS Project (fbs_project/)              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Django Core   │  │    FBS App      │  │  Other Apps │ │
│  │                 │  │   (fbs_app/)    │  │             │ │
│  │ • Settings      │  │ • Service Layer │  │ • Blog      │ │
│  │ • URL Routing   │  │ • Interface     │  │ • E-commerce│ │
│  │ • Configuration │  │ • Models        │  │ • etc.      │ │
│  └─────────────────┘  │ • Admin         │  └─────────────┘ │
│                       │ • Commands      │                 │
│                       └─────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Odoo ERP      │
                       │ (Primary Data)  │
                       │                 │
                       │ • ir.attachment │
                       │ • res.partner   │
                       │ • res.company   │
                       │ • + Virtual     │
                       │   Fields        │
                       └─────────────────┘
```

### **Key Components**
- **Project Level**: Configuration, routing, and project-wide settings
- **App Level**: Business logic, models, services, and app-specific functionality
- **Service Layer**: Business logic encapsulated in service classes
- **Interface Layer**: Clean service interfaces for accessing business capabilities
- **Model Layer**: Django models with business logic methods (UI references)
- **Admin Interface**: Django admin for data management
- **Management Commands**: CLI interfaces for administrative tasks
- **Signals**: Event-driven functionality for business processes

## 🚀 Quick Start

### **Installation**

```bash
# Clone the repository
git clone https://github.com/kuriadn/fbs.git
cd fbs

# Install in development mode
pip install -e .
```

### **Basic Usage**

```python
from fbs_app.interfaces import FBSInterface

# Initialize FBS interface
fbs = FBSInterface('your_solution_name')

# Access Odoo integration
models = fbs.odoo.discover_models()
records = fbs.odoo.get_records('res.partner')

# Access MSME capabilities
dashboard = fbs.msme.get_dashboard()
kpis = fbs.msme.calculate_kpis()

# Access virtual fields
custom_data = fbs.fields.get_custom_fields('res.partner', 1)
fbs.fields.set_custom_field('res.partner', 1, 'custom_field', 'value')
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
