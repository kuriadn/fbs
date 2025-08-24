# 🏗️ FBS Modular Architecture

This document explains the new modular architecture of FBS, where core functionality, licensing, and document management are separated into independent, embeddable apps.

## 🎯 **Architecture Overview**

### **Before: Monolithic Structure**
```
fbs_app/
├── licensing/          # Embedded licensing
├── models/            # All models in one place
├── services/          # All services together
└── interfaces.py      # Single interface
```

### **After: Modular Structure**
```
fbs_app/               # Core FBS functionality
├── models/            # Core models only
├── services/          # Core services only
└── interfaces.py      # Core interface

fbs_license_manager/   # Standalone licensing
├── models/            # License models
├── services/          # License services
└── admin.py           # License admin

fbs_dms/              # Future: Document management
├── models/            # Document models
├── services/          # Document services
└── admin.py           # Document admin
```

## 🚀 **Benefits of Modular Architecture**

### **1. Independent Development**
- **Separate teams** can work on different components
- **Different release cycles** for each app
- **Specialized expertise** for each domain

### **2. Flexible Deployment**
```python
# Solution A: Core + Licensing only
INSTALLED_APPS = [
    'fbs_app',
    'fbs_license_manager',
    # No DMS needed
]

# Solution B: Core + DMS only
INSTALLED_APPS = [
    'fbs_app',
    'fbs_dms',
    # No licensing needed
]

# Solution C: All three
INSTALLED_APPS = [
    'fbs_app',
    'fbs_license_manager',
    'fbs_dms',
]
```

### **3. Multi-Database Architecture**
- **`fbs_system_db`**: FBS system-wide configurations only
- **`lic_system_db`**: System-wide licensing management
- **`djo_{solution}_db`**: Django-specific data per solution
- **`fbs_{solution}_db`**: Odoo-specific data per solution

### **3. Reusability**
- **License Manager** can be used in non-FBS projects
- **DMS** can be used in non-FBS projects
- **FBS Core** can be used without licensing or DMS

### **4. Testing & Quality**
- **Isolated testing** for each app
- **Easier debugging** and maintenance
- **Better separation of concerns**

## 🔌 **Integration Patterns**

### **1. Optional Integration**
```python
class FBSInterface:
    def __init__(self, solution_name: str, license_key: str = None):
        self.solution_name = solution_name
        
        # Core FBS (always available)
        self.odoo = OdooIntegrationInterface(solution_name)
        self.workflows = WorkflowInterface(solution_name)
        
        # Optional integrations
        try:
            from fbs_license_manager import LicenseManager
            self.licensing = LicenseManager(solution_name)
            self._licensing_available = True
        except ImportError:
            self.licensing = None
            self._licensing_available = False
```

### **2. Service Discovery**
```python
class AppDiscoveryService:
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        self.available_apps = self._discover_apps()
    
    def _discover_apps(self):
        """Discover which FBS apps are available"""
        apps = {
            'core': True,  # Always available
            'licensing': self._check_app('fbs_license_manager'),
            'dms': self._check_app('fbs_dms'),
        }
        return apps
```

### **3. Cross-App Communication**
```python
class WorkflowService:
    def create_workflow(self, workflow_data):
        # Core workflow logic
        workflow = self._create_workflow(workflow_data)
        
        # Optional: Integrate with licensing
        if self._has_licensing():
            self._check_workflow_license(workflow)
        
        # Optional: Integrate with DMS
        if self._has_dms():
            self._create_workflow_documents(workflow)
        
        return workflow
```

## 📦 **Package Structure**

### **FBS Core** (`fbs_app`)
```
fbs_app/
├── __init__.py
├── apps.py
├── models/
│   ├── core.py          # Odoo databases, tokens, etc.
│   ├── workflows.py     # Workflow engine
│   ├── msme.py         # MSME features
│   ├── bi.py           # Business intelligence
│   └── discovery.py    # Odoo model discovery
├── services/            # Business logic services
└── interfaces.py        # Core FBS interface
```

### **FBS License Manager** (`fbs_license_manager`)
```
fbs_license_manager/
├── __init__.py
├── apps.py
├── models/
│   ├── licenses.py      # License models
│   ├── features.py      # Feature definitions
│   └── usage.py         # Usage tracking
├── services/
│   ├── license_engine.py
│   ├── feature_flags.py
│   └── upgrade_prompts.py
└── interfaces.py        # Licensing interface
```

### **FBS Document Management** (`fbs_dms`) - Future
```
fbs_dms/
├── __init__.py
├── apps.py
├── models/
│   ├── documents.py     # Document storage
│   ├── versions.py      # Version control
│   ├── metadata.py      # Document metadata
│   └── workflows.py     # Document workflows
├── services/
│   ├── storage.py       # File storage
│   ├── indexing.py      # Search/indexing
│   └── conversion.py    # Format conversion
└── interfaces.py        # DMS interface
```

## 🔄 **Migration Strategy**

### **Phase 1: Extract Licensing** ✅ **COMPLETED**
- [x] Create `fbs_license_manager` app
- [x] Move license models and services
- [x] Update FBS core to use optional integration
- [x] Maintain backward compatibility

