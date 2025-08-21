# FBS App Security Guide

## 🔒 Security Overview

The FBS app implements several security measures to protect against common vulnerabilities and ensure secure operation in production environments.

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
```

### 3. **Configuration in Django Settings**

```python
# settings.py
FBS_APP = {
    'ODOO_BASE_URL': 'https://your-odoo-server.com',
    'DATABASE_USER': 'odoo',
    'DATABASE_PASSWORD': os.getenv('ODOO_DATABASE_PASSWORD'),
    'default_database_config': {
        'host': 'localhost',
        'port': 5432,
        'user': 'postgres',
        'password': os.getenv('POSTGRES_PASSWORD'),
    },
}
```

## 🛡️ Security Features

### 1. **Handshake Authentication**
- Secure token-based authentication
- Configurable expiry times
- Rate limiting support

### 2. **Database Isolation**
- Multi-tenant database architecture
- Solution-specific database routing
- Middleware-based security enforcement

### 3. **Input Validation**
- Comprehensive input sanitization
- Field length validation
- Type checking and validation

### 4. **Error Handling**
- Specific exception handling
- No internal error exposure
- Secure error logging

## 🔐 Production Deployment Checklist

- [ ] **Environment Variables**: All credentials set via environment variables
- [ ] **Hardcoded Passwords**: No hardcoded passwords in code
- [ ] **HTTPS**: Odoo server accessible via HTTPS
- [ ] **Firewall**: Database ports restricted to application servers
- [ ] **Secrets Management**: Use proper secrets management (Vault, AWS Secrets Manager, etc.)
- [ ] **Regular Updates**: Keep dependencies updated
- [ ] **Monitoring**: Implement security monitoring and alerting

## 🚫 Security Anti-Patterns

### 1. **Broad Exception Handling**
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

### 2. **Direct Database Queries**
```python
# ❌ DON'T DO THIS
cursor.execute(f"SELECT * FROM {table_name}")  # SQL injection risk
```

```python
# ✅ DO THIS INSTEAD
cursor.execute("SELECT * FROM %s", (table_name,))  # Parameterized query
```

### 3. **Unvalidated User Input**
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
