# FBS Quick Installation Guide

## 🚀 Quick Start

### **1. Clone Repository**
```bash
git clone https://github.com/kuriadn/fbs.git
cd fbs
```

### **2. Install FBS Suite**
```bash
# Install in development mode (recommended)
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with testing dependencies
pip install -e ".[test]"

# Install with documentation dependencies
pip install -e ".[docs]"
```

### **3. Test Installation**
```bash
# Run installation test
python test_installation.py
```

## 📦 Installation Options

### **Basic Installation**
```bash
pip install -e .
```
Includes:
- Core FBS app
- DMS (Document Management)
- License Manager
- Production dependencies

### **Development Installation**
```bash
pip install -e ".[dev]"
```
Includes:
- All basic features
- Testing frameworks (pytest, coverage)
- Code quality tools (black, flake8, mypy)
- Development utilities

### **Testing Installation**
```bash
pip install -e ".[test]"
```
Includes:
- All basic features
- Testing frameworks
- Test data generators

### **Documentation Installation**
```bash
pip install -e ".[docs]"
```
Includes:
- All basic features
- Documentation tools (Sphinx)
- Documentation themes

## 🔧 Configuration

### **1. Django Settings**
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

### **2. Environment Variables**
```bash
# .env
ODOO_BASE_URL=http://localhost:8069
ODOO_DATABASE_USER=your_user
ODOO_DATABASE_PASSWORD=your_password
FBS_SOLUTION_NAME=your_solution
```

## 🧪 Testing

### **Run Installation Test**
```bash
python test_installation.py
```

### **Run Unit Tests**
```bash
# All tests
pytest

# Specific app tests
pytest fbs_app/
pytest fbs_dms/
pytest fbs_license_manager/

# With coverage
pytest --cov=fbs_app --cov=fbs_dms --cov=fbs_license_manager
```

### **Run Django Tests**
```bash
python manage.py test fbs_app
python manage.py test fbs_dms
python manage.py test fbs_license_manager
```

## 📚 Next Steps

### **1. Read Documentation**
- [Installation Guide](docs/INSTALLATION.md) - Complete setup instructions
- [Integration Guide](docs/INTEGRATION.md) - How to embed FBS
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - Service interfaces
- [Odoo Integration](docs/ODOO_INTEGRATION.md) - Odoo + Virtual Fields

### **2. Run Examples**
```bash
cd docs/EXAMPLES
python basic_integration.py
```

### **3. Start Building**
```python
from fbs_app.interfaces import FBSInterface

# Initialize FBS
fbs = FBSInterface('your_solution_name')

# Check system health
health = fbs.get_system_health()

# Access Odoo integration
models = fbs.odoo.discover_models()
```

## 🐛 Troubleshooting

### **Import Errors**
```bash
# Reinstall in development mode
pip uninstall fbs-suite
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### **Missing Dependencies**
```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### **Configuration Issues**
```bash
# Check environment variables
python -c "import os; print('ODOO_BASE_URL:', os.getenv('ODOO_BASE_URL'))"

# Test Odoo connection
python test_installation.py
```

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Examples**: [docs/EXAMPLES/](docs/EXAMPLES/)
- **Issues**: [GitHub Issues](https://github.com/kuriadn/fbs/issues)
- **Email**: dev@fayvad.com

---

**Ready to Build!** 🚀

FBS is now installed and ready to power your business applications with Odoo integration and Virtual Fields technology.
