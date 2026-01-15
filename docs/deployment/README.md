# MochaCafe Deployment Guide

This guide provides comprehensive instructions for deploying MochaCafe restaurant management system in production environments.

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Deployment Options](#deployment-options)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Security Considerations](#security-considerations)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)

## 🖥️ System Requirements

### Minimum Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 20GB SSD
- **Network**: Stable internet connection

### Recommended Requirements
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **Network**: 100Mbps+ connection

### Software Dependencies
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Redis**: 6+
- **Nginx**: 1.18+
- **SSL Certificate**: Let's Encrypt or commercial

## 🚀 Deployment Options

Choose the deployment method that best fits your needs:

### Option 1: Docker Deployment (Recommended)
- **Pros**: Easy setup, consistent environment, automatic scaling
- **Best for**: Cloud deployments, development teams
- **Guide**: [Docker Deployment](docker-deployment.md)

### Option 2: Manual Server Setup
- **Pros**: Full control, custom configurations
- **Best for**: Dedicated servers, specific requirements
- **Guide**: [Manual Deployment](manual-deployment.md)

### Option 3: Cloud Platform Deployment
- **Pros**: Managed services, automatic backups
- **Best for**: High availability, enterprise use
- **Platforms**: AWS, DigitalOcean, Heroku

## ⚡ Quick Start

### For Docker (5 minutes)
```bash
# Clone the repository
git clone https://github.com/your-username/MochaCafe.git
cd MochaCafe

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access application
# http://your-domain.com
```

### For Manual Setup (30 minutes)
See [Manual Deployment Guide](manual-deployment.md) for detailed instructions.

## 🔧 Environment Setup

### Required Environment Variables
```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database Settings
DB_NAME=mochacafe_prod
DB_USER=mochacafe_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_password_here
```

See [Environment Setup Guide](environment-setup.md) for complete configuration.

## 🔒 Security Considerations

### Essential Security Steps
1. **Change default passwords** for database and Redis
2. **Use strong SECRET_KEY** (50+ random characters)
3. **Enable SSL/HTTPS** with valid certificates
4. **Configure firewall** to allow only necessary ports
5. **Regular security updates** for OS and dependencies
6. **Database backups** with encryption
7. **Monitor logs** for suspicious activity

### Recommended Security Tools
- **Fail2ban**: Protection against brute force attacks
- **UFW/iptables**: Firewall configuration
- **Certbot**: Automatic SSL certificate management
- **Logwatch**: Log monitoring and alerts

## 🔄 Maintenance

### Regular Tasks
- **Daily**: Monitor system resources and logs
- **Weekly**: Check for security updates
- **Monthly**: Database maintenance and optimization
- **Quarterly**: Full system backup verification

### Update Procedures
```bash
# Backup database
pg_dump mochacafe_prod > backup_$(date +%Y%m%d).sql

# Update application
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Restart services
sudo systemctl restart mochacafe-web
sudo systemctl restart nginx
```

## 🆘 Troubleshooting

### Common Issues

#### Application Won't Start
1. Check environment variables in `.env`
2. Verify database connection
3. Check Redis connectivity
4. Review application logs

#### Database Connection Errors
1. Verify PostgreSQL is running
2. Check database credentials
3. Ensure database exists
4. Check network connectivity

#### Static Files Not Loading
1. Run `python manage.py collectstatic`
2. Check Nginx configuration
3. Verify file permissions
4. Check STATIC_ROOT setting

### Log Locations
- **Application logs**: `/var/log/mochacafe/`
- **Nginx logs**: `/var/log/nginx/`
- **PostgreSQL logs**: `/var/log/postgresql/`
- **System logs**: `journalctl -u mochacafe-web`

### Getting Help
- **Documentation**: Check other guides in this folder
- **Logs**: Always include relevant log excerpts
- **System Info**: Provide OS version, Python version, etc.
- **Error Messages**: Include complete error messages

## 📚 Additional Resources

- [Environment Setup](environment-setup.md) - Detailed environment configuration
- [Docker Deployment](docker-deployment.md) - Container-based deployment
- [Manual Deployment](manual-deployment.md) - Traditional server setup
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
- [Backup & Recovery](backup-recovery.md) - Data protection procedures

## 📞 Support

For deployment assistance:
1. Check the troubleshooting guide
2. Review application logs
3. Consult the relevant deployment guide
4. Contact system administrator

---

**Note**: This is a production system handling sensitive restaurant data. Always follow security best practices and test deployments in a staging environment first.