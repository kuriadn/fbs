# FBS FastAPI v3.1.0 - Deployment Guide

## 🏗️ **Architecture Overview**

**FBS FastAPI uses a hybrid deployment architecture:**

```
┌─────────────────┐     ┌─────────────────┐
│   Host Machine  │     │   Docker        │
│                 │     │   Container     │
├─────────────────┤     ├─────────────────┤
│ • PostgreSQL    │◄────┤ • FBS FastAPI   │
│   (localhost)   │     │   (Container)   │
│ • Redis         │◄────┤                 │
│   (localhost)   │     │ • Generated     │
│ • Odoo          │◄────┤   Modules       │
│   (localhost)   │     │ • Static Files  │
│ • Nginx         │     └─────────────────┘
│   (localhost)   │
└─────────────────┘
```

**Why this architecture?**
- **Database persistence**: Host-based PostgreSQL for data persistence
- **Service isolation**: Redis, Odoo, Nginx remain on host for flexibility
- **Application containerization**: FBS FastAPI runs in Docker for easy deployment
- **Host networking**: Direct access to host services via `host.docker.internal`

---

## 🐳 **Docker Deployment (Recommended)**

### **Prerequisites**

Ensure these services are running on your host machine:

#### **1. PostgreSQL Setup**
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create FBS database and user
sudo -u postgres psql
```

```sql
-- In PostgreSQL shell
CREATE USER fbs_user WITH PASSWORD 'fbs_password';
CREATE DATABASE fbs_system_db OWNER fbs_user;
GRANT ALL PRIVILEGES ON DATABASE fbs_system_db TO fbs_user;
\q
```

```bash
# Test connection
psql -h localhost -U fbs_user -d fbs_system_db
# Enter password: fbs_password
```

#### **2. Redis Setup**
```bash
# Install Redis
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping  # Should return PONG
```

#### **3. Odoo Setup (Optional)**
```bash
# Install Odoo dependencies
sudo apt install python3-pip postgresql-client python3-dev libxml2-dev libxslt1-dev zlib1g-dev libsasl2-dev libldap2-dev build-essential

# Create Odoo user
sudo useradd -m -d /opt/odoo -U -r -s /bin/bash odoo

# Download and install Odoo
cd /opt/odoo
sudo -u odoo git clone https://github.com/odoo/odoo.git --depth 1 --branch 17.0
cd odoo
sudo -u odoo pip3 install -r requirements.txt

# Configure Odoo
sudo -u odoo cp debian/odoo.conf /etc/odoo.conf
sudo nano /etc/odoo.conf  # Edit database settings
```

#### **4. Nginx Setup (Optional)**
```bash
# Install Nginx
sudo apt install nginx

# Configure reverse proxy (see nginx/nginx.conf example)
sudo cp nginx/nginx.conf /etc/nginx/sites-available/fbs
sudo ln -s /etc/nginx/sites-available/fbs /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### **FBS FastAPI Deployment**

```bash
# Clone repository
git clone https://github.com/kuriadn/fbs.git
cd fbs

# Start FBS FastAPI (connects to host services)
docker-compose up -d

# Check logs
docker-compose logs -f fbs-fastapi

# Verify deployment
curl http://localhost:8000/health
```

### **Environment Configuration**

Create `.env` file in the project root:

```bash
# FBS Application
APP_NAME="FBS - Fayvad Business Suite"
APP_VERSION="3.1.0"
DEBUG=false
SECRET_KEY="your-super-secret-key-here"

# Host Database (via host.docker.internal)
DATABASE_URL="postgresql+asyncpg://fbs_user:fbs_password@host.docker.internal:5432/fbs_system_db"

# Host Redis
REDIS_URL="redis://host.docker.internal:6379/0"

# Host Odoo
ODOO_BASE_URL="http://host.docker.internal:8069"
ODOO_USER="odoo"
ODOO_PASSWORD="odoo_password"

# Module Generation
ENABLE_MODULE_GENERATION=true
MODULE_OUTPUT_DIR="./generated_modules"
```

---

## 🔧 **Manual Deployment (Development)**

### **Local Development Setup**

```bash
# Clone repository
git clone https://github.com/kuriadn/fbs.git
cd fbs/fbs_django

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r ../requirements-dev.txt

# Set environment variables
export DJANGO_SETTINGS_MODULE=config.settings
export DB_NAME="fbs_system_db"
export DB_USER="fayvad"
export DB_PASSWORD="MeMiMo@0207"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="your-secret-key"

# Run database migrations
python manage.py migrate

# Run application
python manage.py runserver 0.0.0.0:8000
```

---

## 🔗 **Network Architecture Details**

### **Host Network Mode**
FBS FastAPI uses `network_mode: host` in Docker Compose:

```yaml
services:
  fbs-fastapi:
    network_mode: host  # Direct access to host network
    extra_hosts:
      - "host.docker.internal:host-gateway"  # Docker Desktop compatibility
```

