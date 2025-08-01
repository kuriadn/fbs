# 🎯 FBS Single Database Approach

## Overview

The FBS Discovery & Schema Management System now supports a **single database approach** where both FBS system tables and business tables are created in the user's specified database with clear table prefixes for separation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Single Database Architecture             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              User-Specified Database                   │ │
│  │                                                         │ │
│  │  ┌─────────────────┐  ┌─────────────────┐              │ │
│  │  │   FBS System    │  │   Business      │              │ │
│  │  │   Tables        │  │   Tables        │              │ │
│  │  │                 │  │                 │              │ │
│  │  │ • fbs_discoveries│  │ • rental_property│            │ │
│  │  │ • fbs_schemas   │  │ • rental_lease  │              │ │
│  │  │ • fbs_migrations│  │ • rental_tenant │              │ │
│  │  │ • fbs_workflows │  │ • rental_payment│              │ │
│  │  │ • fbs_bi_dashboards│ │ • rental_maintenance│        │ │
│  │  └─────────────────┘  └─────────────────┘              │ │
│  └─────────────────────────────────────────────────────────┘ │
│         ✅ One database, complete control                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Setup a Rental Solution

```bash
# Create rental database
createdb rental_db

# Setup FBS solution
python manage.py test_discovery \
    --action setup \
    --solution-name fayvad_rentals \
    --domain rental \
    --database-name rental_db \
    --database-user rental_user \
    --database-password rental_password \
    --business-prefix rental_ \
    --refresh-discoveries
```

### 2. Check Solution Status

```bash
python manage.py test_discovery \
    --action status \
    --solution-name fayvad_rentals
```

### 3. List All Solutions

```bash
python manage.py test_discovery --action list
```

## 📋 Configuration

### Solution Configuration Structure

```python
solution_config = {
    'solution_name': 'fayvad_rentals',
    'domain': 'rental',
    'database_config': {
        'name': 'rental_db',           # User's database name
        'user': 'rental_user',         # Database user
        'password': 'rental_password', # Database password
        'host': 'localhost',           # Database host
        'port': '5432'                 # Database port
    },
    'table_prefix': 'fbs_',            # FBS system table prefix
    'business_prefix': 'rental_',      # Business table prefix
    'refresh_discoveries': True        # Refresh discoveries during setup
}
```

### Django Settings Configuration

```python
# settings.py
FBS_CONFIG = {
    'table_prefix': 'fbs_',           # Default FBS table prefix
    'business_prefix': '',             # Default business prefix
    'auto_create_tables': True,        # Auto-create tables on startup
    'enable_migrations': True,         # Enable schema migrations
    'default_database_config': {
        'host': 'localhost',
        'port': '5432',
        'user': 'postgres',
        'password': 'postgres'
    }
}
```

## 🗄️ Database Schema

### FBS System Tables (fbs_*)

