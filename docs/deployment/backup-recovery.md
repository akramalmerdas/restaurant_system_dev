# Backup & Recovery Guide

This guide covers comprehensive backup strategies and recovery procedures for MochaCafe.

## 📋 Backup Strategy Overview

### What to Backup
1. **Database** - All restaurant data (orders, customers, inventory)
2. **Media Files** - Uploaded images, logos, documents
3. **Configuration Files** - Environment variables, settings
4. **Application Code** - Custom modifications (if any)
5. **SSL Certificates** - Let's Encrypt certificates
6. **System Configuration** - Nginx, systemd service files

### Backup Schedule
- **Hourly**: Database incremental backups (during business hours)
- **Daily**: Full database backup + media files
- **Weekly**: Complete system backup
- **Monthly**: Archive backup (long-term storage)

## 🗄️ Database Backup & Recovery

### Automated Daily Database Backup

#### Create Backup Script
```bash
sudo tee /opt/mochacafe/scripts/db_backup.sh << 'EOF'
#!/bin/bash

# Configuration
BACKUP_DIR="/opt/mochacafe/backups/database"
DB_NAME="mochacafe_prod"
DB_USER="mochacafe_app"
DB_HOST="localhost"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mochacafe_backup_$TIMESTAMP.sql"
COMPRESSED_FILE="$BACKUP_FILE.gz"

# Create database backup
echo "Starting database backup at $(date)"
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    # Compress the backup
    gzip $BACKUP_FILE
    echo "Database backup completed: $COMPRESSED_FILE"
    
    # Remove old backups
    find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "Old backups cleaned up (older than $RETENTION_DAYS days)"
    
    # Log backup size
    BACKUP_SIZE=$(du -h $COMPRESSED_FILE | cut -f1)
    echo "Backup size: $BACKUP_SIZE"
    
else
    echo "ERROR: Database backup failed!"
    exit 1
fi
EOF

sudo chmod +x /opt/mochacafe/scripts/db_backup.sh
sudo chown mochacafe:mochacafe /opt/mochacafe/scripts/db_backup.sh
```

#### Set Up Automated Backups
```bash
# Create backup directories
sudo -u mochacafe mkdir -p /opt/mochacafe/backups/{database,media,system}
sudo -u mochacafe mkdir -p /opt/mochacafe/scripts

# Add to crontab for automated execution
sudo -u mochacafe crontab -e

# Add these lines:
# Database backup every 6 hours during business hours (6 AM to 10 PM)
0 6,12,18,22 * * * /opt/mochacafe/scripts/db_backup.sh >> /opt/mochacafe/logs/backup.log 2>&1

# Full backup daily at 2 AM
0 2 * * * /opt/mochacafe/scripts/full_backup.sh >> /opt/mochacafe/logs/backup.log 2>&1
```

### Manual Database Backup

#### Create Backup
```bash
# Simple backup
pg_dump -h localhost -U mochacafe_app mochacafe_prod > backup_$(date +%Y%m%d).sql

# Compressed backup
pg_dump -h localhost -U mochacafe_app mochacafe_prod | gzip > backup_$(date +%Y%m%d).sql.gz

# Custom format backup (recommended for large databases)
pg_dump -h localhost -U mochacafe_app -Fc mochacafe_prod > backup_$(date +%Y%m%d).dump
```

#### Backup Specific Tables
```bash
# Backup only orders and customers
pg_dump -h localhost -U mochacafe_app -t orders_order -t users_customer mochacafe_prod > critical_data_backup.sql

# Backup schema only (no data)
pg_dump -h localhost -U mochacafe_app --schema-only mochacafe_prod > schema_backup.sql

# Backup data only (no schema)
pg_dump -h localhost -U mochacafe_app --data-only mochacafe_prod > data_backup.sql
```

### Database Recovery

#### Full Database Restore
```bash
# Stop the application first
sudo systemctl stop mochacafe-web mochacafe-worker

# Method 1: From SQL dump
psql -h localhost -U mochacafe_app -d mochacafe_prod < backup_20241216.sql

# Method 2: From compressed SQL dump
gunzip -c backup_20241216.sql.gz | psql -h localhost -U mochacafe_app -d mochacafe_prod

# Method 3: From custom format dump
pg_restore -h localhost -U mochacafe_app -d mochacafe_prod backup_20241216.dump

# Start the application
sudo systemctl start mochacafe-web mochacafe-worker
```

#### Create New Database from Backup
```bash
# Create new database
sudo -u postgres createdb mochacafe_restored

# Grant permissions
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mochacafe_restored TO mochacafe_app;"

# Restore data
psql -h localhost -U mochacafe_app -d mochacafe_restored < backup_20241216.sql
```