**Benefits:**
- Direct access to host services (PostgreSQL, Redis, Odoo)
- No port conflicts or network configuration
- Better performance (no network overhead)
- Simplified service discovery

### **Service Connections**

| Service | Host Address | Docker Address | Purpose |
|---------|-------------|----------------|---------|
| PostgreSQL | `localhost:5432` | `host.docker.internal:5432` | Database |
| Redis | `localhost:6379` | `host.docker.internal:6379` | Caching |
| Odoo | `localhost:8069` | `host.docker.internal:8069` | ERP |
| FBS API | `localhost:8000` | N/A (host mode) | API |

---

## 🔍 **Troubleshooting**

### **Database Connection Issues**

**Problem:** `Connection refused` to PostgreSQL
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Test connection
psql -h localhost -U fbs_user -d fbs_system_db
```

**Problem:** Docker can't connect to host PostgreSQL
```bash
# Check if PostgreSQL accepts connections from Docker
# Edit /etc/postgresql/*/main/pg_hba.conf
# Add: host    all    fbs_user    172.17.0.0/16    md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### **Redis Connection Issues**

**Problem:** Redis connection refused
```bash
# Check Redis status
sudo systemctl status redis-server

# Test Redis connectivity
redis-cli ping

# Check Redis configuration
sudo nano /etc/redis/redis.conf
# Ensure: bind 0.0.0.0 or specific IP
```

### **Odoo Connection Issues**

**Problem:** FBS can't connect to Odoo
```bash
# Check Odoo status
sudo systemctl status odoo

# Check Odoo logs
sudo tail -f /var/log/odoo/odoo.log

# Test Odoo API
curl -X POST http://localhost:8069/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "call", "params": {"db": "your_db", "login": "admin", "password": "password"}}'
```

### **Docker Network Issues**

**Problem:** `host.docker.internal` not working
```bash
# For Docker Desktop
# Add to docker-compose.yml
extra_hosts:
  - "host.docker.internal:host-gateway"

# For Linux Docker
# Use actual host IP or add to /etc/hosts
echo "172.17.0.1 host.docker.internal" >> /etc/hosts
```

---

## 📊 **Performance Optimization**

### **PostgreSQL Tuning**
```sql
-- Optimize for FBS workload
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### **Redis Configuration**
```bash
# /etc/redis/redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
tcp-keepalive 300
timeout 300
```

### **FBS FastAPI Configuration**
```bash
# Environment variables for performance
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
CACHE_TIMEOUT=300
WORKERS=4  # For production
```

---

## 🔒 **Security Considerations**

### **Database Security**
```sql
-- Create restricted user for FBS
CREATE USER fbs_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE fbs_system_db TO fbs_user;
GRANT USAGE ON SCHEMA public TO fbs_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO fbs_user;
```

### **Network Security**
```bash
# Configure PostgreSQL to only accept connections from Docker
# /etc/postgresql/*/main/pg_hba.conf
host    fbs_system_db    fbs_user    172.17.0.0/16    md5
```

### **Application Security**
```bash
# Use strong secrets
SECRET_KEY="generate-strong-random-key"
JWT_SECRET_KEY="separate-jwt-key"

# Enable HTTPS in production
# Configure Nginx with SSL certificates
```

---

## 📋 **Monitoring & Maintenance**

### **Health Checks**
```bash
# FBS Health Check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/health/detailed

# Service monitoring
docker-compose logs -f fbs-fastapi
```

### **Backup Strategy**
```bash
# Database backup
pg_dump -U fbs_user -h localhost fbs_system_db > fbs_backup_$(date +%Y%m%d).sql

# Docker volumes backup
docker run --rm -v fbs_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .
```

### **Log Management**
```bash
# Application logs
docker-compose logs fbs-fastapi > fbs_app_$(date +%Y%m%d).log

# System logs
sudo journalctl -u postgresql
sudo journalctl -u redis-server
sudo journalctl -u nginx
```

---

## 🚀 **Production Deployment Checklist**

### **Pre-Deployment**
- [ ] PostgreSQL installed and configured
- [ ] Redis installed and running
- [ ] Odoo installed (if needed)
- [ ] Nginx configured (if needed)
- [ ] SSL certificates (for production)
- [ ] Firewall configured
- [ ] Backup strategy in place

### **Deployment**
- [ ] Repository cloned
- [ ] Environment variables configured
- [ ] Docker Compose built
- [ ] Services started
- [ ] Health checks passing
- [ ] API documentation accessible

### **Post-Deployment**
- [ ] Monitoring configured
- [ ] Log rotation setup
- [ ] Backup automation configured
- [ ] Performance monitoring active
- [ ] Security hardening applied

---

**This deployment architecture ensures FBS FastAPI runs in Docker while maintaining direct, high-performance access to host-based services like PostgreSQL, Redis, and Odoo.**
