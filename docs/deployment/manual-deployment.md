# Manual Deployment Guide

This guide provides step-by-step instructions for manually deploying MochaCafe on a Linux server.

## 📋 Prerequisites

- Ubuntu 20.04+ or CentOS 8+ server
- Root or sudo access
- Domain name pointing to your server
- Completed [Environment Setup](environment-setup.md)

## 🚀 Step-by-Step Deployment

### Step 1: System Preparation

#### Update System Packages
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo dnf update -y
```

#### Install Essential Packages
```bash
# Ubuntu/Debian
sudo apt install -y git curl wget vim nginx supervisor
sudo apt install -y python3 python3-pip python3-venv python3-dev
sudo apt install -y postgresql postgresql-contrib redis-server
sudo apt install -y build-essential libpq-dev

# CentOS/RHEL
sudo dnf install -y git curl wget vim nginx supervisor
sudo dnf install -y python3 python3-pip python3-devel
sudo dnf install -y postgresql postgresql-server postgresql-contrib redis
sudo dnf install -y gcc postgresql-devel
```

### Step 2: Create Application User

```bash
# Create dedicated user for the application
sudo useradd --system --shell /bin/bash --home /opt/mochacafe mochacafe
sudo mkdir -p /opt/mochacafe
sudo chown mochacafe:mochacafe /opt/mochacafe
```

### Step 3: Deploy Application Code

```bash
# Switch to application user
sudo -u mochacafe -i

# Clone the repository
cd /opt/mochacafe
git clone https://github.com/your-username/MochaCafe.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Step 4: Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit environment variables (use your production values)
nano .env
```

**Important**: Update `.env` with your production settings from [Environment Setup](environment-setup.md).

### Step 5: Database Setup

#### Initialize PostgreSQL (CentOS only)
```bash
# CentOS/RHEL only
sudo postgresql-setup --initdb
```

#### Start and Enable Services
```bash
sudo systemctl start postgresql redis
sudo systemctl enable postgresql redis
```

#### Create Database and User
```bash
sudo -u postgres psql << EOF
CREATE DATABASE mochacafe_prod;
CREATE USER mochacafe_app WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE mochacafe_prod TO mochacafe_app;
ALTER USER mochacafe_app CREATEDB;
\q
EOF
```

### Step 6: Django Application Setup

```bash
# Switch back to application user
sudo -u mochacafe -i
cd /opt/mochacafe
source venv/bin/activate

# Run Django setup commands
python manage.py collectstatic --noinput
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Test the application
python manage.py check --deploy
```

### Step 7: Configure Gunicorn

#### Create Gunicorn Configuration
```bash
sudo -u mochacafe mkdir -p /opt/mochacafe/config
sudo -u mochacafe tee /opt/mochacafe/config/gunicorn.conf.py << EOF
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/opt/mochacafe/logs/gunicorn_access.log"
errorlog = "/opt/mochacafe/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "mochacafe"

# Server mechanics
daemon = False
pidfile = "/opt/mochacafe/gunicorn.pid"
user = "mochacafe"
group = "mochacafe"
tmp_upload_dir = None

# SSL (if terminating SSL at Gunicorn level)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
EOF
```

#### Create Log Directory
```bash
sudo -u mochacafe mkdir -p /opt/mochacafe/logs
```

### Step 8: Create Systemd Service

#### Create Gunicorn Service File
```bash
sudo tee /etc/systemd/system/mochacafe-web.service << EOF
[Unit]
Description=MochaCafe Gunicorn Application Server
Requires=mochacafe-web.socket
After=network.target

[Service]
Type=notify
User=mochacafe
Group=mochacafe
RuntimeDirectory=mochacafe
WorkingDirectory=/opt/mochacafe
Environment=PATH=/opt/mochacafe/venv/bin
EnvironmentFile=/opt/mochacafe/.env
ExecStart=/opt/mochacafe/venv/bin/gunicorn --config /opt/mochacafe/config/gunicorn.conf.py MochaCafe.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
```

#### Create Socket File
```bash
sudo tee /etc/systemd/system/mochacafe-web.socket << EOF
[Unit]
Description=MochaCafe Gunicorn Socket

[Socket]
ListenStream=/run/mochacafe/socket
SocketUser=www-data
SocketMode=600

[Install]
WantedBy=sockets.target
EOF
```

#### Create Background Worker Service (for printing system)
```bash
sudo tee /etc/systemd/system/mochacafe-worker.service << EOF
[Unit]
Description=MochaCafe Background Worker
After=network.target