#### Point-in-Time Recovery
```bash
# If you have continuous archiving enabled
pg_restore -h localhost -U mochacafe_app -d mochacafe_prod --clean --if-exists backup_20241216.dump
```

## 📁 Media Files Backup

### Create Media Backup Script
```bash
sudo tee /opt/mochacafe/scripts/media_backup.sh << 'EOF'
#!/bin/bash

# Configuration
MEDIA_DIR="/opt/mochacafe/media"
BACKUP_DIR="/opt/mochacafe/backups/media"
RETENTION_DAYS=60

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate backup filename
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/media_backup_$TIMESTAMP.tar.gz"

# Create media backup
echo "Starting media backup at $(date)"
tar -czf $BACKUP_FILE -C /opt/mochacafe media/

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Media backup completed: $BACKUP_FILE"
    
    # Remove old backups
    find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
    echo "Old media backups cleaned up"
    
    # Log backup size
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "Media backup size: $BACKUP_SIZE"
else
    echo "ERROR: Media backup failed!"
    exit 1
fi
EOF

sudo chmod +x /opt/mochacafe/scripts/media_backup.sh
sudo chown mochacafe:mochacafe /opt/mochacafe/scripts/media_backup.sh
```

### Media Recovery
```bash
# Stop application
sudo systemctl stop mochacafe-web

# Backup current media (just in case)
mv /opt/mochacafe/media /opt/mochacafe/media_old_$(date +%Y%m%d)

# Restore media from backup
cd /opt/mochacafe
tar -xzf backups/media/media_backup_20241216_020000.tar.gz

# Fix permissions
sudo chown -R mochacafe:www-data /opt/mochacafe/media
sudo chmod -R 755 /opt/mochacafe/media

# Start application
sudo systemctl start mochacafe-web
```

## 🔧 System Configuration Backup

### Create System Backup Script
```bash
sudo tee /opt/mochacafe/scripts/system_backup.sh << 'EOF'
#!/bin/bash

# Configuration
BACKUP_DIR="/opt/mochacafe/backups/system"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/system_backup_$TIMESTAMP.tar.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting system configuration backup at $(date)"

# Create temporary directory for system files
TEMP_DIR="/tmp/mochacafe_system_backup_$$"
mkdir -p $TEMP_DIR

# Copy important system files
mkdir -p $TEMP_DIR/nginx
cp /etc/nginx/sites-available/mochacafe $TEMP_DIR/nginx/

mkdir -p $TEMP_DIR/systemd
cp /etc/systemd/system/mochacafe-*.service $TEMP_DIR/systemd/
cp /etc/systemd/system/mochacafe-*.socket $TEMP_DIR/systemd/ 2>/dev/null || true

mkdir -p $TEMP_DIR/ssl
cp -r /etc/letsencrypt/live/*/  $TEMP_DIR/ssl/ 2>/dev/null || true

mkdir -p $TEMP_DIR/application
cp /opt/mochacafe/.env $TEMP_DIR/application/
cp /opt/mochacafe/config/gunicorn.conf.py $TEMP_DIR/application/

# Create backup archive
tar -czf $BACKUP_FILE -C $TEMP_DIR .

# Cleanup
rm -rf $TEMP_DIR

if [ $? -eq 0 ]; then
    echo "System backup completed: $BACKUP_FILE"
    
    # Remove old backups (keep 10 most recent)
    ls -t $BACKUP_DIR/system_backup_*.tar.gz | tail -n +11 | xargs rm -f
    
    BACKUP_SIZE=$(du -h $BACKUP_FILE | cut -f1)
    echo "System backup size: $BACKUP_SIZE"
else
    echo "ERROR: System backup failed!"
    exit 1
fi
EOF

sudo chmod +x /opt/mochacafe/scripts/system_backup.sh
```

## 🔄 Complete Backup Solution

