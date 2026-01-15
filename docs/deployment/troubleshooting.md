# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with MochaCafe deployment and operation.

## 🚨 Emergency Quick Fixes

### Application is Down
```bash
# Check all services
sudo systemctl status mochacafe-web nginx postgresql redis

# Restart all services
sudo systemctl restart mochacafe-web mochacafe-worker nginx

# Check logs immediately
sudo journalctl -u mochacafe-web --no-pager -n 50
```

### Database Connection Lost
```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Test connection
sudo -u mochacafe psql -h localhost -U mochacafe_app -d mochacafe_prod -c "SELECT 1;"
```

### High CPU/Memory Usage
```bash
# Check resource usage
htop
free -h
df -h

# Restart application
sudo systemctl restart mochacafe-web
```

## 🔍 Diagnostic Commands

### System Health Check
```bash
#!/bin/bash
echo "=== MochaCafe System Health Check ==="
echo "Date: $(date)"
echo

echo "=== Service Status ==="
systemctl is-active mochacafe-web nginx postgresql redis

echo "=== Disk Usage ==="
df -h /

echo "=== Memory Usage ==="
free -h

echo "=== Load Average ==="
uptime

echo "=== Recent Errors ==="
journalctl -u mochacafe-web --since "1 hour ago" --no-pager | grep -i error | tail -5
```

### Application Status
```bash
# Check if application is responding
curl -I https://your-domain.com/health/

# Check database connectivity
sudo -u mochacafe python3 /opt/mochacafe/manage.py dbshell -c "SELECT version();"

# Check Redis connectivity
redis-cli -a your-redis-password ping
```

## 🐛 Common Issues & Solutions

### 1. Application Won't Start

#### Symptoms
- HTTP 502 Bad Gateway
- Service fails to start
- Connection refused errors

#### Diagnosis
```bash
# Check service status
sudo systemctl status mochacafe-web

# Check detailed logs
sudo journalctl -u mochacafe-web --no-pager -n 100

# Check if socket exists
ls -la /run/mochacafe/

# Test Gunicorn manually
sudo -u mochacafe /opt/mochacafe/venv/bin/gunicorn --bind 127.0.0.1:8001 MochaCafe.wsgi:application
```

#### Solutions
```bash
# Fix permissions
sudo chown -R mochacafe:mochacafe /opt/mochacafe
sudo chmod 600 /opt/mochacafe/.env

# Recreate socket directory
sudo mkdir -p /run/mochacafe
sudo chown mochacafe:mochacafe /run/mochacafe

# Restart services
sudo systemctl daemon-reload
sudo systemctl restart mochacafe-web.socket
sudo systemctl restart mochacafe-web.service
```

### 2. Database Connection Issues

#### Symptoms
- "Connection refused" errors
- "Authentication failed" errors
- Slow database queries

#### Diagnosis
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='mochacafe_prod';"

# Test authentication
sudo -u mochacafe psql -h localhost -U mochacafe_app -d mochacafe_prod -c "SELECT 1;"

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

#### Solutions
```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Check pg_hba.conf authentication
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Ensure this line exists:
# local   mochacafe_prod    mochacafe_app                     md5

# Reload PostgreSQL configuration
sudo systemctl reload postgresql

# Reset database password
sudo -u postgres psql -c "ALTER USER mochacafe_app PASSWORD 'new-password';"
```

### 3. Redis Connection Problems

#### Symptoms
- Real-time features not working
- WebSocket connection failures
- Redis connection timeouts

#### Diagnosis
```bash
# Check Redis status
sudo systemctl status redis

# Test Redis connection
redis-cli ping
redis-cli -a your-password ping

# Check Redis logs
sudo journalctl -u redis --no-pager -n 50

# Check Redis memory usage
redis-cli info memory
```

#### Solutions
```bash
# Restart Redis
sudo systemctl restart redis

# Check Redis configuration
sudo nano /etc/redis/redis.conf

# Test without password (if auth disabled)
redis-cli ping

# Clear Redis cache if corrupted
redis-cli -a your-password FLUSHALL
```

### 4. SSL Certificate Issues

#### Symptoms
- "Certificate expired" warnings
- "Insecure connection" errors
- HTTPS not working

#### Diagnosis
```bash
# Check certificate status
sudo certbot certificates

# Test SSL configuration
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Check Nginx SSL configuration
sudo nginx -t

# Check certificate files
ls -la /etc/letsencrypt/live/your-domain.com/
```

#### Solutions
```bash
# Renew certificates
sudo certbot renew

# Force certificate renewal
sudo certbot renew --force-renewal

# Restart Nginx after renewal
sudo systemctl restart nginx

# Check auto-renewal cron job
sudo crontab -l | grep certbot
```

### 5. Static Files Not Loading

#### Symptoms
- CSS/JS files return 404
- Images not displaying
- Styling broken

#### Diagnosis
```bash
# Check static files directory
ls -la /opt/mochacafe/collected_static/

# Check Nginx configuration
sudo nginx -t

# Check file permissions
ls -la /opt/mochacafe/collected_static/css/

# Test static file URL
curl -I https://your-domain.com/static/css/style.css
```

#### Solutions
```bash
# Collect static files
sudo -u mochacafe /opt/mochacafe/venv/bin/python /opt/mochacafe/manage.py collectstatic --noinput

# Fix permissions
sudo chown -R mochacafe:www-data /opt/mochacafe/collected_static/
sudo chmod -R 755 /opt/mochacafe/collected_static/

# Restart Nginx
sudo systemctl restart nginx
```

### 6. High Memory Usage

#### Symptoms
- Server running out of memory
- Application becomes slow
- OOM (Out of Memory) errors

#### Diagnosis
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Check swap usage
swapon --show

