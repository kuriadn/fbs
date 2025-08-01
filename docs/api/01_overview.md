# 01. FBS API Overview 📚

## Introduction

The **FBS (Fayvad Business System) API** provides a comprehensive REST API for integrating with Odoo systems, managing workflows, business intelligence, and enterprise operations. This API serves as the backbone for building scalable business applications that can dynamically adapt to different industries and business domains.

## 🎯 Key Features

### **Dynamic Model Discovery**
- **Automatic Model Detection**: Discovers all available Odoo models and their capabilities
- **Field Analysis**: Analyzes model fields, relationships, and constraints
- **Workflow Detection**: Identifies state machines and workflow patterns
- **BI Feature Discovery**: Finds available reports, dashboards, and KPIs

### **Multi-Tenant Architecture**
- **Database Isolation**: Each client gets their own isolated database
- **Schema Management**: Dynamic schema creation and migration
- **Resource Allocation**: Efficient resource management across tenants
- **Security Isolation**: Complete data separation between clients

### **Business Domain Intelligence**
- **Industry Mapping**: Maps business requirements to appropriate modules
- **Capability Resolution**: Automatically resolves dependencies and requirements
- **Domain-Specific APIs**: Generates APIs tailored to business domains
- **Workflow Automation**: Creates and manages business process workflows

### **Real-Time Analytics**
- **Live Dashboards**: Real-time business intelligence dashboards
- **KPI Tracking**: Key Performance Indicators with automated calculations
- **Report Generation**: Dynamic report creation and scheduling
- **Data Visualization**: Interactive charts and graphs

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FBS API       │    │   Odoo System   │
│   Applications  │◄──►│   Gateway       │◄──►│   (Multiple     │
│                 │    │                 │    │   Databases)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Discovery     │
                       │   Engine        │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Schema        │
                       │   Manager       │
                       └─────────────────┘
```

## 📊 API Categories

### **1. Core Operations** (`02_core_operations.md`)
- **Generic Model Operations**: CRUD operations for any Odoo model
- **Database Management**: Multi-tenant database operations
- **Token Management**: API token handling and authentication
- **Schema Operations**: Dynamic schema creation and management

### **2. Discovery & Profiling** (`03_discovery_profiling.md`)
- **Model Discovery**: Discover available Odoo models with metadata
- **Workflow Discovery**: Find applicable workflows for models
- **BI Feature Discovery**: Discover available KPIs and dashboards
- **Capability Analysis**: Analyze model capabilities and relationships

### **3. Authentication & Security** (`04_authentication.md`)
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Fine-grained permission control
- **API Key Management**: Secure API key handling
- **Rate Limiting**: Request throttling and protection

### **4. Business Endpoints** (`05_business_endpoints.md`)
- **Domain-Specific APIs**: Industry-specific endpoint generation
- **Workflow Management**: Business process automation
- **Business Logic**: Complex multi-step operations
- **Validation Rules**: Business rule enforcement

### **5. Business Intelligence** (`06_business_intelligence.md`)
- **Analytics Engine**: Real-time analytics and reporting
- **Dashboard API**: Dynamic dashboard data retrieval
- **KPI Management**: Key Performance Indicators
- **Report Generation**: Automated report creation

### **6. Error Handling** (`07_error_handling.md`)
- **Error Codes**: Comprehensive error code system
- **Validation Errors**: Input validation and error messages
- **Business Logic Errors**: Domain-specific error handling
- **Debugging Support**: Detailed error information

### **7. Integration Examples** (`08_integration_examples.md`)
- **Frontend Integration**: React, Vue, Angular examples
- **Mobile Integration**: iOS and Android examples
- **Third-Party Integration**: Webhook and API integration
- **Real-World Scenarios**: Complete application examples

### **8. WebSocket API** (`09_websocket_api.md`)
- **Real-Time Updates**: Live data synchronization
- **Event Streaming**: Business event streaming
- **Push Notifications**: Real-time notifications
- **Collaborative Features**: Multi-user collaboration

## 🚀 Quick Start Guide

### **1. Authentication Setup**
```bash
# Get authentication token
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'
```

### **2. Discover Available Models**
```bash
# List all available models
curl -X GET "http://localhost:8001/api/profile/models/?db=your_database" \
  -H "Authorization: Bearer <your_token>"
