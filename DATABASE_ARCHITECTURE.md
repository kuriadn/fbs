# 🗄️ FBS Database Architecture

This document explains the multi-database architecture of FBS, ensuring proper separation of concerns across different database levels.

## 🎯 **Architecture Overview**

### **Database Separation Strategy**

```
┌─────────────────────────────────────────────────────────────────┐
│                        FBS Multi-Database Architecture         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │ fbs_system_db   │    │ lic_system_db   │    │ Solution    │ │
│  │                 │    │                 │    │ Databases   │ │
│  │ • FBS Core      │    │ • System-wide   │    │             │ │
│  │   Configs       │    │   Licensing     │    │ ┌─────────┐ │ │
│  │ • Odoo DB       │    │ • License Tiers │    │ │djo_     │ │ │
│  │   Connections   │    │ • Global        │    │ │solution │ │ │
│  │ • System        │    │   Features      │    │ │_db      │ │ │
│  │   Settings      │    │ • Policies      │    │ │         │ │ │
│  │ • Request Logs  │    │ • Usage         │    │ │• Django │ │ │
│  │ • Cache Data    │    │   Tracking      │    │ │  Data   │ │ │
│  └─────────────────┘    └─────────────────┘    │ └─────────┘ │ │
│                                                 │             │ │
│                                                 │ ┌─────────┐ │ │
│                                                 │ │fbs_     │ │ │
│                                                 │ │solution │ │ │
│                                                 │ │_db      │ │ │
│                                                 │ │         │ │ │
│                                                 │ │• Odoo   │ │ │
│                                                 │ │  Data   │ │ │
│                                                 │ └─────────┘ │ │
│                                                 └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🗃️ **Database Purposes**

### **1. fbs_system_db (Default)**
**Purpose**: FBS system-wide configurations and operational data

**Contains**:
- FBS core application models
- Odoo database connection configurations
- System settings and configurations
- Request logs and audit trails
- Cache entries and temporary data
- User authentication tokens
- Business rules and system policies

**Models**:
```python
# fbs_app.models.core
- OdooDatabase          # Odoo connection configs
- TokenMapping          # User-DB token mappings
- RequestLog            # System request logs
- BusinessRule          # System business rules
- CacheEntry            # System cache data
- Handshake             # Authentication handshakes
- Notification          # System notifications
- ApprovalRequest       # System approval requests
- ApprovalResponse      # System approval responses
- CustomField           # System custom fields
```

### **2. lic_system_db (Licensing)**
**Purpose**: System-wide licensing management and feature control

**Contains**:
- License tier definitions
- Global feature configurations
- System-wide usage policies
- License validation rules
- Upgrade path definitions
- Global feature flags

**Models**:
```python
# fbs_license_manager.models
- SolutionLicense       # Solution license records
- FeatureUsage          # Feature usage tracking
- LicenseManager        # License management utilities
```

### **3. djo_{solution}_db (Solution Django)**
**Purpose**: Django-specific data for each client solution

**Contains**:
- Solution-specific Django models
- User preferences and settings
- Solution-specific configurations
- Local cache and session data
- Solution-specific business rules

**Examples**:
```
djo_acme_corp_db      # ACME Corporation Django data
djo_tech_startup_db   # Tech Startup Django data
djo_retail_chain_db   # Retail Chain Django data
```

### **4. fbs_{solution}_db (Solution Odoo)**
**Purpose**: Odoo-specific data for each client solution

**Contains**:
- Business data (customers, products, orders)
- Workflow instances and states
- Business intelligence data
- Compliance and audit data
- Accounting and financial data

**Examples**:
```
fbs_acme_corp_db      # ACME Corporation Odoo data
fbs_tech_startup_db   # Tech Startup Odoo data
fbs_retail_chain_db   # Retail Chain Odoo data
```

## 🔌 **Database Routing**

### **Router Logic**

```python
class FBSDatabaseRouter:
    def db_for_read(self, model, **hints):
        app_label = model._meta.app_label
        
        if app_label == 'fbs_license_manager':
            return 'licensing'           # → lic_system_db
        
        if app_label == 'fbs_app':
            return 'default'             # → fbs_system_db
        
        # Solution-specific databases via hints
        if 'database' in hints:
            return hints['database']     # → djo_{solution}_db
        
        return None
```

### **Migration Routing**

```python
def allow_migrate(self, db, app_label, model_name=None, **hints):
    if app_label == 'fbs_license_manager':
        return db == 'licensing'        # License models → lic_system_db
    
    elif app_label == 'fbs_app':
        return db == 'default'          # FBS models → fbs_system_db
    
    return None
