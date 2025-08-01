# FBS (Fayvad Business System) API

A comprehensive REST API for integrating with Odoo systems, managing workflows, business intelligence, and enterprise operations. This API serves as the backbone for building scalable business applications that can dynamically adapt to different industries and business domains.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Odoo instance (for integration)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kuriadn/fbs.git
   cd fbs
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start the server**
   ```bash
   python manage.py runserver 0.0.0.0:8001
   ```

## 📋 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com,localhost

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fbs_db

# Odoo Integration
ODOO_URL=http://localhost:8069
ODOO_DB=odoo_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# API Settings
API_VERSION=v1
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com

# Security
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=86400
```

## 🏗️ Architecture

```
FBS API
├── Core Operations (CRUD)
├── Discovery & Profiling
├── Authentication & Security
├── Business Endpoints
├── Business Intelligence
├── Error Handling
└── Webhooks & Integrations
```

## 📚 API Documentation

Comprehensive API documentation is available in the `docs/api/` directory:

- [01. API Overview](docs/api/01_overview.md)
- [02. Core Operations](docs/api/02_core_operations.md)
- [03. Discovery & Profiling](docs/api/03_discovery_profiling.md)
- [04. Authentication & Security](docs/api/04_authentication.md)
- [05. Business Endpoints](docs/api/05_business_endpoints.md)
- [06. Business Intelligence](docs/api/06_business_intelligence.md)
- [07. Error Handling](docs/api/07_error_handling.md)
- [08. Webhooks & Integrations](docs/api/08_webhooks_integrations.md)

## 🔧 Management Commands

### Discovery Commands
```bash
# Test discovery system
python manage.py test_discovery --action phase1
python manage.py test_discovery --action phase2 --solution-name my_solution --requirements requirements.json
python manage.py test_discovery --action status --solution-name my_solution

# Generate APIs
python manage.py generate_apis --solution-name my_solution
```

### Database Commands
```bash
# Create solution database
python manage.py create_solution_db --name my_solution --domain rental

# List solutions
python manage.py list_solutions
```

## 🚀 Production Deployment

### Using Gunicorn

1. **Install Gunicorn**
   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn config**
   ```bash
   # gunicorn.conf.py
   bind = "0.0.0.0:8001"
   workers = 4
   worker_class = "sync"
   worker_connections = 1000
   timeout = 30
   keepalive = 2
   ```

3. **Start with Gunicorn**
   ```bash
   gunicorn -c gunicorn.conf.py fbs.wsgi:application
   ```

### Using Systemd Service

Create `/etc/systemd/system/fbs-api.service`:

```ini
[Unit]
Description=FBS API
After=network.target

[Service]
Type=simple
User=fbs
Group=fbs
WorkingDirectory=/opt/fbs-api
Environment=PATH=/opt/fbs-api/venv/bin
ExecStart=/opt/fbs-api/venv/bin/gunicorn -c gunicorn.conf.py fbs.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable fbs-api
sudo systemctl start fbs-api
```

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- API key management
- Rate limiting
- CORS configuration
- Input validation and sanitization

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8001/api/health/
```

### Status Endpoints
```bash
# API status
curl http://localhost:8001/api/status/

# Database status
curl http://localhost:8001/api/db/status/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the [API Documentation](docs/api/)
- Review the [Issues](https://github.com/kuriadn/fbs/issues)
- Contact: support@fayvad.com

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added Business Intelligence features
- **v1.2.0** - Enhanced webhook and integration capabilities