[Service]
Type=simple
User=mochacafe
Group=mochacafe
WorkingDirectory=/opt/mochacafe
Environment=PATH=/opt/mochacafe/venv/bin
EnvironmentFile=/opt/mochacafe/.env
ExecStart=/opt/mochacafe/venv/bin/python print_orders.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### Step 9: Configure Nginx

#### Create Nginx Configuration
```bash
sudo tee /etc/nginx/sites-available/mochacafe << EOF
upstream mochacafe_app {
    server unix:/run/mochacafe/socket fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration (will be configured by Certbot)
    # ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;

    # Client max body size
    client_max_body_size 100M;

    # Static files
    location /static/ {
        alias /opt/mochacafe/collected_static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/mochacafe/media/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Main application
    location / {
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # WebSocket support for Django Channels
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        proxy_pass http://mochacafe_app;
    }

    # Health check endpoint
    location /health/ {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
```

#### Enable Nginx Site
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/mochacafe /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 10: SSL Certificate Setup

#### Install Certbot
```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo dnf install certbot python3-certbot-nginx
```

#### Obtain SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Step 11: Start Services

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start and enable services
sudo systemctl start mochacafe-web.socket
sudo systemctl enable mochacafe-web.socket
sudo systemctl start mochacafe-web.service
sudo systemctl enable mochacafe-web.service
sudo systemctl start mochacafe-worker.service
sudo systemctl enable mochacafe-worker.service

# Restart Nginx
sudo systemctl restart nginx
```

### Step 12: Verify Deployment

#### Check Service Status
```bash
sudo systemctl status mochacafe-web
sudo systemctl status mochacafe-worker
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
```

#### Check Application Logs
```bash
# Gunicorn logs
sudo tail -f /opt/mochacafe/logs/gunicorn_error.log

# Systemd logs
sudo journalctl -u mochacafe-web -f
sudo journalctl -u mochacafe-worker -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

#### Test Application
```bash
# Test HTTP redirect
curl -I http://your-domain.com

# Test HTTPS
curl -I https://your-domain.com

# Test application response
curl https://your-domain.com/health/
```

## 🔧 Post-Deployment Configuration

### 1. Set Up Log Rotation

```bash
sudo tee /etc/logrotate.d/mochacafe << EOF
/opt/mochacafe/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 mochacafe mochacafe
    postrotate
        systemctl reload mochacafe-web
    endscript
}
EOF
```

### 2. Configure Backup Script

```bash
sudo tee /opt/mochacafe/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/mochacafe/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U mochacafe_app mochacafe_prod > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/mochacafe/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

sudo chmod +x /opt/mochacafe/backup.sh
sudo chown mochacafe:mochacafe /opt/mochacafe/backup.sh
```

### 3. Set Up Cron Jobs

```bash
sudo -u mochacafe crontab -e

# Add these lines:
# Daily backup at 2 AM
0 2 * * * /opt/mochacafe/backup.sh >> /opt/mochacafe/logs/backup.log 2>&1

# SSL certificate renewal check (twice daily)
0 0,12 * * * /usr/bin/certbot renew --quiet
```

### 4. Configure Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs fail2ban

# Configure fail2ban for SSH protection
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 🔄 Maintenance Commands

### Update Application
```bash
# Switch to application user
sudo -u mochacafe -i
cd /opt/mochacafe

# Backup database
pg_dump -h localhost -U mochacafe_app mochacafe_prod > backup_$(date +%Y%m%d).sql

# Pull latest code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart mochacafe-web
sudo systemctl restart mochacafe-worker
```

### View Logs
```bash
# Application logs
sudo journalctl -u mochacafe-web -f
sudo journalctl -u mochacafe-worker -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -f
```

### Restart Services
```bash
sudo systemctl restart mochacafe-web
sudo systemctl restart mochacafe-worker
sudo systemctl restart nginx
sudo systemctl restart postgresql
sudo systemctl restart redis
```

## ⚠️ Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check service status
sudo systemctl status mochacafe-web

# Check logs
sudo journalctl -u mochacafe-web --no-pager

# Check configuration
sudo nginx -t
```

#### Database Connection Issues
```bash
# Test database connection
sudo -u mochacafe psql -h localhost -U mochacafe_app -d mochacafe_prod

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### Permission Issues
```bash
# Fix file permissions
sudo chown -R mochacafe:mochacafe /opt/mochacafe
sudo chmod -R 755 /opt/mochacafe
sudo chmod 600 /opt/mochacafe/.env
```

---

**Congratulations!** Your MochaCafe application should now be running in production. Visit your domain to access the application and create your first restaurant setup.

For ongoing maintenance, refer to the [Troubleshooting Guide](troubleshooting.md) and [Backup & Recovery](backup-recovery.md) documentation.