### Create Full Backup Script
```bash
sudo tee /opt/mochacafe/scripts/full_backup.sh << 'EOF'
#!/bin/bash

# Configuration
BACKUP_BASE="/opt/mochacafe/backups"
LOG_FILE="/opt/mochacafe/logs/backup.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log_message "Starting full backup process"

# Run database backup
log_message "Running database backup..."
/opt/mochacafe/scripts/db_backup.sh
if [ $? -ne 0 ]; then
    log_message "ERROR: Database backup failed"
    exit 1
fi

# Run media backup
log_message "Running media backup..."
/opt/mochacafe/scripts/media_backup.sh
if [ $? -ne 0 ]; then
    log_message "ERROR: Media backup failed"
    exit 1
fi

# Run system backup
log_message "Running system backup..."
/opt/mochacafe/scripts/system_backup.sh
if [ $? -ne 0 ]; then
    log_message "ERROR: System backup failed"
    exit 1
fi

# Create backup summary
SUMMARY_FILE="$BACKUP_BASE/backup_summary_$TIMESTAMP.txt"
cat > $SUMMARY_FILE << EOL
MochaCafe Backup Summary
Date: $(date)
Timestamp: $TIMESTAMP

Database Backup:
$(ls -lh $BACKUP_BASE/database/mochacafe_backup_*$TIMESTAMP*.sql.gz 2>/dev/null || echo "Not found")

Media Backup:
$(ls -lh $BACKUP_BASE/media/media_backup_*$TIMESTAMP*.tar.gz 2>/dev/null || echo "Not found")

System Backup:
$(ls -lh $BACKUP_BASE/system/system_backup_*$TIMESTAMP*.tar.gz 2>/dev/null || echo "Not found")

Total Backup Size:
$(du -sh $BACKUP_BASE | cut -f1)
EOL

log_message "Full backup completed successfully"
log_message "Backup summary: $SUMMARY_FILE"
EOF

sudo chmod +x /opt/mochacafe/scripts/full_backup.sh
sudo chown mochacafe:mochacafe /opt/mochacafe/scripts/full_backup.sh
```

## 🌐 Remote Backup Storage

### Set Up Remote Backup with rsync

#### Create Remote Backup Script
```bash
sudo tee /opt/mochacafe/scripts/remote_backup.sh << 'EOF'
#!/bin/bash

# Configuration
LOCAL_BACKUP_DIR="/opt/mochacafe/backups"
REMOTE_USER="backup_user"
REMOTE_HOST="backup.example.com"
REMOTE_DIR="/backups/mochacafe"
SSH_KEY="/opt/mochacafe/.ssh/backup_key"

# Log function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a /opt/mochacafe/logs/remote_backup.log
}

log_message "Starting remote backup sync"

# Sync to remote server
rsync -avz --delete \
    -e "ssh -i $SSH_KEY" \
    $LOCAL_BACKUP_DIR/ \
    $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/

if [ $? -eq 0 ]; then
    log_message "Remote backup sync completed successfully"
else
    log_message "ERROR: Remote backup sync failed"
    exit 1
fi
EOF

sudo chmod +x /opt/mochacafe/scripts/remote_backup.sh
```

### Cloud Storage Integration

#### AWS S3 Backup
```bash
# Install AWS CLI
sudo apt install awscli

# Configure AWS credentials
sudo -u mochacafe aws configure

# Create S3 backup script
sudo tee /opt/mochacafe/scripts/s3_backup.sh << 'EOF'
#!/bin/bash

BUCKET_NAME="mochacafe-backups"
LOCAL_BACKUP_DIR="/opt/mochacafe/backups"
S3_PREFIX="$(hostname)/$(date +%Y/%m)"

# Sync to S3
aws s3 sync $LOCAL_BACKUP_DIR s3://$BUCKET_NAME/$S3_PREFIX/ \
    --storage-class STANDARD_IA \
    --exclude "*.tmp"

echo "Backup synced to S3: s3://$BUCKET_NAME/$S3_PREFIX/"
EOF
```

## 🚨 Disaster Recovery Procedures

### Complete System Recovery

#### Scenario: Server Completely Lost
```bash
# 1. Set up new server with same OS
# 2. Install basic dependencies
sudo apt update && sudo apt install -y postgresql redis-server nginx python3 python3-pip

# 3. Restore system configuration
tar -xzf system_backup_20241216_020000.tar.gz -C /

# 4. Create application user and directories
sudo useradd --system --shell /bin/bash --home /opt/mochacafe mochacafe
sudo mkdir -p /opt/mochacafe
sudo chown mochacafe:mochacafe /opt/mochacafe

# 5. Clone application code
sudo -u mochacafe git clone https://github.com/your-username/MochaCafe.git /opt/mochacafe

# 6. Set up Python environment
sudo -u mochacafe python3 -m venv /opt/mochacafe/venv
sudo -u mochacafe /opt/mochacafe/venv/bin/pip install -r /opt/mochacafe/requirements.txt

# 7. Restore database
sudo -u postgres createdb mochacafe_prod
sudo -u postgres psql -c "CREATE USER mochacafe_app WITH PASSWORD 'your-password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mochacafe_prod TO mochacafe_app;"
gunzip -c mochacafe_backup_20241216_020000.sql.gz | sudo -u mochacafe psql -h localhost -U mochacafe_app -d mochacafe_prod

# 8. Restore media files
sudo -u mochacafe tar -xzf media_backup_20241216_020000.tar.gz -C /opt/mochacafe/

# 9. Start services
sudo systemctl daemon-reload
sudo systemctl enable --now mochacafe-web nginx postgresql redis
```

