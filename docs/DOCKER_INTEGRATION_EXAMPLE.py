"""
FBS FastAPI Docker Integration Example

This example shows how to integrate FBS FastAPI into your solution's Docker setup.
It demonstrates the recommended architecture where FBS runs in Docker but connects
to host-based services (PostgreSQL, Redis, Odoo).
"""

# ============================================================================
# docker-compose.yml EXAMPLE
# ============================================================================

DOCKER_COMPOSE_EXAMPLE = """
version: '3.8'

services:
  your-solution-app:
    # Your main application with FBS embedded
    build:
      context: .
      dockerfile: Dockerfile.your_solution
    container_name: your-solution-app
    ports:
      - "8000:8000"
    environment:
      # ============================================================================
      # APPLICATION CONFIGURATION
      # ============================================================================
      - APP_NAME=Your Solution - Powered by FBS FastAPI
      - APP_VERSION=1.0.0
      - DEBUG=false
      - SECRET_KEY=your-production-secret-key-here

      # ============================================================================
      # DATABASE CONNECTIONS (Host Services)
      # ============================================================================
      # FBS System Database (shared across solutions)
      - DATABASE_URL=postgresql+asyncpg://fbs_user:fbs_password@host.docker.internal:5432/fbs_system_db

      # Your Solution-specific Database (FastAPI data)
      - SOLUTION_DATABASE_URL=postgresql+asyncpg://solution_user:solution_pass@host.docker.internal:5432/fpi_your_solution_db

      # Odoo Database (ERP data)
      - ODOO_DATABASE_URL=postgresql+asyncpg://odoo:odoo_pass@host.docker.internal:5432/fbs_your_solution_db

      # ============================================================================
      # EXTERNAL SERVICE CONNECTIONS
      # ============================================================================
      - REDIS_URL=redis://host.docker.internal:6379/0
      - ODOO_BASE_URL=http://host.docker.internal:8069
      - ODOO_USER=odoo
      - ODOO_PASSWORD=your_odoo_password

      # ============================================================================
      # FBS FEATURE FLAGS
      # ============================================================================
      - ENABLE_MSME_FEATURES=true
      - ENABLE_DMS_FEATURES=true
      - ENABLE_BI_FEATURES=true
      - ENABLE_WORKFLOW_FEATURES=true
      - ENABLE_COMPLIANCE_FEATURES=true
      - ENABLE_ACCOUNTING_FEATURES=true
      - ENABLE_MODULE_GENERATION=true
      - ENABLE_LICENSING_FEATURES=true

      # ============================================================================
      # CORS CONFIGURATION
      # ============================================================================
      - CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
      - CORS_ALLOW_CREDENTIALS=true
      - CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS
      - CORS_ALLOW_HEADERS=Authorization,Content-Type,X-API-Key

      # ============================================================================
      # SECURITY & AUTHENTICATION
      # ============================================================================
      - JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
      - JWT_EXPIRY_HOURS=24
      - TOKEN_EXPIRY_HOURS=24

      # ============================================================================
      # FILE UPLOAD & STORAGE
      # ============================================================================
      - MAX_UPLOAD_SIZE=10485760  # 10MB
      - UPLOAD_PATH=/app/uploads
      - ALLOWED_FILE_TYPES=pdf,doc,docx,xls,xlsx,txt,jpg,jpeg,png

      # ============================================================================
      # LOGGING & MONITORING
      # ============================================================================
      - LOG_LEVEL=INFO
      - LOG_REQUESTS=true
      - LOG_RESPONSES=false

      # ============================================================================
      # RATE LIMITING
      # ============================================================================
      - REQUEST_RATE_LIMIT=5000   # requests per hour
      - REQUEST_BURST_LIMIT=500   # requests per minute

      # ============================================================================
      # CACHE CONFIGURATION
      # ============================================================================
      - CACHE_TIMEOUT=3600
      - CACHE_ENABLED=true

      # ============================================================================
      # MODULE GENERATION
      # ============================================================================
      - MODULE_GENERATOR_OUTPUT_DIR=/app/generated_modules
      - MODULE_GENERATOR_TEMPLATE_DIR=/app/templates
      - MODULE_GENERATOR_MAX_MODULES_PER_TENANT=100
      - MODULE_GENERATOR_RATE_LIMIT_PER_HOUR=10

    # ============================================================================
    # DOCKER NETWORKING & VOLUMES
    # ============================================================================
    network_mode: host  # Access host services directly
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      # Persistent storage for uploads
      - ./uploads:/app/uploads
      # Generated modules storage
      - ./generated_modules:/app/generated_modules
      # Optional: Custom templates
      - ./custom_templates:/app/custom_templates
    restart: unless-stopped

    # ============================================================================
    # HEALTH CHECKS
    # ============================================================================
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

    # ============================================================================
    # RESOURCE LIMITS
    # ============================================================================
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
"""