### **Phase 2: Extract DMS** 🔄 **PLANNED**
- [ ] Identify document-related functionality
- [ ] Create new `fbs_dms` app
- [ ] Move document models and services
- [ ] Update FBS core integration

### **Phase 3: Clean Integration** 🔄 **PLANNED**
- [ ] Remove duplicate code
- [ ] Establish clean interfaces
- [ ] Update documentation
- [ ] Performance optimization

## 🧪 **Testing Strategy**

### **Unit Tests**
```python
# Test each app independently
pytest fbs_app/
pytest fbs_license_manager/
pytest fbs_dms/  # Future
```

### **Integration Tests**
```python
# Test app interactions
pytest tests/integration/
```

### **End-to-End Tests**
```python
# Test complete workflows
pytest tests/e2e/
```

## 🚀 **Deployment Options**

### **Option 1: All Apps Together**
```bash
# Install all components
pip install fbs-app fbs-license-manager fbs-dms

# Django settings
INSTALLED_APPS = [
    'fbs_app',
    'fbs_license_manager',
    'fbs_dms',
]
```

### **Option 2: Core + Licensing Only**
```bash
# Install core + licensing
pip install fbs-app fbs-license-manager

# Django settings
INSTALLED_APPS = [
    'fbs_app',
    'fbs_license_manager',
]
```

### **Option 3: Core Only**
```bash
# Install core only
pip install fbs-app

# Django settings
INSTALLED_APPS = [
    'fbs_app',
]
```

## 🔧 **Configuration Management**

### **Shared Configuration**
```python
# settings.py - Each app can share config
FBS_APPS = {
    'core': {
        'enabled': True,
        'odoo_connection': {...}
    },
    'licensing': {
        'enabled': True,
        'license_api_url': '...',
        'feature_flags': {...}
    },
    'dms': {
        'enabled': True,
        'storage_backend': 's3',
        'max_file_size': '100MB'
    }
}
```

### **Environment Variables**
```bash
# Core FBS
export FBS_ODOO_HOST="localhost"
export FBS_ODOO_PORT="8069"

# License Manager
export FBS_LICENSE_TYPE="professional"
export FBS_ENABLE_MSME_FEATURES="true"

# Document Management (Future)
export FBS_DMS_STORAGE="s3"
export FBS_DMS_BUCKET="my-documents"
```

## 📊 **Performance Considerations**

### **Lazy Loading**
```python
# Load apps only when needed
def get_license_manager():
    if not hasattr(get_license_manager, '_instance'):
        try:
            from fbs_license_manager import LicenseManager
            get_license_manager._instance = LicenseManager()
        except ImportError:
            get_license_manager._instance = None
    return get_license_manager._instance
```

### **Caching Strategy**
```python
# Each app manages its own cache
# Core FBS: Odoo connection caching
# License Manager: License data caching
# DMS: Document metadata caching
```

## 🔒 **Security Considerations**

### **App Isolation**
- **Each app** has its own models and services
- **No cross-app** data access without explicit interfaces
- **Permission systems** are app-specific

### **API Security**
- **License checks** happen at the service layer
- **Feature flags** are enforced consistently
- **Usage limits** are enforced per solution

## 🎯 **Next Steps**

### **Immediate (Completed)**
1. ✅ Extract licensing into `fbs_license_manager`
2. ✅ Update FBS core for optional integration
3. ✅ Create comprehensive documentation
4. ✅ Set up testing infrastructure

### **Short Term (Next 2 weeks)**
1. 🔄 Extract document management into `fbs_dms`
2. 🔄 Create clean interfaces between apps
3. 🔄 Update admin interfaces
4. 🔄 Performance testing and optimization

### **Medium Term (Next month)**
1. 🔄 Create app discovery service
2. 🔄 Implement cross-app communication
3. 🔄 Advanced configuration management
4. 🔄 Monitoring and analytics

### **Long Term (Next quarter)**
1. 🔄 External service integrations
2. 🔄 Advanced feature dependencies
3. 🔄 Multi-tenant optimizations
4. 🔄 Enterprise features

## 🤝 **Contributing to Modular Architecture**

### **Development Guidelines**
1. **Keep apps independent** - minimize cross-app dependencies
2. **Use interfaces** - define clear contracts between apps
3. **Test thoroughly** - each app should work independently
4. **Document changes** - update this document for architectural changes

### **Code Review Checklist**
- [ ] Does this change maintain app independence?
- [ ] Are interfaces clearly defined?
- [ ] Is backward compatibility maintained?
- [ ] Are tests updated for all affected apps?
- [ ] Is documentation updated?

## 📚 **Additional Resources**

- **FBS Core Documentation**: [docs/FBS_CORE.md](docs/FBS_CORE.md)
- **License Manager Documentation**: [fbs_license_manager/README.md](fbs_license_manager/README.md)
- **API Reference**: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Testing Guide**: [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md)

## 🆘 **Support & Questions**

For questions about the modular architecture:
- **GitHub Issues**: [Create an issue](https://github.com/fbs/fbs/issues)
- **Documentation**: Check the relevant app documentation
- **Team Chat**: Join our development discussions

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Phase 1 Complete, Phase 2 Planning
