# FBS Comprehensive Security Guide

## 🔒 Security Overview

The FBS ecosystem (FBS App, DMS, and License Manager) implements comprehensive security measures to protect against common vulnerabilities and ensure secure operation in production environments. This guide covers security for all three apps.

## 🚨 Critical Security Requirements

### 1. **NO HARDCODED CREDENTIALS**

**❌ NEVER DO THIS:**
```python
password = 'four@One2'  # HARDCODED - SECURITY RISK!
```

**✅ ALWAYS DO THIS:**
```python
password = os.getenv('ODOO_DATABASE_PASSWORD')
if not password:
    raise ValueError('ODOO_DATABASE_PASSWORD environment variable is required')
```

### 2. **Required Environment Variables**

Set these environment variables in your production environment:

```bash
# Odoo Database Credentials
ODOO_DATABASE_USER=odoo
ODOO_DATABASE_PASSWORD=your_secure_odoo_password

# PostgreSQL Credentials
POSTGRES_PASSWORD=your_secure_postgres_password

# Django Secret Key
DJANGO_SECRET_KEY=your-super-secret-key-here

# FBS License Manager
FBS_LICENSE_TYPE=professional
FBS_ENABLE_LICENSING=true
FBS_MSME_BUSINESSES_LIMIT=10
FBS_WORKFLOWS_LIMIT=50
FBS_REPORTS_LIMIT=1000
FBS_USERS_LIMIT=25
FBS_DOCUMENTS_LIMIT=5000
FBS_STORAGE_GB_LIMIT=100
```

### 3. **Configuration in Django Settings**

```python
# settings.py
FBS_APP = {
    'ODOO_BASE_URL': 'https://your-odoo-server.com',
    'DATABASE_USER': 'odoo',
    'DATABASE_PASSWORD': os.getenv('ODOO_DATABASE_PASSWORD'),
    'ENABLE_MSME_FEATURES': True,
    'ENABLE_BI_FEATURES': True,
    'ENABLE_WORKFLOW_FEATURES': True,
    'ENABLE_COMPLIANCE_FEATURES': True,
    'ENABLE_ACCOUNTING_FEATURES': True,
    'CACHE_ENABLED': True,
    'CACHE_TIMEOUT': 300,
}

FBS_DMS = {
    'UPLOAD_PATH': 'documents/',
    'MAX_FILE_SIZE': 10485760,  # 10MB
    'ALLOWED_EXTENSIONS': ['.pdf', '.doc', '.docx', '.xls', '.xlsx'],
    'ENABLE_VERSIONING': True,
    'ENABLE_WORKFLOWS': True,
}

FBS_LICENSE_MANAGER = {
    'ENABLE_LICENSING': True,
    'LICENSE_TYPE': 'professional',
    'FEATURE_LIMITS': {
        'msme_businesses': 10,
        'workflows': 50,
        'reports': 1000,
        'users': 25,
        'documents': 5000,
        'storage_gb': 100
    }
}
```

## 🛡️ Security Features

### 1. **Solution-Aware Architecture**
- **Solution isolation** through `solution_name` parameter
- **Multi-tenant database architecture** with automatic routing
- **Solution-specific database routing** via `FBSDatabaseRouter`
- **Middleware-based security enforcement**

### 2. **Handshake Authentication**
- Secure token-based authentication
- Configurable expiry times
- Rate limiting support

### 3. **License-Based Feature Control**
- **Feature flags** for conditional functionality
- **Usage limits** enforcement
- **License validation** and expiry checking
- **Upgrade prompts** for feature access

### 4. **Input Validation**
- Comprehensive input sanitization
- Field length validation
- Type checking and validation

### 5. **Error Handling**
- Specific exception handling
- No internal error exposure
- Secure error logging

### 6. **Document Security**
- **Confidentiality levels** (internal, confidential, restricted)
- **Access control** based on user permissions
- **Workflow approvals** for sensitive documents
- **Audit trails** for all document operations