```sql
-- FBS Discoveries
CREATE TABLE fbs_discoveries (
    id SERIAL PRIMARY KEY,
    discovery_type VARCHAR(50) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    name VARCHAR(100) NOT NULL,
    version VARCHAR(20) DEFAULT '1.0',
    metadata JSONB DEFAULT '{}',
    schema_definition JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    discovered_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(discovery_type, domain, name, version)
);

-- FBS Solution Schemas
CREATE TABLE fbs_solution_schemas (
    id SERIAL PRIMARY KEY,
    solution_name VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(100) NOT NULL,
    database_name VARCHAR(100) NOT NULL,
    database_user VARCHAR(100) NOT NULL,
    database_password VARCHAR(255) NOT NULL,
    table_prefix VARCHAR(20) DEFAULT 'fbs_',
    business_prefix VARCHAR(20) DEFAULT '',
    schema_definition JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- FBS Schema Migrations
CREATE TABLE fbs_schema_migrations (
    id SERIAL PRIMARY KEY,
    solution_name VARCHAR(100) NOT NULL,
    migration_type VARCHAR(50) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    sql_statement TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- FBS Workflow Definitions
CREATE TABLE fbs_workflow_definitions (
    id SERIAL PRIMARY KEY,
    workflow_name VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(100) NOT NULL,
    workflow_steps JSONB DEFAULT '{}',
    trigger_conditions JSONB DEFAULT '{}',
    approval_roles JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- FBS BI Dashboards
CREATE TABLE fbs_bi_dashboards (
    id SERIAL PRIMARY KEY,
    dashboard_name VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(100) NOT NULL,
    dashboard_config JSONB DEFAULT '{}',
    chart_definitions JSONB DEFAULT '{}',
    data_sources JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Business Tables (rental_*)

```sql
-- Rental Property
CREATE TABLE rental_property (
    id SERIAL PRIMARY KEY,
    property_name VARCHAR(255) NOT NULL,
    property_type VARCHAR(50),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    rent_amount DECIMAL(10,2) NOT NULL,
    deposit_amount DECIMAL(10,2),
    square_feet INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    is_available BOOLEAN DEFAULT TRUE,
    amenities JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Rental Tenant
CREATE TABLE rental_tenant (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    credit_score INTEGER,
    employment_status VARCHAR(50),
    employer_name VARCHAR(255),
    annual_income DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Rental Lease
CREATE TABLE rental_lease (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES rental_property(id),
    tenant_id INTEGER REFERENCES rental_tenant(id),
    lease_start_date DATE NOT NULL,
    lease_end_date DATE NOT NULL,
    monthly_rent DECIMAL(10,2) NOT NULL,
    security_deposit DECIMAL(10,2),
    lease_status VARCHAR(20) DEFAULT 'active',
    lease_terms JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Rental Payment
CREATE TABLE rental_payment (
    id SERIAL PRIMARY KEY,
    lease_id INTEGER REFERENCES rental_lease(id),
    tenant_id INTEGER REFERENCES rental_tenant(id),
    payment_date DATE NOT NULL,
    payment_amount DECIMAL(10,2) NOT NULL,
    payment_type VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending',
    transaction_id VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Rental Maintenance
CREATE TABLE rental_maintenance (
    id SERIAL PRIMARY KEY,
    property_id INTEGER REFERENCES rental_property(id),
    tenant_id INTEGER REFERENCES rental_tenant(id),
    issue_type VARCHAR(100),
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'open',
    assigned_to VARCHAR(255),
    estimated_cost DECIMAL(10,2),
    actual_cost DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 API Usage

### 1. Setup Solution

```bash
curl -X POST http://localhost:8000/api/v1/solutions/setup/ \
  -H "Content-Type: application/json" \
  -d '{
    "solution_name": "fayvad_rentals",
    "domain": "rental",
    "database_config": {
      "name": "rental_db",
      "user": "rental_user",
      "password": "rental_password",
      "host": "localhost",
      "port": "5432"
    },
    "table_prefix": "fbs_",
    "business_prefix": "rental_",
    "refresh_discoveries": true
  }'
```

### 2. Get Solution Status

```bash
curl -X GET http://localhost:8000/api/v1/solutions/fayvad_rentals/status/
```

### 3. List All Solutions

```bash
curl -X GET http://localhost:8000/api/v1/solutions/
```

### 4. Refresh Discoveries

```bash
curl -X POST http://localhost:8000/api/v1/solutions/fayvad_rentals/discoveries/ \
  -H "Content-Type: application/json" \
  -d '{"action": "refresh"}'
```

### 5. Migrate Schema

```bash
curl -X POST http://localhost:8000/api/v1/solutions/fayvad_rentals/migrate/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 🎯 Management Commands

### Complete Command Reference

```bash
# Discover Odoo modules for a domain
python manage.py test_discovery \
    --action discover \
    --domain rental \
    --database-name rental_db \
    --output-format json

# Setup a complete solution
python manage.py test_discovery \
    --action setup \
    --solution-name fayvad_rentals \
    --domain rental \
    --database-name rental_db \
    --database-user rental_user \
    --database-password rental_password \
    --business-prefix rental_ \
    --refresh-discoveries

# Check solution status
python manage.py test_discovery \
    --action status \
    --solution-name fayvad_rentals

# List all solutions
python manage.py test_discovery --action list

# Refresh discoveries for a solution
python manage.py test_discovery \
    --action refresh \
    --solution-name fayvad_rentals

# Migrate solution schema
python manage.py test_discovery \
    --action migrate \
    --solution-name fayvad_rentals
```

## 🔍 Domain Support

### Supported Domains

1. **rental** - Property rental management
2. **ecommerce** - E-commerce and retail
3. **hr** - Human resources management
4. **generic** - Generic business entities

### Domain-Specific Tables

Each domain gets its own set of business tables:

- **rental**: property, tenant, lease, payment, maintenance
- **ecommerce**: product, customer, order
- **hr**: employee, department
- **generic**: entity, transaction

## 🚀 Benefits

### ✅ Simplified Management
- **One database** to backup, restore, monitor
- **Single connection** pool
- **Unified administration**

### ✅ User Control
- **User specifies** exactly which database to use
- **Complete ownership** of data
- **No external dependencies**

### ✅ Better Performance
- **No cross-database** operations
- **Faster queries** and transactions
- **Optimized indexes**

### ✅ Easy Deployment
- **Single database** configuration
- **Simplified backup/restore**
- **Easy migration** between environments

### ✅ Clean Architecture
- **Clear separation** with table prefixes
- **No data mixing** between system and business
- **Easy to understand** and maintain

## 🔧 Advanced Features

### 1. Custom Table Prefixes

```python
# Custom FBS prefix
solution_config = {
    'table_prefix': 'my_fbs_',        # Custom FBS prefix
    'business_prefix': 'my_biz_',      # Custom business prefix
    # ... other config
}
```

### 2. Multi-Tenant Support

```python
# Multiple solutions in same database
solution1_config = {
    'solution_name': 'company_a_rentals',
    'business_prefix': 'company_a_',
    # ... other config
}

solution2_config = {
    'solution_name': 'company_b_rentals', 
    'business_prefix': 'company_b_',
    # ... other config
}
```

### 3. Schema Migrations

```python
# Automatic schema migration
migration_result = integration_service.migrate_solution_schema(
    solution_name='fayvad_rentals'
)
```

### 4. Discovery Refresh

```python
# Refresh discoveries from Odoo
refresh_result = integration_service.refresh_solution_discoveries(
    solution_name='fayvad_rentals'
)
```

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check database exists
   psql -l | grep rental_db
   
   # Create database if needed
   createdb rental_db
   ```

2. **Permission Error**
   ```bash
   # Grant permissions
   psql -d rental_db -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO rental_user;"
   ```

3. **Table Already Exists**
   ```bash
   # Drop and recreate (careful!)
   python manage.py test_discovery --action setup --solution-name fayvad_rentals --domain rental
   ```

### Debug Mode

```bash
# Enable debug output
python manage.py test_discovery \
    --action setup \
    --solution-name fayvad_rentals \
    --domain rental \
    --output-format json
```

## 📊 Monitoring

### Database Size Monitoring

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('rental_db'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Table Count Monitoring

```sql
-- Count FBS tables
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'fbs_%';

-- Count business tables
SELECT COUNT(*) FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'rental_%';
```

## 🎉 Summary

The **single database approach** provides:

- ✅ **Complete user control** over their database
- ✅ **Simplified management** with one database
- ✅ **Better performance** with no cross-database operations
- ✅ **Clean architecture** with table prefixes
- ✅ **Easy deployment** and migration
- ✅ **Multi-tenant support** in same database

**The user gets exactly what they want: one database they control, with FBS managing everything within it using clear table prefixes!** 🚀 