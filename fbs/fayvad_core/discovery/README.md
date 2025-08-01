# FBS Discovery & Schema Management System 🚀

Complete discovery and schema management solution for the FBS Generic Odoo API system. This module provides persistent discovery, dynamic schema creation, and multi-tenant schema isolation.

## 🎯 Overview

The FBS Discovery & Schema Management System solves the core issues of:
- **Repeated API calls** for model/workflow discovery
- **Test database setup failures** due to missing schema
- **Manual table creation** requirements for each solution
- **Inconsistent schema management** across solutions
- **No multi-tenant schema support**
- **Dynamic database creation** for each solution
- **Odoo integration** using the same database

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FBS Discovery System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Discovery   │  │ Schema      │  │ Integration │        │
│  │ Service     │  │ Service     │  │ Service     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ API Views   │  │ Admin       │  │ Management  │        │
│  │ & Endpoints │  │ Interface   │  │ Commands    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. **Discovery Service** (`services.py`)
- **Model Discovery**: Discovers Odoo models via XML-RPC
- **Workflow Discovery**: Discovers workflow definitions
- **BI Feature Discovery**: Discovers business intelligence features
- **Caching**: Persists discoveries in database
- **Domain Filtering**: Filters discoveries by business domain

### 2. **Schema Service** (`schema_service.py`)
- **Dynamic Table Creation**: Creates PostgreSQL tables from discoveries
- **Schema Generation**: Converts Odoo models to SQL schemas
- **Migration Management**: Handles schema evolution
- **Multi-tenant Support**: Isolates schemas per solution

### 3. **Integration Service** (`integration_service.py`)
- **Solution Setup**: Complete solution initialization
- **Status Monitoring**: Solution health checks
- **Configuration Validation**: Validates solution configs
- **Discovery Management**: Manages discovery lifecycle

## 📊 Database Schema

### **FBSDiscovery** Table
```sql
CREATE TABLE fbs_discoveries (
    id SERIAL PRIMARY KEY,
    discovery_type VARCHAR(50) NOT NULL, -- 'model', 'workflow', 'bi_feature'
    domain VARCHAR(100) NOT NULL, -- 'rental', 'inventory', 'sales'
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) DEFAULT '1.0',
    metadata JSONB NOT NULL,
    schema_definition JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    discovered_at TIMESTAMP DEFAULT NOW()
);
```

### **FBSSolutionSchema** Table
```sql
CREATE TABLE fbs_solution_schemas (
    id SERIAL PRIMARY KEY,
    solution_name VARCHAR(100) NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    database_user VARCHAR(100) NOT NULL,
    database_password VARCHAR(255) NOT NULL,
    schema_version VARCHAR(20) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **FBSSchemaMigration** Table
```sql
CREATE TABLE fbs_schema_migrations (
    id SERIAL PRIMARY KEY,
    solution_name VARCHAR(100) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    migration_type VARCHAR(50) NOT NULL, -- 'create', 'alter', 'drop'
    old_schema JSONB,
    new_schema JSONB,
    executed_at TIMESTAMP DEFAULT NOW(),
    executed_by VARCHAR(100),
    status VARCHAR(20) DEFAULT 'success'
);
```

## 🚀 API Endpoints

### **Discovery Management**
- `GET /api/v1/discoveries/{domain}/{type}/` - Get cached discoveries
- `POST /api/v1/discoveries/{domain}/{type}/` - Refresh discoveries

### **Solution Management**
- `POST /api/v1/solutions/setup/` - Setup complete solution
- `GET /api/v1/solutions/{name}/status/` - Get solution status
- `POST /api/v1/solutions/{name}/migrate/` - Migrate solution schema
- `GET /api/v1/solutions/{name}/discoveries/` - Get solution discoveries
- `POST /api/v1/solutions/{name}/discoveries/` - Refresh solution discoveries
- `GET /api/v1/solutions/` - List all solutions

### **Health Check**
- `GET /api/v1/health/` - System health check

## 💻 Usage Examples

### **Basic Discovery**
```python
from fayvad_core.discovery import FBSDiscoveryService

# Initialize service
discovery_service = FBSDiscoveryService()

# Discover models for rental domain
result = discovery_service.discover_and_cache('rental', 'model')
print(f"Discovered {result['discovered_count']} models")

# Get cached discoveries
models = discovery_service.get_cached_discoveries('rental', 'model')
for model in models:
    print(f"- {model['name']}: {model['metadata']}")
```

### **Solution Setup**
```python
from fayvad_core.discovery import FBSAPIIntegrationService

# Initialize integration service
integration_service = FBSAPIIntegrationService()