## 🔐 Production Deployment Checklist

- [ ] **Environment Variables**: All credentials set via environment variables
- [ ] **Hardcoded Passwords**: No hardcoded passwords in code
- [ ] **HTTPS**: Odoo server accessible via HTTPS
- [ ] **Firewall**: Database ports restricted to application servers
- [ ] **Secrets Management**: Use proper secrets management (Vault, AWS Secrets Manager, etc.)
- [ ] **Regular Updates**: Keep dependencies updated
- [ ] **Monitoring**: Implement security monitoring and alerting
- [ ] **Solution Isolation**: Verify solution_name parameter usage in all services
- [ ] **License Validation**: Test license manager and feature flags
- [ ] **Document Security**: Verify confidentiality levels and access controls
- [ ] **Database Routing**: Test multi-database routing and isolation

## 🚫 Security Anti-Patterns

### 1. **Missing Solution Context**
```python
# ❌ DON'T DO THIS
service = MSMEService()  # Missing solution_name parameter
```

```python
# ✅ DO THIS INSTEAD
service = MSMEService('your_solution_name')  # Always provide solution_name
```

### 2. **Broad Exception Handling**
```python
# ❌ DON'T DO THIS
try:
    # ... code ...
except Exception as e:
    return {'error': str(e)}  # Exposes internal errors
```

```python
# ✅ DO THIS INSTEAD
try:
    # ... code ...
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    return {'error': 'Operation failed'}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {'error': 'Internal server error'}
```

### 3. **Direct Database Queries**
```python
# ❌ DON'T DO THIS
cursor.execute(f"SELECT * FROM {table_name}")  # SQL injection risk
```

```python
# ✅ DO THIS INSTEAD
cursor.execute("SELECT * FROM %s", (table_name,))  # Parameterized query
```

### 4. **Bypassing License Checks**
```python
# ❌ DON'T DO THIS
# Directly accessing features without license validation
if some_condition:
    use_licensed_feature()  # No license check
```

```python
# ✅ DO THIS INSTEAD
# Always check license before using features
if license_manager.has_feature('msme') and feature_flags.is_enabled('msme'):
    use_licensed_feature()
else:
    handle_feature_unavailable()
```

### 5. **Unvalidated User Input**
```python
# ❌ DON'T DO THIS
username = request.POST.get('username')  # No validation
```

```python
# ✅ DO THIS INSTEAD
username = request.POST.get('username', '').strip()
if not username or len(username) > 150:
    return JsonResponse({'error': 'Invalid username'}, status=400)
```

### 6. **Document Access Without Permissions**
```python
# ❌ DON'T DO THIS
document = Document.objects.get(id=doc_id)  # No permission check
```

```python
# ✅ DO THIS INSTEAD
document = doc_service.get_document(doc_id)  # Service handles permissions
if not doc_service._can_access_document(document, user):
    raise PermissionDenied("Access denied")
```

## 🔍 Security Testing

### 1. **Run Security Tests**
```bash
# Install security testing tools
pip install bandit safety

# Run security audit
bandit -r fbs_app/

# Check for known vulnerabilities
safety check
```

### 2. **Common Security Issues to Check**
- [ ] Hardcoded credentials
- [ ] SQL injection vulnerabilities
- [ ] Cross-site scripting (XSS)
- [ ] Cross-site request forgery (CSRF)
- [ ] Insecure direct object references
- [ ] Missing input validation
- [ ] Information disclosure
- [ ] Missing solution_name parameter in services
- [ ] License bypass attempts
- [ ] Document permission violations
- [ ] Database routing misconfigurations
- [ ] Feature flag bypasses

## 📞 Security Contact

If you discover a security vulnerability in the FBS app:

1. **DO NOT** create a public issue
2. **DO** contact the security team privately
3. **DO** provide detailed reproduction steps
4. **DO** wait for acknowledgment before public disclosure

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Python Security](https://python-security.readthedocs.io/)
