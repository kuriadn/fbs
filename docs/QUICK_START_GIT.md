# 🚀 **FBS Git Installation - Quick Start Guide**

Get FBS running from Git source in under 5 minutes!

## ⚡ **Super Quick Install**

### **1. Install from Git (Recommended)**

```bash
# Install directly from Git
pip install git+https://github.com/fayvad/fbs.git

# Or from specific branch
pip install git+https://github.com/fayvad/fbs.git@develop
```

### **2. Add to Django Settings**

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ... other apps ...
    
    # Add FBS
    'fbs_app.apps.FBSAppConfig',
]

# FBS Configuration
FBS_APP = {
    'ODOO_BASE_URL': 'http://localhost:8069',  # Your Odoo URL
    'DATABASE_USER': 'odoo',
    'DATABASE_PASSWORD': 'your_password',
}
```

### **3. Run Migrations**

```bash
python manage.py migrate
```

### **4. Test Installation**

```python
# Test in Django shell
python manage.py shell

>>> from fbs_app.interfaces import FBSInterface
>>> fbs = FBSInterface('my_solution')
>>> print(fbs.get_system_health())
```

**That's it!** 🎉

## 🐳 **Docker Quick Start**

### **1. Clone and Setup**

```bash
git clone https://github.com/fayvad/fbs.git
cd fbs
```

### **2. Copy Environment File**

```bash
cp docker/env.git.example .env
# Edit .env with your settings
```

### **3. Build and Run**

```bash
# Build with custom FBS repo
docker-compose -f docker/docker-compose.git.yml up --build

# Or with custom arguments
FBS_REPO=https://github.com/yourusername/fbs.git \
FBS_BRANCH=feature-branch \
docker-compose -f docker/docker-compose.git.yml up --build
```

## 🔧 **Advanced Git Installation**

### **Install from Fork**

```bash
# Install from your fork
pip install git+https://github.com/yourusername/fbs.git

# Install from specific commit
pip install git+https://github.com/yourusername/fbs.git@abc1234

# Install in editable mode (for development)
pip install -e git+https://github.com/yourusername/fbs.git#egg=fbs-app
```

### **Clone and Customize**

```bash
# Clone repository
git clone https://github.com/yourusername/fbs.git
cd fbs

# Create custom branch
git checkout -b my-custom-features

# Make changes
# ... edit files ...

# Install in editable mode
pip install -e .

# Test changes
python -c "import fbs_app; print('Custom FBS loaded!')"
```

## 📦 **Requirements.txt Integration**

```txt
# requirements.txt
# Install FBS from Git
git+https://github.com/fayvad/fbs.git

# Or with specific version
git+https://github.com/fayvad/fbs.git@v2.0.0

# Other dependencies
Django>=4.2.0
psycopg2-binary>=2.9.0
```

Then run:
```bash
pip install -r requirements.txt
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Git not found**: `apt-get install git` (Ubuntu) or `brew install git` (macOS)
2. **Permission denied**: Use HTTPS instead of SSH or check your Git credentials
3. **Import error**: Make sure you added `fbs_app.apps.FBSAppConfig` to `INSTALLED_APPS`

### **Verify Installation**

```bash
# Check if FBS is installed
pip list | grep fbs

# Test import
python -c "import fbs_app; print('FBS version:', fbs_app.__version__)"

# Test interfaces
python -c "from fbs_app.interfaces import FBSInterface; print('Interfaces OK')"
```

## 📚 **Next Steps**

- 📖 Read the [Full Git Installation Guide](GIT_INSTALLATION.md)
- 🐳 Check [Docker Examples](docker/)
- 🔧 Explore [Configuration Options](../fbs_app/config_template.py)
- 🧪 Run [Tests](../TESTING_GUIDE.md)

## 🆘 **Need Help?**

- 📖 Check the [main README](../README.md)
- 🐛 Open an [issue on GitHub](https://github.com/fayvad/fbs/issues)
- 💬 Join our [discussions](https://github.com/fayvad/fbs/discussions)

---

**Happy coding with FBS!** 🚀✨
