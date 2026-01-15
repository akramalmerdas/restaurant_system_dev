# Environment Setup Guide

This guide covers the complete environment configuration for MochaCafe deployment.

## 📋 Environment Variables Reference

### Django Core Settings

```bash
# REQUIRED: Django secret key for cryptographic signing
DJANGO_SECRET_KEY=your-very-long-random-secret-key-here-50-characters-minimum

# REQUIRED: Debug mode (NEVER set to True in production)
DEBUG=False

# REQUIRED: Allowed hosts (comma-separated list)
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,your-server-ip
```

### Database Configuration

```bash
# REQUIRED: PostgreSQL database settings
DB_NAME=mochacafe_production
DB_USER=mochacafe_user
DB_PASSWORD=your-secure-database-password
DB_HOST=localhost
DB_PORT=5432
```

### Redis Configuration

```bash
# REQUIRED: Redis settings for real-time features
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password-if-auth-enabled
```

## 🔧 Environment File Setup

### 1. Create Production Environment File

```bash
# Copy the example file
cp .env.example .env

# Edit with your production values
nano .env
```

### 2. Generate Secure Secret Key

```python
# Run this Python script to generate a secure secret key
import secrets
import string

alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
secret_key = ''.join(secrets.choice(alphabet) for i in range(50))
print(f"DJANGO_SECRET_KEY={secret_key}")
```

### 3. Production Environment Example

```bash
# Django Settings
DJANGO_SECRET_KEY=mK9#vL2$nR8@pQ4&wE7*tY1!uI6%oP3^sA5+dF0-gH2=jC8~xZ9
DEBUG=False
DJANGO_ALLOWED_HOSTS=mochacafe.restaurant.com,www.mochacafe.restaurant.com,192.168.1.100

# Database Settings
DB_NAME=mochacafe_prod
DB_USER=mochacafe_app
DB_PASSWORD=SecureDbPass2024!@#
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=SecureRedisPass2024!@#
```

## 🗄️ Database Setup

### 1. Install PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### CentOS/RHEL
```bash
sudo dnf install postgresql postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE mochacafe_prod;

# Create user
CREATE USER mochacafe_app WITH PASSWORD 'SecureDbPass2024!@#';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE mochacafe_prod TO mochacafe_app;
ALTER USER mochacafe_app CREATEDB;

# Exit PostgreSQL
\q
```

### 3. Configure PostgreSQL Authentication

Edit `/etc/postgresql/*/main/pg_hba.conf`:
```bash
# Add this line for local connections
local   mochacafe_prod    mochacafe_app                     md5
host    mochacafe_prod    mochacafe_app    127.0.0.1/32     md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## 🔴 Redis Setup

### 1. Install Redis

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### CentOS/RHEL
```bash
sudo dnf install redis
sudo systemctl start redis
sudo systemctl enable redis
```

### 2. Configure Redis Security

Edit `/etc/redis/redis.conf`:
```bash
# Bind to localhost only
bind 127.0.0.1

# Enable password authentication
requirepass SecureRedisPass2024!@#

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
```

Restart Redis:
```bash
sudo systemctl restart redis
```

### 3. Test Redis Connection

```bash
redis-cli -a SecureRedisPass2024!@#
127.0.0.1:6379> ping
PONG
127.0.0.1:6379> exit
```

## 🐍 Python Environment Setup

### 1. Install Python and Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-dev
sudo apt install build-essential libpq-dev
```

#### CentOS/RHEL
```bash
sudo dnf install python3 python3-pip python3-devel
sudo dnf install gcc postgresql-devel
```

### 2. Create Virtual Environment

```bash
# Create application directory
sudo mkdir -p /opt/mochacafe
sudo chown $USER:$USER /opt/mochacafe
cd /opt/mochacafe

# Clone repository
git clone https://github.com/your-username/MochaCafe.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install Additional Production Dependencies

```bash
# Install Gunicorn for production WSGI server
pip install gunicorn

# Install process monitoring
pip install supervisor
```

## 🔒 Security Configuration

### 1. File Permissions

```bash
# Set proper ownership
sudo chown -R www-data:www-data /opt/mochacafe
sudo chmod -R 755 /opt/mochacafe

# Protect sensitive files
sudo chmod 600 /opt/mochacafe/.env
sudo chmod 600 /opt/mochacafe/logs/*.log
```

### 2. Firewall Configuration

```bash
# Install UFW
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable
```

### 3. SSL Certificate Setup

#### Using Let's Encrypt (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

## 🧪 Environment Validation

### 1. Test Database Connection

```bash
cd /opt/mochacafe
source venv/bin/activate
python manage.py dbshell
```

### 2. Test Redis Connection

```bash
python manage.py shell
>>> import redis
>>> r = redis.Redis(host='localhost', port=6379, password='your-redis-password')
>>> r.ping()
True
```

### 3. Run Django Checks

```bash
python manage.py check --deploy
python manage.py migrate --check
python manage.py collectstatic --dry-run
```

## 📊 Environment Monitoring

### 1. System Resource Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Check system resources
htop
df -h
free -h
```

### 2. Application Monitoring

```bash
# Check Django logs
tail -f /opt/mochacafe/logs/django.log

# Check database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='mochacafe_prod';"

# Check Redis memory usage
redis-cli -a your-password info memory
```

## 🔄 Environment Updates

### 1. Update Environment Variables

```bash
# Backup current environment
cp .env .env.backup.$(date +%Y%m%d)

# Update variables
nano .env

# Restart services after changes
sudo systemctl restart mochacafe-web
sudo systemctl restart nginx
```

### 2. Rotate Secrets

```bash
# Generate new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Update database password
sudo -u postgres psql -c "ALTER USER mochacafe_app PASSWORD 'NewSecurePassword2024';"

# Update Redis password
# Edit /etc/redis/redis.conf and restart Redis
```

## ⚠️ Common Environment Issues

### Issue: Database Connection Refused
**Solution**: Check PostgreSQL service and authentication settings
```bash
sudo systemctl status postgresql
sudo -u postgres psql -c "SELECT version();"
```

### Issue: Redis Connection Timeout
**Solution**: Verify Redis is running and accessible
```bash
sudo systemctl status redis
redis-cli ping
```

### Issue: Permission Denied Errors
**Solution**: Check file ownership and permissions
```bash
ls -la /opt/mochacafe/
sudo chown -R www-data:www-data /opt/mochacafe/
```

### Issue: SSL Certificate Errors
**Solution**: Verify certificate validity and renewal
```bash
sudo certbot certificates
sudo nginx -t
```

---

**Next Steps**: After completing environment setup, proceed to [Manual Deployment](manual-deployment.md) or [Docker Deployment](docker-deployment.md).