### Database Corruption Recovery
```bash
# 1. Stop application
sudo systemctl stop mochacafe-web mochacafe-worker

# 2. Attempt database repair
sudo -u postgres psql -d mochacafe_prod -c "REINDEX DATABASE mochacafe_prod;"

# 3. If repair fails, restore from backup
sudo -u postgres dropdb mochacafe_prod
sudo -u postgres createdb mochacafe_prod
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mochacafe_prod TO mochacafe_app;"
gunzip -c /opt/mochacafe/backups/database/mochacafe_backup_latest.sql.gz | psql -h localhost -U mochacafe_app -d mochacafe_prod

# 4. Start application
sudo systemctl start mochacafe-web mochacafe-worker
```

## 📊 Backup Monitoring & Verification

### Create Backup Verification Script
```bash
sudo tee /opt/mochacafe/scripts/verify_backups.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/mochacafe/backups"
LOG_FILE="/opt/mochacafe/logs/backup_verification.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

log_message "Starting backup verification"

# Check if recent backups exist
YESTERDAY=$(date -d "yesterday" +%Y%m%d)

# Check database backup
DB_BACKUP=$(find $BACKUP_DIR/database -name "*$YESTERDAY*.sql.gz" | head -1)
if [ -n "$DB_BACKUP" ]; then
    # Test if backup can be read
    if gunzip -t "$DB_BACKUP" 2>/dev/null; then
        log_message "Database backup verification: PASSED ($DB_BACKUP)"
    else
        log_message "Database backup verification: FAILED - Corrupted file ($DB_BACKUP)"
    fi
else
    log_message "Database backup verification: FAILED - No recent backup found"
fi

# Check media backup
MEDIA_BACKUP=$(find $BACKUP_DIR/media -name "*$YESTERDAY*.tar.gz" | head -1)
if [ -n "$MEDIA_BACKUP" ]; then
    if tar -tzf "$MEDIA_BACKUP" >/dev/null 2>&1; then
        log_message "Media backup verification: PASSED ($MEDIA_BACKUP)"
    else
        log_message "Media backup verification: FAILED - Corrupted file ($MEDIA_BACKUP)"
    fi
else
    log_message "Media backup verification: FAILED - No recent backup found"
fi

log_message "Backup verification completed"
EOF

sudo chmod +x /opt/mochacafe/scripts/verify_backups.sh

# Add to crontab to run daily
sudo -u mochacafe crontab -e
# Add: 0 8 * * * /opt/mochacafe/scripts/verify_backups.sh
```

### Backup Size Monitoring
```bash
# Create backup size monitoring
sudo tee /opt/mochacafe/scripts/backup_size_monitor.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/mochacafe/backups"
MAX_SIZE_GB=50  # Alert if backups exceed 50GB

CURRENT_SIZE=$(du -s $BACKUP_DIR | cut -f1)
CURRENT_SIZE_GB=$((CURRENT_SIZE / 1024 / 1024))

if [ $CURRENT_SIZE_GB -gt $MAX_SIZE_GB ]; then
    echo "WARNING: Backup directory size ($CURRENT_SIZE_GB GB) exceeds threshold ($MAX_SIZE_GB GB)"
    # Here you could send an email or notification
fi

echo "Current backup size: $CURRENT_SIZE_GB GB"
EOF
```

## 📋 Backup Checklist

### Daily Checklist
- [ ] Database backup completed successfully
- [ ] Media files backup completed
- [ ] Backup logs reviewed for errors
- [ ] Backup sizes are reasonable
- [ ] Remote sync completed (if configured)

### Weekly Checklist
- [ ] Full system backup completed
- [ ] Backup verification tests passed
- [ ] Old backups cleaned up properly
- [ ] Backup storage space sufficient
- [ ] Recovery procedures tested

### Monthly Checklist
- [ ] Complete disaster recovery test
- [ ] Backup retention policy reviewed
- [ ] Remote backup storage verified
- [ ] Backup documentation updated
- [ ] Recovery time objectives met

---

**Remember**: Backups are only as good as your ability to restore from them. Regularly test your recovery procedures to ensure they work when needed.