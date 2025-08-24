# 🔄 FBS Database Architecture Migration Guide

This guide explains how to migrate from the old single-database architecture to the new multi-database architecture.

## 🎯 **Migration Overview**

### **What's Changing**
- **Before**: Single `fbs_system_db` containing everything
- **After**: 
  - `fbs_system_db` → FBS system configurations only
  - `lic_system_db` → Licensing management only
  - Future: `djo_{solution}_db` and `fbs_{solution}_db` for solutions

### **Migration Benefits**
- ✅ **Better separation of concerns**
- ✅ **Improved scalability**
- ✅ **Enhanced security**
- ✅ **Easier maintenance**

## 🚀 **Step-by-Step Migration**

### **Phase 1: Prepare Environment**

#### **1.1 Update Environment Variables**
```bash
# Copy and update environment file
cp env.example .env

# Edit .env file to include licensing database
LIC_DB_NAME=lic_system_db
LIC_DB_USER=odoo
LIC_DB_PASSWORD=your_secure_password
LIC_DB_HOST=localhost
LIC_DB_PORT=5432
```

#### **1.2 Install Dependencies**
```bash
# Ensure psycopg2 is installed for database operations
pip install psycopg2-binary

# Or if you prefer psycopg2
pip install psycopg2
```

### **Phase 2: Create New Databases**

#### **2.1 Run Database Setup Script**
```bash
# Make script executable
chmod +x scripts/setup_databases.py

# Run setup script
python scripts/setup_databases.py
```

#### **2.2 Manual Database Creation (Alternative)**
```bash
# Connect to PostgreSQL
psql -U odoo -h localhost

# Create licensing database
CREATE DATABASE lic_system_db;

# Verify databases
\l

# Exit psql
\q
```

### **Phase 3: Run Django Migrations**

#### **3.1 Migrate FBS Core (System Database)**
```bash
# Migrate FBS app models to fbs_system_db
python manage.py migrate fbs_app --database=default

# Verify migration
python manage.py showmigrations --database=default
```

#### **3.2 Migrate License Manager (Licensing Database)**
```bash
# Migrate license manager models to lic_system_db
python manage.py migrate fbs_license_manager --database=licensing

# Verify migration
python manage.py showmigrations --database=licensing
```

#### **3.3 Verify Database Separation**
```bash
# Check which models are in which database
python manage.py dbshell --database=default
# In psql shell:
\dt fbs_*

python manage.py dbshell --database=licensing
# In psql shell:
\dt fbs_license_manager_*
```

### **Phase 4: Test the New Architecture**

#### **4.1 Test Database Routing**
```python
# Create a test script test_db_routing.py
from django.conf import settings
from django.db import connections
from fbs_app.models.core import OdooDatabase
from fbs_license_manager.models import SolutionLicense

# Test FBS models routing
try:
    odoo_db = OdooDatabase.objects.create(
        name='test_db',
        host='localhost',
        port=8069,
        protocol='http',
        username='test',
        password='test'
    )
    print(f"✅ FBS model created in: {odoo_db._state.db}")
    odoo_db.delete()  # Clean up
except Exception as e:
    print(f"❌ FBS model creation failed: {e}")

# Test license models routing
try:
    license = SolutionLicense.objects.create(
        solution_name='test_solution',
        license_type='trial'
    )
    print(f"✅ License model created in: {license._state.db}")
    license.delete()  # Clean up
except Exception as e:
    print(f"❌ License model creation failed: {e}")
```

#### **4.2 Test Django Admin**
```bash
# Start Django development server
python manage.py runserver

# Visit admin interface
# http://localhost:8000/admin/
# Verify that:
# - FBS models appear in fbs_system_db
# - License models appear in lic_system_db
```

### **Phase 5: Verify Data Integrity**