# Monitor memory in real-time
watch -n 1 free -h
```

#### Solutions
```bash
# Restart application to free memory
sudo systemctl restart mochacafe-web

# Add swap space (if none exists)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Optimize Gunicorn workers
sudo nano /opt/mochacafe/config/gunicorn.conf.py
# Reduce workers if memory is limited
# workers = 2  # Instead of CPU * 2 + 1
```

### 7. Slow Performance

#### Symptoms
- Pages load slowly
- Database queries timeout
- High CPU usage

#### Diagnosis
```bash
# Check system load
uptime
htop

# Check database performance
sudo -u postgres psql -d mochacafe_prod -c "SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"

# Check Nginx access logs for slow requests
sudo tail -f /var/log/nginx/access.log | grep -E "HTTP/[0-9.]+ [45][0-9][0-9]"

# Monitor network usage
nethogs
```

#### Solutions
```bash
# Optimize database
sudo -u postgres psql -d mochacafe_prod -c "VACUUM ANALYZE;"

# Restart services
sudo systemctl restart mochacafe-web nginx

# Check for long-running processes
ps aux | grep python

# Optimize Nginx caching
# Add to Nginx config:
# location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
#     expires 1y;
#     add_header Cache-Control "public, immutable";
# }
```

### 8. Printing System Issues

#### Symptoms
- Orders not printing automatically
- Print service not running
- Printer connection errors

#### Diagnosis
```bash
# Check worker service
sudo systemctl status mochacafe-worker

# Check worker logs
sudo journalctl -u mochacafe-worker --no-pager -n 50

# Test printer connection
# (This depends on your printer setup)
lpstat -p
```

#### Solutions
```bash
# Restart worker service
sudo systemctl restart mochacafe-worker

# Check printer configuration
# Ensure printer is properly configured in the system

# Test print script manually
sudo -u mochacafe /opt/mochacafe/venv/bin/python /opt/mochacafe/print_orders.py
```

## 📊 Monitoring & Alerting

### Set Up Basic Monitoring

#### Create Health Check Script
```bash
sudo tee /opt/mochacafe/health_check.sh << 'EOF'
#!/bin/bash
LOGFILE="/opt/mochacafe/logs/health_check.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check web service
if ! systemctl is-active --quiet mochacafe-web; then
    echo "$DATE - ERROR: mochacafe-web service is down" >> $LOGFILE
    systemctl restart mochacafe-web
fi

# Check database
if ! sudo -u mochacafe psql -h localhost -U mochacafe_app -d mochacafe_prod -c "SELECT 1;" > /dev/null 2>&1; then
    echo "$DATE - ERROR: Database connection failed" >> $LOGFILE
fi

# Check Redis
if ! redis-cli -a your-password ping > /dev/null 2>&1; then
    echo "$DATE - ERROR: Redis connection failed" >> $LOGFILE
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "$DATE - WARNING: Disk usage is ${DISK_USAGE}%" >> $LOGFILE
fi

echo "$DATE - Health check completed" >> $LOGFILE
EOF

sudo chmod +x /opt/mochacafe/health_check.sh
```

#### Add to Crontab
```bash
sudo crontab -e
# Add this line to run health check every 5 minutes:
*/5 * * * * /opt/mochacafe/health_check.sh
```

### Log Analysis Commands

#### Find Recent Errors
```bash
# Application errors
sudo journalctl -u mochacafe-web --since "1 hour ago" | grep -i error

# Nginx errors
sudo grep -i error /var/log/nginx/error.log | tail -10

# Database errors
sudo grep -i error /var/log/postgresql/postgresql-*-main.log | tail -10
```

#### Monitor Resource Usage
```bash
# Real-time monitoring
watch -n 1 'free -h && echo && df -h / && echo && uptime'

# Process monitoring
watch -n 1 'ps aux --sort=-%cpu | head -10'
```

## 🆘 Emergency Procedures

### Complete System Recovery

#### If Everything is Down
```bash
# 1. Check system resources
df -h
free -h
uptime

# 2. Restart all services
sudo systemctl restart postgresql redis nginx
sudo systemctl restart mochacafe-web mochacafe-worker

# 3. Check logs
sudo journalctl --since "10 minutes ago" | grep -i error

# 4. Test application
curl -I https://your-domain.com/health/
```

#### Database Recovery
```bash
# 1. Stop application
sudo systemctl stop mochacafe-web

# 2. Backup current database
pg_dump -h localhost -U mochacafe_app mochacafe_prod > emergency_backup.sql

# 3. Restore from backup (if needed)
# dropdb -h localhost -U mochacafe_app mochacafe_prod
# createdb -h localhost -U mochacafe_app mochacafe_prod
# psql -h localhost -U mochacafe_app -d mochacafe_prod < backup_file.sql

# 4. Start application
sudo systemctl start mochacafe-web
```

### Contact Information Template

Create `/opt/mochacafe/EMERGENCY_CONTACTS.txt`:
```
EMERGENCY CONTACTS FOR MOCHACAFE SYSTEM

System Administrator: [Name] - [Phone] - [Email]
Database Administrator: [Name] - [Phone] - [Email]
Hosting Provider Support: [Phone] - [Email]
Domain Registrar Support: [Phone] - [Email]

CRITICAL INFORMATION:
- Server IP: [IP Address]
- Domain: [Domain Name]
- Database Host: [Host]
- Backup Location: [Location]

QUICK COMMANDS:
- Restart all: sudo systemctl restart mochacafe-web nginx postgresql redis
- Check logs: sudo journalctl -u mochacafe-web -f
- Emergency backup: pg_dump mochacafe_prod > emergency_backup.sql
```

---

**Remember**: Always test fixes in a staging environment first when possible. Keep regular backups and document any changes made to the system.