#!/bin/bash

# FBS API Deployment Script
# This script sets up the FBS API on a VPS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FBS_USER="fbs"
FBS_GROUP="fbs"
FBS_HOME="/opt/fbs-api"
FBS_LOG_DIR="/var/log/fbs-api"
FBS_RUN_DIR="/var/run"

echo -e "${GREEN}🚀 FBS API Deployment Script${NC}"
echo "=================================="

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   exit 1
fi

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Install required packages
echo -e "${YELLOW}📦 Installing required packages...${NC}"
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git curl

# Create FBS user and group
echo -e "${YELLOW}👤 Creating FBS user and group...${NC}"
if ! getent group $FBS_GROUP > /dev/null 2>&1; then
    groupadd $FBS_GROUP
fi

if ! getent passwd $FBS_USER > /dev/null 2>&1; then
    useradd -r -g $FBS_GROUP -d $FBS_HOME -s /bin/bash $FBS_USER
fi

# Create directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p $FBS_HOME
mkdir -p $FBS_LOG_DIR
mkdir -p $FBS_RUN_DIR

# Set permissions
chown -R $FBS_USER:$FBS_GROUP $FBS_HOME
chown -R $FBS_USER:$FBS_GROUP $FBS_LOG_DIR
chmod 755 $FBS_HOME
chmod 755 $FBS_LOG_DIR

# Clone repository (if not already present)
if [ ! -d "$FBS_HOME/.git" ]; then
    echo -e "${YELLOW}📥 Cloning FBS API repository...${NC}"
    cd $FBS_HOME
    # Clone the FBS repository
    git clone https://github.com/kuriadn/fbs.git .
    chown -R $FBS_USER:$FBS_GROUP $FBS_HOME
else
    echo -e "${YELLOW}📥 Updating FBS API repository...${NC}"
    cd $FBS_HOME
    git pull origin main
    chown -R $FBS_USER:$FBS_GROUP $FBS_HOME
fi

# Create virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
cd $FBS_HOME
sudo -u $FBS_USER python3 -m venv venv
sudo -u $FBS_USER $FBS_HOME/venv/bin/pip install --upgrade pip
sudo -u $FBS_USER $FBS_HOME/venv/bin/pip install -r requirements.txt

# Setup environment file
echo -e "${YELLOW}⚙️ Setting up environment configuration...${NC}"
if [ ! -f "$FBS_HOME/.env" ]; then
    cp $FBS_HOME/env.example $FBS_HOME/.env
    echo -e "${YELLOW}⚠️ Please edit $FBS_HOME/.env with your configuration${NC}"
fi

# Setup PostgreSQL
echo -e "${YELLOW}🐘 Setting up PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE USER fbs_user WITH PASSWORD 'fbs_password';" || true
sudo -u postgres psql -c "CREATE DATABASE fbs_db OWNER fbs_user;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fbs_db TO fbs_user;" || true

# Run migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
cd $FBS_HOME
sudo -u $FBS_USER $FBS_HOME/venv/bin/python manage.py migrate

# Create superuser (optional)
echo -e "${YELLOW}👤 Creating superuser...${NC}"
echo "You can create a superuser now or later with:"
echo "sudo -u $FBS_USER $FBS_HOME/venv/bin/python manage.py createsuperuser"

# Setup systemd service
echo -e "${YELLOW}🔧 Setting up systemd service...${NC}"
cat > /etc/systemd/system/fbs-api.service << EOF
[Unit]
Description=FBS API
After=network.target postgresql.service

[Service]
Type=simple
User=$FBS_USER
Group=$FBS_GROUP
WorkingDirectory=$FBS_HOME
Environment=PATH=$FBS_HOME/venv/bin
ExecStart=$FBS_HOME/venv/bin/gunicorn -c gunicorn.conf.py fbs.wsgi:application
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Setup Nginx
echo -e "${YELLOW}🌐 Setting up Nginx...${NC}"
cat > /etc/nginx/sites-available/fbs-api << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $FBS_HOME/static/;
    }

    location /media/ {
        alias $FBS_HOME/media/;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/fbs-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
cd $FBS_HOME
sudo -u $FBS_USER $FBS_HOME/venv/bin/python manage.py collectstatic --noinput

# Enable and start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
systemctl daemon-reload
systemctl enable fbs-api
systemctl start fbs-api
systemctl restart nginx

# Setup firewall
echo -e "${YELLOW}🔥 Setting up firewall...${NC}"
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# Health check
echo -e "${YELLOW}🏥 Performing health check...${NC}"
sleep 5
if curl -f http://localhost:8001/api/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✅ FBS API is running successfully!${NC}"
else
    echo -e "${RED}❌ FBS API health check failed${NC}"
    echo "Check logs with: journalctl -u fbs-api -f"
fi

echo -e "${GREEN}🎉 Deployment completed!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "1. Edit $FBS_HOME/.env with your configuration"
echo "2. Update /etc/nginx/sites-available/fbs-api with your domain"
echo "3. Create a superuser: sudo -u $FBS_USER $FBS_HOME/venv/bin/python manage.py createsuperuser"
echo "4. Check logs: journalctl -u fbs-api -f"
echo "5. Restart services if needed: systemctl restart fbs-api nginx"
echo ""
echo -e "${GREEN}🌐 Your FBS API should be available at: http://your-domain.com${NC}"