```

### **3. Retrieve Model Data**
```bash
# Get employee records
curl -X GET "http://localhost:8001/api/v1/hr.employee/?limit=10" \
  -H "Authorization: Bearer <your_token>"
```

### **4. Create Business Workflow**
```bash
# Create approval workflow
curl -X POST "http://localhost:8001/api/workflows/" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "expense_approval",
    "model": "hr.expense",
    "states": ["draft", "submitted", "approved", "paid"],
    "transitions": [
      {"from": "draft", "to": "submitted"},
      {"from": "submitted", "to": "approved"},
      {"from": "approved", "to": "paid"}
    ]
  }'
```

## 📋 Response Format Standards

### **Success Response**
```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Optional success message",
  "error": null,
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### **Error Response**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  },
  "data": null,
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

## 🔧 Configuration

### **Environment Variables**
```bash
# API Configuration
FBS_API_HOST=localhost
FBS_API_PORT=8001
FBS_API_DEBUG=true

# Database Configuration
FBS_DB_HOST=localhost
FBS_DB_PORT=5432
FBS_DB_NAME=fbs_main
FBS_DB_USER=fayvad
FBS_DB_PASSWORD=secure_password

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=fayvad
ODOO_USER=admin
ODOO_PASSWORD=admin

# Security Configuration
JWT_SECRET_KEY=your_jwt_secret_key
JWT_EXPIRATION_HOURS=24
API_RATE_LIMIT=1000
```

### **Rate Limiting**
| Endpoint Category | Requests/Hour | Burst Limit |
|------------------|---------------|-------------|
| **Core Operations** | 1,000 | 100 |
| **Discovery** | 100 | 10 |
| **Workflows** | 500 | 50 |
| **Analytics** | 200 | 20 |
| **File Upload** | 50 | 5 |

### **Caching Strategy**
| Data Type | Cache Duration | Invalidation |
|-----------|----------------|--------------|
| **Model Metadata** | 5 minutes | On schema change |
| **Discovery Results** | 15 minutes | On module install |
| **Report Data** | 30 minutes | On data update |
| **User Sessions** | 24 hours | On logout |

## 📝 HTTP Status Codes

| Code | Category | Description |
|------|----------|-------------|
| **200** | Success | Request completed successfully |
| **201** | Created | Resource created successfully |
| **204** | No Content | Request completed, no response body |
| **400** | Bad Request | Invalid parameters or request format |
| **401** | Unauthorized | Authentication required or failed |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Resource conflict (e.g., duplicate) |
| **422** | Validation Error | Business logic validation failed |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Error | Server error |
| **503** | Service Unavailable | Service temporarily unavailable |

## 🔗 Related Documentation

- **[02. Core Operations](./02_core_operations.md)** - Basic CRUD operations
- **[03. Discovery & Profiling](./03_discovery_profiling.md)** - Model and capability discovery
- **[04. Authentication](./04_authentication.md)** - Security and authentication
- **[05. Business Endpoints](./05_business_endpoints.md)** - Domain-specific APIs
- **[06. Business Intelligence](./06_business_intelligence.md)** - Analytics and reporting
- **[07. Error Handling](./07_error_handling.md)** - Error codes and handling
- **[08. Integration Examples](./08_integration_examples.md)** - Implementation examples
- **[09. WebSocket API](./09_websocket_api.md)** - Real-time communication

## 📞 Support & Resources

### **Technical Support**
- **Email**: api-support@fayvad.com
- **Documentation**: https://docs.fayvad.com/api
- **Status Page**: https://status.fayvad.com
- **Community Forum**: https://community.fayvad.com

### **Development Resources**
- **API Playground**: https://api.fayvad.com/playground
- **SDK Downloads**: https://github.com/fayvad/fbs-sdk
- **Code Examples**: https://github.com/fayvad/fbs-examples
- **Video Tutorials**: https://youtube.com/fayvad-api

### **Enterprise Support**
- **24/7 Support**: enterprise-support@fayvad.com
- **Dedicated Account Manager**: Available for enterprise clients
- **Custom Integration**: Professional services for complex integrations
- **Training Programs**: On-site and online training available 