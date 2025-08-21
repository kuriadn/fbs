# 🚀 **FBS Git Source Installation Guide**

This guide covers installing FBS directly from Git source code, giving you full control over versions, branches, and customizations.

## 📋 **Prerequisites**

- Python 3.8+ 
- Git
- pip or pipenv
- PostgreSQL (for production)
- Redis (optional, for caching)

## 🔧 **Installation Methods**

### **Method 1: Direct Git Install (Recommended)**

```bash
# Install directly from Git
pip install git+https://github.com/yourusername/fbs.git

# Install from specific branch
pip install git+https://github.com/yourusername/fbs.git@develop

# Install from specific commit
pip install git+https://github.com/yourusername/fbs.git@abc1234

# Install in editable mode (for development)
pip install -e git+https://github.com/yourusername/fbs.git#egg=fbs-app
```

### **Method 2: Clone and Install**

```bash
# Clone the repository
git clone https://github.com/yourusername/fbs.git
cd fbs

# Install in editable mode
pip install -e .

# Or install normally
pip install .
```

### **Method 3: From Requirements.txt**

```txt
# requirements.txt
# Install from Git
git+https://github.com/yourusername/fbs.git

# Or with specific branch
git+https://github.com/yourusername/fbs.git@develop

# Or with specific version tag
git+https://github.com/yourusername/fbs.git@v2.0.0
```

Then run:
```bash
pip install -r requirements.txt
```

## 🐳 **Docker Git Installation**

### **Dockerfile with Git Install**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install FBS from Git
RUN pip install git+https://github.com/yourusername/fbs.git

# Copy your project
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### **Docker Compose with Git**

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - FBS_GIT_REPO=https://github.com/yourusername/fbs.git
      - FBS_GIT_BRANCH=main
    # ... rest of config
```

## 🔄 **Version Management**

### **Using Git Tags for Releases**

```bash
# Tag a release
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0

# Install specific version
pip install git+https://github.com/yourusername/fbs.git@v2.0.0
```

### **Using Git Branches**

```bash
# Create feature branch
git checkout -b feature/new-feature

# Install from feature branch
pip install git+https://github.com/yourusername/fbs.git@feature/new-feature

# Install from develop branch
pip install git+https://github.com/yourusername/fbs.git@develop
```

## 🛠 **Customization and Development**

### **Fork and Customize**

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/fbs.git
cd fbs

# Add upstream remote
git remote add upstream https://github.com/originalowner/fbs.git

# Create custom branch
git checkout -b custom-features

# Make your changes
# ... edit files ...

# Commit and push
git add .
git commit -m "Add custom features"
git push origin custom-features

# Install your custom version
pip install git+https://github.com/yourusername/fbs.git@custom-features
```

### **Local Development Installation**

```bash
# Clone your repository
git clone https://github.com/yourusername/fbs.git
cd fbs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Make changes and test
# ... edit files ...
pytest  # Test your changes
```

## 📦 **Package Management**

### **Using pip-tools**

```bash
# Install pip-tools
pip install pip-tools

# Create requirements.in
echo "git+https://github.com/yourusername/fbs.git" > requirements.in

# Compile requirements
pip-compile requirements.in

# Install
pip-sync requirements.txt
```

### **Using Poetry**

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.8"
fbs-app = {git = "https://github.com/yourusername/fbs.git"}

# Or specific branch
fbs-app = {git = "https://github.com/yourusername/fbs.git", branch = "develop"}
```

```bash
# Install with Poetry
poetry install
```

## 🔐 **Private Repository Installation**

### **Using SSH Keys**

```bash
# Install from private SSH repository
pip install git+ssh://git@github.com/yourusername/private-fbs.git

# Or with specific branch
pip install git+ssh://git@github.com/yourusername/private-fbs.git@develop
```

### **Using Personal Access Tokens**

```bash
# Install from private HTTPS with token
pip install git+https://your-token@github.com/yourusername/private-fbs.git

# Or set environment variable
export GITHUB_TOKEN=your-token-here
pip install git+https://${GITHUB_TOKEN}@github.com/yourusername/private-fbs.git
```

## 🚀 **Production Deployment**

### **Requirements.txt for Production**

```txt
# Production requirements
git+https://github.com/yourusername/fbs.git@v2.0.0

# Other dependencies
Django>=4.2.0,<5.1.0
psycopg2-binary>=2.9.0
gunicorn>=21.2.0
```

### **Environment-Specific Branches**

```bash
# Production branch
git checkout -b production
# ... production-specific changes ...
git push origin production

# Install production version
pip install git+https://github.com/yourusername/fbs.git@production
```

## 🔍 **Verification and Testing**

### **Verify Installation**

```python
# Test FBS installation
import fbs_app
print(f"FBS version: {fbs_app.__version__}")

# Test interfaces
from fbs_app.interfaces import FBSInterface
fbs = FBSInterface('test_solution')
print(f"FBS status: {fbs.get_system_health()}")
```

### **Run Tests**

```bash
# Run FBS tests
python -m pytest fbs_app/tests/ -v

# Run with coverage
python -m pytest fbs_app/tests/ --cov=fbs_app --cov-report=html
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Git not found**: Install Git on your system
2. **Permission denied**: Check SSH keys or use HTTPS
3. **Branch not found**: Verify branch name exists
4. **Installation fails**: Check Python version compatibility

### **Debug Commands**

```bash
# Check Git remote
git remote -v

# Check available branches
git branch -r

# Check specific commit
git show abc1234

# Verify repository access
git ls-remote https://github.com/yourusername/fbs.git
```

## 📚 **Best Practices**

1. **Use specific versions**: Pin to tags or commits for production
2. **Fork for customization**: Don't modify upstream directly
3. **Keep up to date**: Regularly pull from upstream
4. **Test thoroughly**: Always test custom versions
5. **Document changes**: Keep track of customizations
6. **Use virtual environments**: Isolate dependencies

## 🔗 **Quick Start Commands**

```bash
# Quick install from main branch
pip install git+https://github.com/yourusername/fbs.git

# Install specific version
pip install git+https://github.com/yourusername/fbs.git@v2.0.0

# Development install
git clone https://github.com/yourusername/fbs.git
cd fbs
pip install -e .

# Test installation
python -c "import fbs_app; print('FBS installed successfully!')"
```

---

**Need help?** Check the [main README](../README.md) or open an issue on GitHub!