```

## 🚀 **Benefits of This Architecture**

### **1. Clear Separation of Concerns**
- **System data** stays in system databases
- **Solution data** stays in solution databases
- **Licensing data** isolated in licensing database

### **2. Scalability**
- Each solution gets its own databases
- No cross-contamination between solutions
- Easy to add new solutions

### **3. Security**
- Solution data isolated from system data
- Licensing data separate from business data
- Clear access control boundaries

### **4. Maintenance**
- Easy to backup/restore specific solutions
- System maintenance doesn't affect solutions
- License management independent of business logic

### **5. Performance**
- No cross-database joins
- Optimized queries within each database
- Better connection pooling

## ⚙️ **Configuration**

### **Environment Variables**

```bash
# System Database
DB_NAME=fbs_system_db
DB_USER=odoo
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

# Licensing Database
LIC_DB_NAME=lic_system_db
LIC_DB_USER=odoo
LIC_DB_PASSWORD=secure_password
LIC_DB_HOST=localhost
LIC_DB_PORT=5432
```

### **Django Settings**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'fbs_system_db',
        # ... other settings
    },
    'licensing': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lic_system_db',
        # ... other settings
    }
}

DATABASE_ROUTERS = [
    'fbs_app.routers.FBSDatabaseRouter',
]
```

## 🔄 **Migration Strategy**

### **Phase 1: Create Licensing Database**
```bash
# Create licensing database
createdb lic_system_db

# Run migrations for license manager
python manage.py migrate --database=licensing
```

### **Phase 2: Verify Separation**
```bash
# Verify FBS models in system DB
python manage.py migrate --database=default

# Verify license models in licensing DB
python manage.py migrate --database=licensing
```

### **Phase 3: Solution Database Creation**
```python
# When creating new solutions
solution_name = "acme_corp"

# Create Django database
django_db = f"djo_{solution_name}_db"
# Create Odoo database  
odoo_db = f"fbs_{solution_name}_db"

# Initialize solution-specific databases
# (Implementation depends on solution creation logic)
```

## 🧪 **Testing the Architecture**

### **Test Database Routing**

```python
from fbs_app.models.core import OdooDatabase
from fbs_license_manager.models import SolutionLicense

# FBS models should go to default (fbs_system_db)
odoo_db = OdooDatabase.objects.create(...)
print(f"OdooDatabase DB: {odoo_db._state.db}")  # Should be 'default'

# License models should go to licensing (lic_system_db)
license = SolutionLicense.objects.create(...)
print(f"SolutionLicense DB: {license._state.db}")  # Should be 'licensing'
```

### **Test Cross-Database Relations**

```python
# This should fail - no cross-database relations
try:
    odoo_db.licenses.all()  # Should raise error
except Exception as e:
    print(f"Cross-database relation blocked: {e}")
```

## 📋 **Best Practices**

### **1. Always Use App Labels**
```python
class MyModel(models.Model):
    class Meta:
        app_label = 'my_app'  # Always specify app_label
```

### **2. Use Database Hints for Solution Data**
```python
# When working with solution-specific data
SolutionModel.objects.using('djo_acme_corp_db').create(...)
```

### **3. Avoid Cross-Database Queries**
```python
# ❌ Wrong - Cross-database join
User.objects.filter(license__status='active')

# ✅ Correct - Query within same database
User.objects.filter(status='active')
```

### **4. Use Transactions Appropriately**
```python
from django.db import transaction

# Single database transaction
with transaction.atomic(using='licensing'):
    license.save()

# Multi-database operations need separate transactions
with transaction.atomic(using='default'):
    odoo_db.save()
with transaction.atomic(using='licensing'):
    license.save()
```

## 🚨 **Common Pitfalls**

### **1. Forgetting App Labels**
```python
# ❌ Wrong - No app_label
class MyModel(models.Model):
    pass

# ✅ Correct - With app_label
class MyModel(models.Model):
    class Meta:
        app_label = 'my_app'
```

### **2. Cross-Database Relations**
```python
# ❌ Wrong - Models in different databases
class SystemModel(models.Model):
    license = models.ForeignKey('fbs_license_manager.SolutionLicense')

# ✅ Correct - Separate queries
system_model = SystemModel.objects.get(id=1)
license = SolutionLicense.objects.get(solution_name=system_model.solution_name)
```

### **3. Ignoring Database Hints**
```python
# ❌ Wrong - No database hint
SolutionModel.objects.create(...)

# ✅ Correct - With database hint
SolutionModel.objects.using('djo_solution_db').create(...)
```

---

## **✅ Conclusion**

This multi-database architecture provides:

- **Clear separation** between system, licensing, and solution data
- **Scalability** for multiple client solutions
- **Security** through data isolation
- **Maintainability** through clear boundaries
- **Performance** through optimized routing

Follow these guidelines to maintain the integrity of the architecture and ensure proper data separation across all database levels.