# ============================================================================
# Dockerfile.your_solution EXAMPLE
# ============================================================================

DOCKERFILE_EXAMPLE = """
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads generated_modules logs

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "main.py"]
"""

# ============================================================================
# requirements.txt EXAMPLE
# ============================================================================

REQUIREMENTS_EXAMPLE = """
# FBS FastAPI Framework
fbs-fastapi>=3.1.0

# Web Framework
fastapi>=0.115.6
uvicorn[standard]>=0.24.0

# Database
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.12.0

# Authentication & Security
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# External Services
redis[hiredis]>=5.0.0
xmlrpc.client>=1.0.0  # Built-in Python

# File Processing
python-magic>=0.4.27
Pillow>=10.0.0

# Utilities
pydantic>=2.5.0
pydantic-settings>=2.1.0
aiofiles>=23.2.1
httpx>=0.25.0

# Optional: Monitoring
sentry-sdk[fastapi]>=1.30.0

# Development
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0  # For testing
"""

# ============================================================================
# .env.example FOR DOCKER
# ============================================================================

ENV_EXAMPLE = """
# =============================================================================
# FBS FASTAPI DOCKER ENVIRONMENT CONFIGURATION
# =============================================================================

# APPLICATION SETTINGS
APP_NAME=Your Solution - Powered by FBS FastAPI
APP_VERSION=1.0.0
DEBUG=false
SECRET_KEY=your-production-secret-key-here-change-this

# =============================================================================
# DATABASE CONNECTIONS (Host Services via host.docker.internal)
# =============================================================================

# FBS System Database - Shared across all solutions
DATABASE_URL=postgresql+asyncpg://fbs_user:fbs_password@host.docker.internal:5432/fbs_system_db

# Your Solution Database - FastAPI business data
SOLUTION_DATABASE_URL=postgresql+asyncpg://solution_user:solution_pass@host.docker.internal:5432/fpi_your_solution_db

# Odoo Database - ERP data
ODOO_DATABASE_URL=postgresql+asyncpg://odoo:odoo_pass@host.docker.internal:5432/fbs_your_solution_db

# =============================================================================
# EXTERNAL SERVICES (Host-based)
# =============================================================================

REDIS_URL=redis://host.docker.internal:6379/0
ODOO_BASE_URL=http://host.docker.internal:8069
ODOO_USER=odoo
ODOO_PASSWORD=your_secure_odoo_password

# =============================================================================
# FBS FEATURE FLAGS
# =============================================================================

ENABLE_MSME_FEATURES=true
ENABLE_DMS_FEATURES=true
ENABLE_BI_FEATURES=true
ENABLE_WORKFLOW_FEATURES=true
ENABLE_COMPLIANCE_FEATURES=true
ENABLE_ACCOUNTING_FEATURES=true
ENABLE_MODULE_GENERATION=true
ENABLE_LICENSING_FEATURES=true

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
JWT_EXPIRY_HOURS=24
TOKEN_EXPIRY_HOURS=24

# =============================================================================
# CORS CONFIGURATION
# =============================================================================

CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,PATCH,OPTIONS
CORS_ALLOW_HEADERS=Authorization,Content-Type,X-API-Key

# =============================================================================
# FILE UPLOAD CONFIGURATION
# =============================================================================

MAX_UPLOAD_SIZE=10485760
UPLOAD_PATH=/app/uploads
ALLOWED_FILE_TYPES=pdf,doc,docx,xls,xlsx,txt,jpg,jpeg,png

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_LEVEL=INFO
LOG_REQUESTS=true
LOG_RESPONSES=false

# =============================================================================
# PERFORMANCE & SCALING
# =============================================================================

DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
REQUEST_RATE_LIMIT=5000
REQUEST_BURST_LIMIT=500
CACHE_TIMEOUT=3600
CACHE_ENABLED=true

# =============================================================================
# MODULE GENERATION
# =============================================================================

MODULE_GENERATOR_OUTPUT_DIR=/app/generated_modules
MODULE_GENERATOR_TEMPLATE_DIR=/app/templates
MODULE_GENERATOR_MAX_MODULES_PER_TENANT=100
MODULE_GENERATOR_RATE_LIMIT_PER_HOUR=10

# =============================================================================
# MONITORING (Optional)
# =============================================================================

# SENTRY_DSN=https://your-sentry-dsn-here
# SENTRY_ENVIRONMENT=production
"""