# Setup rental solution (creates fbs_fayvad_rentals_db)
solution_config = {
    'solution_name': 'fayvad_rentals',
    'domain': 'rental',
    'database_config': {
        'user': 'postgres',
        'password': 'postgres',
        'host': 'localhost',
        'port': '5432'
    },
    'table_prefix': 'fbs_',
    'business_prefix': 'rental_',
    'refresh_discoveries': True
}

result = integration_service.setup_solution(solution_config)
if result['status'] == 'success':
    print(f"Solution setup complete: {result['database']}")
    print(f"Tables created: {result['schema_result']['total_tables']}")
```

### **Solution Status**
```python
# Get solution status
status = integration_service.get_solution_status('fayvad_rentals')
print(f"Status: {status['overall_status']}")
print(f"Database: {status['schema_status']['database_status']}")
```

## 🔧 Management Commands

### **Test Discovery System**
```bash
# Test discovery for rental domain (creates fbs_testing_db)
python manage.py test_discovery --action discover --domain rental --solution-name testing

# Test solution setup (creates fbs_fayvad_rentals_test_db)
python manage.py test_discovery --action setup --solution-name fayvad_rentals_test --domain rental

# Test solution status
python manage.py test_discovery --action status --solution-name fayvad_rentals_test

# List all solutions
python manage.py test_discovery --action list
```

## 🌐 API Examples

### **Setup Solution**
```bash
curl -X POST http://localhost:8000/api/v1/solutions/setup/ \
  -H "Content-Type: application/json" \
  -d '{
    "solution_name": "fayvad_rentals",
    "domain": "rental",
    "database_config": {
        "user": "postgres",
        "password": "postgres",
        "host": "localhost",
        "port": "5432"
    },
    "table_prefix": "fbs_",
    "business_prefix": "rental_",
    "refresh_discoveries": true
  }'
```

### **Get Solution Status**
```bash
curl -X GET http://localhost:8000/api/v1/solutions/fayvad_rentals/status/
```

### **Refresh Discoveries**
```bash
curl -X POST http://localhost:8000/api/v1/discoveries/rental/model/ \
  -H "Content-Type: application/json" \
  -d '{"database": "fayvad_production"}'
```

## 🔒 Security Considerations

### **Database Security**
- **Encrypted Passwords**: Database passwords should be encrypted in production
- **Connection Security**: Use SSL/TLS for database connections
- **Access Control**: Implement role-based access to schema creation

### **API Security**
- **Authentication**: Enable authentication for production endpoints
- **Rate Limiting**: Implement rate limiting on discovery endpoints
- **Input Validation**: All inputs are validated before processing

## 📈 Monitoring & Analytics

### **Health Metrics**
- **Discovery Success Rate**: Track successful vs failed discoveries
- **Schema Creation Rate**: Monitor table creation success
- **Migration Success Rate**: Track schema migration success
- **API Response Times**: Monitor endpoint performance

### **Audit Trail**
- **Discovery Events**: Log all discovery operations
- **Schema Changes**: Track all schema modifications
- **Migration History**: Complete migration audit trail
- **User Actions**: Track user-initiated operations

## 🚀 Deployment

### **Environment Variables**
```bash
# FBS Database Configuration
FBS_DB_NAME=fbs_metadata
FBS_DB_USER=fbs_user
FBS_DB_PASSWORD=fbs_password
FBS_DB_HOST=localhost
FBS_DB_PORT=5432

# Odoo Integration
ODOO_USER=odoo
ODOO_PASSWORD=four@One2
ODOO_BASE_URL=http://localhost:8069
ODOO_DATABASE=fayvad_production

# FBS API Configuration
FBS_API_BASE_URL=http://localhost:8000
```

### **Dependencies**
```bash
# Install required packages
pip install psycopg2-binary
pip install PyJWT
pip install requests
```

## 🔧 Configuration

### **Settings Configuration**
```python
# settings.py
ODOO_USER = 'odoo'
ODOO_PASSWORD = 'four@One2'
ODOO_BASE_URL = 'http://localhost:8069'
ODOO_DATABASE = 'fayvad_production'

# Database configuration
DB_HOST = 'localhost'
DB_PORT = '5432'
```

## 📚 Troubleshooting

### **Common Issues**

1. **Discovery Fails**
   - Check Odoo connection and credentials
   - Verify Odoo database exists and is accessible
   - Check XML-RPC endpoint availability

2. **Schema Creation Fails**
   - Verify PostgreSQL connection
   - Check database user permissions
   - Ensure database exists

3. **API Endpoints Not Working**
   - Check Django server is running
   - Verify URL configuration
   - Check authentication settings

### **Debug Mode**
```python
# Enable debug logging
import logging
logging.getLogger('fayvad_core.discovery').setLevel(logging.DEBUG)
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Add tests**
5. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎉 The FBS Discovery & Schema Management System provides a robust foundation for building scalable, multi-tenant Odoo solutions!** 