#### **5.1 Check Data Separation**
```python
# Verify no cross-database relations exist
from django.db import connections

# Check default database tables
with connections['default'].cursor() as cursor:
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    default_tables = [row[0] for row in cursor.fetchall()]
    print(f"Default DB tables: {default_tables}")

# Check licensing database tables
with connections['licensing'].cursor() as cursor:
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    licensing_tables = [row[0] for row in cursor.fetchall()]
    print(f"Licensing DB tables: {licensing_tables}")

# Verify no overlap
overlap = set(default_tables) & set(licensing_tables)
if overlap:
    print(f"⚠️  Warning: Tables in both databases: {overlap}")
else:
    print("✅ No table overlap between databases")
```

#### **5.2 Test Application Functionality**
```bash
# Run the test suite
python manage.py test

# Run specific app tests
python manage.py test fbs_app
python manage.py test fbs_license_manager
```

## 🔧 **Troubleshooting**

### **Common Issues**

#### **Issue 1: Database Connection Errors**
```bash
# Error: database "lic_system_db" does not exist
# Solution: Run database setup script
python scripts/setup_databases.py
```

#### **Issue 2: Migration Errors**
```bash
# Error: Table already exists
# Solution: Check existing tables and clean up if needed
python manage.py dbshell --database=licensing
# In psql: \dt
# Drop tables if they exist in wrong database
```

#### **Issue 3: Import Errors**
```python
# Error: No module named 'fbs_license_manager'
# Solution: Ensure app is in INSTALLED_APPS
# Check fbs_project/settings.py
```

#### **Issue 4: Cross-Database Relations**
```python
# Error: Cross-database relations not allowed
# Solution: Use separate queries instead of joins
# Query each database separately and combine results in Python
```

### **Rollback Plan**

If migration fails, you can rollback:

```bash
# 1. Stop Django server
# 2. Drop new databases
dropdb lic_system_db

# 3. Restore from backup (if you have one)
# 4. Revert code changes
git checkout HEAD~1

# 5. Restart with old architecture
```

## 📋 **Post-Migration Checklist**

### **✅ Verification Items**
- [ ] Both databases created successfully
- [ ] Migrations run without errors
- [ ] Django admin shows correct database separation
- [ ] Application functionality works correctly
- [ ] No cross-database relation errors
- [ ] Tests pass for both apps
- [ ] Database routing works as expected

### **🔧 Configuration Updates**
- [ ] Environment variables updated
- [ ] Database router configured
- [ ] Django settings updated
- [ ] Documentation updated

### **📊 Monitoring**
- [ ] Database performance metrics
- [ ] Connection pool usage
- [ ] Query performance
- [ ] Error logs

## 🚀 **Next Steps After Migration**

### **1. Solution Database Creation**
```python
# When ready to add client solutions
def create_solution_databases(solution_name):
    """Create solution-specific databases"""
    django_db = f"djo_{solution_name}_db"
    odoo_db = f"fbs_{solution_name}_db"
    
    # Create databases
    # Initialize schemas
    # Configure routing
```

### **2. Performance Optimization**
```python
# Add database-specific optimizations
DATABASES = {
    'default': {
        # ... existing config
        'OPTIONS': {
            'MAX_CONNS': 20,
            'CONN_MAX_AGE': 600,
        }
    },
    'licensing': {
        # ... existing config
        'OPTIONS': {
            'MAX_CONNS': 10,
            'CONN_MAX_AGE': 300,
        }
    }
}
```

### **3. Backup Strategy**
```bash
# Create backup scripts for each database
pg_dump -U odoo -h localhost fbs_system_db > backup_fbs_system.sql
pg_dump -U odoo -h localhost lic_system_db > backup_lic_system.sql
```

---

## **✅ Migration Complete!**

Your FBS system now has:
- **Proper database separation** of concerns
- **Scalable architecture** for multiple solutions
- **Enhanced security** through data isolation
- **Better maintainability** with clear boundaries

The system is ready for production use with the new multi-database architecture!