# ============================================================================
# DOCKER BUILD & RUN SCRIPT
# ============================================================================

BUILD_SCRIPT = """
#!/bin/bash

# FBS FastAPI Docker Build and Deploy Script
# Usage: ./deploy.sh [build|up|down|logs]

set -e

PROJECT_NAME="your-solution"
DOCKER_COMPOSE_FILE="docker-compose.yml"

case "$1" in
    "build")
        echo "🔨 Building FBS FastAPI Docker image..."
        docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache
        echo "✅ Build complete"
        ;;

    "up")
        echo "🚀 Starting FBS FastAPI services..."
        docker-compose -f $DOCKER_COMPOSE_FILE up -d
        echo "⏳ Waiting for services to be healthy..."
        sleep 10
        docker-compose -f $DOCKER_COMPOSE_FILE ps
        echo "🌐 Services available at:"
        echo "  - API: http://localhost:8000"
        echo "  - Docs: http://localhost:8000/docs"
        echo "  - Health: http://localhost:8000/health"
        ;;

    "down")
        echo "🛑 Stopping FBS FastAPI services..."
        docker-compose -f $DOCKER_COMPOSE_FILE down
        echo "✅ Services stopped"
        ;;

    "logs")
        echo "📋 Showing FBS FastAPI logs..."
        docker-compose -f $DOCKER_COMPOSE_FILE logs -f
        ;;

    "restart")
        echo "🔄 Restarting FBS FastAPI services..."
        docker-compose -f $DOCKER_COMPOSE_FILE restart
        echo "✅ Services restarted"
        ;;

    "status")
        echo "📊 FBS FastAPI service status:"
        docker-compose -f $DOCKER_COMPOSE_FILE ps
        echo ""
        echo "🔍 Health check:"
        curl -s http://localhost:8000/health | python3 -m json.tool || echo "Service not responding"
        ;;

    *)
        echo "Usage: $0 {build|up|down|logs|restart|status}"
        echo ""
        echo "Commands:"
        echo "  build   - Build Docker images"
        echo "  up      - Start all services"
        echo "  down    - Stop all services"
        echo "  logs    - Show service logs"
        echo "  restart - Restart services"
        echo "  status  - Show service status"
        exit 1
        ;;
esac
"""

# ============================================================================
# HOST SERVICES SETUP SCRIPT
# ============================================================================

HOST_SETUP_SCRIPT = """
#!/bin/bash

# Host Services Setup for FBS FastAPI
# This script sets up PostgreSQL, Redis, and Odoo on the host machine

set -e

echo "🔧 Setting up host services for FBS FastAPI..."

# Update system
sudo apt-get update

# Install PostgreSQL
echo "📦 Installing PostgreSQL..."
sudo apt-get install -y postgresql postgresql-contrib

# Setup PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create databases and users
sudo -u postgres psql -c "CREATE USER fbs_user WITH PASSWORD 'fbs_password';"
sudo -u postgres psql -c "CREATE DATABASE fbs_system_db OWNER fbs_user;"
sudo -u postgres psql -c "CREATE USER solution_user WITH PASSWORD 'solution_pass';"
sudo -u postgres psql -c "CREATE DATABASE fpi_your_solution_db OWNER solution_user;"
sudo -u postgres psql -c "CREATE USER odoo WITH PASSWORD 'odoo_pass';"
sudo -u postgres psql -c "CREATE DATABASE fbs_your_solution_db OWNER odoo;"

# Install Redis
echo "📦 Installing Redis..."
sudo apt-get install -y redis-server

# Configure Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Install Odoo dependencies
echo "📦 Installing Odoo dependencies..."
sudo apt-get install -y python3 python3-pip python3-dev build-essential libpq-dev

# Create Odoo user and directories
sudo useradd --system --shell /bin/bash --home /opt/odoo --create-home odoo
sudo mkdir -p /opt/odoo/odoo-server

# Download and setup Odoo (example for Odoo 16)
echo "📥 Downloading Odoo..."
cd /opt/odoo/odoo-server
sudo -u odoo git clone https://github.com/odoo/odoo.git --depth 1 --branch 16.0 .

# Install Python dependencies for Odoo
sudo -u odoo pip3 install -r requirements.txt

# Create Odoo configuration
sudo tee /etc/odoo.conf > /dev/null <<EOF
[options]
admin_passwd = admin_password_change_this
db_host = False
db_port = False
db_user = odoo
db_password = odoo_pass
addons_path = /opt/odoo/odoo-server/addons
xmlrpc_port = 8069
xmlrpc_interface = 127.0.0.1
EOF

# Create systemd service for Odoo
sudo tee /etc/systemd/system/odoo.service > /dev/null <<EOF
[Unit]
Description=Odoo
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=/opt/odoo/odoo-server/odoo-bin -c /etc/odoo.conf
KillMode=mixed

[Install]
WantedBy=multi-user.target
EOF

# Enable and start Odoo
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo

# Setup firewall (optional)
sudo ufw allow 8069
sudo ufw allow 5432
sudo ufw allow 6379

echo "✅ Host services setup complete!"
echo ""
echo "📋 Service Status:"
echo "  PostgreSQL: $(sudo systemctl is-active postgresql)"
echo "  Redis: $(sudo systemctl is-active redis-server)"
echo "  Odoo: $(sudo systemctl is-active odoo)"
echo ""
echo "🔗 Connection Details:"
echo "  PostgreSQL: localhost:5432"
echo "  Redis: localhost:6379"
echo "  Odoo: http://localhost:8069"
echo ""
echo "⚠️  Remember to change default passwords in production!"
"""

# ============================================================================
# PRODUCTION NGINX CONFIGURATION
# ============================================================================

NGINX_CONFIG = """
# Nginx Configuration for FBS FastAPI Production Deployment

upstream fbs_fastapi {
    server your-solution-app:8000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Static files (if serving any)
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API endpoints
    location /api/ {
        proxy_pass http://fbs_fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeout settings
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # Health check (internal)
    location /health {
        proxy_pass http://fbs_fastapi;
        access_log off;
    }

    # Main application
    location / {
        proxy_pass http://fbs_fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location /api/business/ {
        limit_req zone=api burst=50 nodelay;
    }

    # Error pages
    error_page 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
"""

# ============================================================================
# MONITORING SETUP
# ============================================================================

MONITORING_SETUP = """
# Monitoring Setup for FBS FastAPI

# 1. Install Prometheus and Grafana
sudo apt-get update
sudo apt-get install -y prometheus grafana

# 2. Configure Prometheus for FBS FastAPI
cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fbs-fastapi'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'  # If you add metrics endpoint

  - job_name: 'odoo'
    static_configs:
      - targets: ['localhost:8069']

  - job_name: 'postgresql'
    static_configs:
      - targets: ['localhost:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:6379']
EOF

# 3. Start monitoring services
sudo systemctl start prometheus
sudo systemctl start grafana
sudo systemctl enable prometheus
sudo systemctl enable grafana

# 4. Access points
echo "📊 Monitoring URLs:"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000 (admin/admin)"

# 5. Add health check monitoring
# Add this to your FastAPI app for Prometheus metrics
# from prometheus_fastapi_instrumentator import Instrumentator
# Instrumentator().instrument(app).expose(app)
"""

# ============================================================================
# BACKUP SCRIPT
# ============================================================================

BACKUP_SCRIPT = """
#!/bin/bash

# FBS FastAPI Backup Script
# Backs up databases and application data

set -e

BACKUP_DIR="/opt/fbs_backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

echo "🔄 Starting FBS FastAPI backup..."

# Backup PostgreSQL databases
echo "💾 Backing up databases..."
pg_dump -h localhost -U fbs_user -d fbs_system_db > $BACKUP_DIR/fbs_system_$DATE.sql
pg_dump -h localhost -U solution_user -d fpi_your_solution_db > $BACKUP_DIR/fpi_solution_$DATE.sql
pg_dump -h localhost -U odoo -d fbs_your_solution_db > $BACKUP_DIR/odoo_solution_$DATE.sql

# Backup Redis data
echo "💾 Backing up Redis..."
redis-cli --rdb $BACKUP_DIR/redis_$DATE.rdb

# Backup application files
echo "💾 Backing up application data..."
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /app/uploads/
tar -czf $BACKUP_DIR/generated_modules_$DATE.tar.gz /app/generated_modules/

# Compress all backups
cd $BACKUP_DIR
tar -czf fbs_backup_$DATE.tar.gz *.sql *.rdb *.tar.gz
rm *.sql *.rdb *.tar.gz

echo "✅ Backup complete: $BACKUP_DIR/fbs_backup_$DATE.tar.gz"

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "fbs_backup_*.tar.gz" -mtime +7 -delete

echo "🧹 Cleaned up old backups"
"""

# ============================================================================
# TROUBLESHOOTING GUIDE
# ============================================================================

TROUBLESHOOTING = """
# FBS FastAPI Docker Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Connection Issues
**Error**: `Connection refused` or `database not available`

**Solutions**:
- Ensure PostgreSQL is running on host: `sudo systemctl status postgresql`
- Check database credentials in .env file
- Verify `host.docker.internal` resolution: `docker exec -it container ping host.docker.internal`
- Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`

### 2. Odoo Integration Issues
**Error**: `Odoo connection failed`

**Solutions**:
- Verify Odoo is running: `sudo systemctl status odoo`
- Check Odoo credentials in .env file
- Test Odoo XML-RPC: `python3 -c "import xmlrpc.client; print(xmlrpc.client.ServerProxy('http://localhost:8069/xmlrpc/2/common').version())"`
- Check Odoo logs: `sudo tail -f /var/log/odoo/odoo-server.log`

### 3. Redis Connection Issues
**Error**: `Redis connection failed`

**Solutions**:
- Ensure Redis is running: `sudo systemctl status redis-server`
- Check Redis configuration: `redis-cli ping`
- Verify Redis URL in .env file

### 4. Port Conflicts
**Error**: `Port already in use`

**Solutions**:
- Check what's using the port: `sudo netstat -tulpn | grep :8000`
- Stop conflicting service or change port in docker-compose.yml
- Use `network_mode: host` carefully

### 5. Permission Issues
**Error**: `Permission denied` on volumes

**Solutions**:
- Ensure proper user permissions on host directories
- Check Docker volume mounts in docker-compose.yml
- Use proper user in Dockerfile: `USER app`

### 6. Module Generation Issues
**Error**: `Module generation failed`

**Solutions**:
- Ensure templates directory exists and is writable
- Check module generation permissions
- Verify Jinja2 templates are valid
- Check generated_modules directory permissions

### 7. Health Check Failures
**Error**: `Health check failed`

**Solutions**:
- Check application logs: `docker-compose logs fbs-fastapi`
- Verify all dependencies are installed
- Check database connectivity from within container
- Ensure proper startup order in docker-compose.yml

### 8. Performance Issues
**Symptoms**: Slow response times, high memory usage

**Solutions**:
- Increase database connection pool size
- Enable Redis caching
- Add rate limiting
- Monitor resource usage with `docker stats`
- Check database query performance

### 9. CORS Issues
**Error**: `CORS policy blocked`

**Solutions**:
- Verify CORS_ORIGINS in .env file
- Check CORS_ALLOW_CREDENTIALS setting
- Ensure proper headers in requests

### 10. File Upload Issues
**Error**: `Upload failed`

**Solutions**:
- Check MAX_UPLOAD_SIZE setting
- Verify ALLOWED_FILE_TYPES
- Ensure upload directory is writable
- Check file permissions

## Debug Commands

### Container Debugging
```bash
# Access container shell
docker exec -it your-solution-app bash

# Check application logs
docker-compose logs -f fbs-fastapi

# Monitor resource usage
docker stats

# Check container health
docker ps
```

### Database Debugging
```bash
# Connect to PostgreSQL
psql -h localhost -U fbs_user -d fbs_system_db

# Check active connections
SELECT * FROM pg_stat_activity;

# Check database size
SELECT pg_size_pretty(pg_database_size('fbs_system_db'));
```

### Network Debugging
```bash
# Test host connectivity from container
docker exec -it your-solution-app ping host.docker.internal

# Check port availability
netstat -tulpn | grep :8000

# Test service connectivity
curl http://localhost:8000/health
```

### Application Debugging
```bash
# Enable debug mode
DEBUG=true docker-compose up

# Check FBS configuration
curl http://localhost:8000/debug/config

# Test FBS services
curl http://localhost:8000/health/detailed
```

## Getting Help

1. Check the logs first: `docker-compose logs`
2. Verify configuration: `docker exec -it container cat .env`
3. Test individual components
4. Check GitHub issues for similar problems
5. Provide detailed error logs when asking for help
"""

# ============================================================================
# PRINT EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("FBS FastAPI Docker Integration Examples")
    print("=" * 50)
    print("\n📋 Available Examples:")
    print("1. docker-compose.yml - Main Docker configuration")
    print("2. Dockerfile - Application container setup")
    print("3. requirements.txt - Python dependencies")
    print("4. .env.example - Environment configuration")
    print("5. deploy.sh - Build and deployment script")
    print("6. host-setup.sh - Host services setup")
    print("7. nginx.conf - Production web server config")
    print("8. monitoring-setup.sh - Monitoring configuration")
    print("9. backup.sh - Backup script")
    print("10. troubleshooting.md - Troubleshooting guide")
    print("\n🔗 Copy the examples above to create your Docker setup!")
