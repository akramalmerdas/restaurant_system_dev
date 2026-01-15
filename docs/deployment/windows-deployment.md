# Windows Deployment Guide

This guide provides step-by-step instructions for deploying MochaCafe on Windows Server.

## 📋 Prerequisites

- Windows Server 2019+ or Windows 10/11 Pro
- Administrator access
- Domain name pointing to your server (optional)
- Completed [Environment Setup](environment-setup.md)

## 🚀 Step-by-Step Windows Deployment

### Step 1: Install Required Software

#### Install Python
```powershell
# Download and install Python 3.11+ from python.org
# Or use Chocolatey (if installed)
choco install python --version=3.11.0

# Verify installation
python --version
pip --version
```

#### Install PostgreSQL
```powershell
# Download from https://www.postgresql.org/download/windows/
# Or use Chocolatey
choco install postgresql --params '/Password:YourSecurePassword'

# Add PostgreSQL to PATH
$env:PATH += ";C:\Program Files\PostgreSQL\15\bin"
```

#### Install Redis
```powershell
# Download Redis for Windows from GitHub releases
# Or use Chocolatey
choco install redis-64

# Start Redis service
net start redis
```

#### Install IIS (Internet Information Services)
```powershell
# Enable IIS feature
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer, IIS-CommonHttpFeatures, IIS-HttpErrors, IIS-HttpLogging, IIS-RequestFiltering, IIS-StaticContent, IIS-DefaultDocument, IIS-DirectoryBrowsing, IIS-ASPNET45
```

### Step 2: Create Application Directory

```powershell
# Create application directory
New-Item -ItemType Directory -Path "C:\MochaCafe" -Force

# Set permissions
icacls "C:\MochaCafe" /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls "C:\MochaCafe" /grant "Users:(OI)(CI)R" /T
```

### Step 3: Deploy Application Code

```powershell
# Navigate to application directory
cd C:\MochaCafe

# Clone repository (install Git first if needed)
git clone https://github.com/your-username/MochaCafe.git .

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install waitress psycopg2-binary
```

### Step 4: Configure Environment

```powershell
# Copy environment file
Copy-Item .env.example .env

# Edit environment file with Windows paths
notepad .env
```

**Update .env for Windows**:
```bash
# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,localhost,127.0.0.1

# Database Settings
DB_NAME=mochacafe_prod
DB_USER=mochacafe_app
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Windows-specific paths
STATIC_ROOT=C:\MochaCafe\collected_static
MEDIA_ROOT=C:\MochaCafe\media
```

### Step 5: Database Setup

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE mochacafe_prod;
CREATE USER mochacafe_app WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE mochacafe_prod TO mochacafe_app;
ALTER USER mochacafe_app CREATEDB;
\q
```

### Step 6: Django Application Setup

```powershell
# Activate virtual environment
cd C:\MochaCafe
.\venv\Scripts\Activate.ps1

# Run Django setup
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py createsuperuser

# Test application
python manage.py check --deploy
```

### Step 7: Create Windows Services

#### Install NSSM (Non-Sucking Service Manager)
```powershell
# Download NSSM from https://nssm.cc/download
# Or use Chocolatey
choco install nssm

# Extract to C:\nssm (add to PATH)
$env:PATH += ";C:\nssm\win64"
```

#### Create MochaCafe Web Service
```powershell
# Create web service
nssm install "MochaCafe Web" "C:\MochaCafe\venv\Scripts\python.exe"
nssm set "MochaCafe Web" Application "C:\MochaCafe\venv\Scripts\python.exe"
nssm set "MochaCafe Web" AppParameters "-m waitress --host=127.0.0.1 --port=8000 MochaCafe.wsgi:application"
nssm set "MochaCafe Web" AppDirectory "C:\MochaCafe"
nssm set "MochaCafe Web" DisplayName "MochaCafe Web Application"
nssm set "MochaCafe Web" Description "MochaCafe Django Web Application"
nssm set "MochaCafe Web" Start SERVICE_AUTO_START

# Set environment file
nssm set "MochaCafe Web" AppEnvironmentExtra "DJANGO_SETTINGS_MODULE=MochaCafe.settings.production"

# Configure logging
nssm set "MochaCafe Web" AppStdout "C:\MochaCafe\logs\web_output.log"
nssm set "MochaCafe Web" AppStderr "C:\MochaCafe\logs\web_error.log"

# Start service
nssm start "MochaCafe Web"
```

#### Create MochaCafe Worker Service
```powershell
# Create worker service for background tasks
nssm install "MochaCafe Worker" "C:\MochaCafe\venv\Scripts\python.exe"
nssm set "MochaCafe Worker" Application "C:\MochaCafe\venv\Scripts\python.exe"
nssm set "MochaCafe Worker" AppParameters "print_orders.py"
nssm set "MochaCafe Worker" AppDirectory "C:\MochaCafe"
nssm set "MochaCafe Worker" DisplayName "MochaCafe Background Worker"
nssm set "MochaCafe Worker" Description "MochaCafe Background Processing Service"
nssm set "MochaCafe Worker" Start SERVICE_AUTO_START

# Configure logging
nssm set "MochaCafe Worker" AppStdout "C:\MochaCafe\logs\worker_output.log"
nssm set "MochaCafe Worker" AppStderr "C:\MochaCafe\logs\worker_error.log"

# Start service
nssm start "MochaCafe Worker"
```

### Step 8: Configure IIS as Reverse Proxy

#### Install URL Rewrite and ARR Modules
```powershell
# Download and install:
# - URL Rewrite Module: https://www.iis.net/downloads/microsoft/url-rewrite
# - Application Request Routing: https://www.iis.net/downloads/microsoft/application-request-routing
```

#### Create IIS Site Configuration

Create `C:\MochaCafe\iis\web.config`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <!-- Static files -->
                <rule name="Static Files" stopProcessing="true">
                    <match url="^(static|media)/(.*)" />
                    <action type="Rewrite" url="C:\MochaCafe\{R:1}\{R:2}" />
                </rule>
                
                <!-- Proxy to Django -->
                <rule name="Django Application" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://127.0.0.1:8000/{R:1}" />
                </rule>
            </rules>
        </rewrite>
        
        <!-- Security headers -->
        <httpProtocol>
            <customHeaders>
                <add name="X-Frame-Options" value="SAMEORIGIN" />
                <add name="X-Content-Type-Options" value="nosniff" />
                <add name="X-XSS-Protection" value="1; mode=block" />
            </customHeaders>
        </httpProtocol>
        
        <!-- Compression -->
        <urlCompression doStaticCompression="true" doDynamicCompression="true" />
        
        <!-- Static content caching -->
        <staticContent>
            <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="365.00:00:00" />
        </staticContent>
    </system.webServer>
</configuration>
```

#### Create IIS Site
```powershell
# Import WebAdministration module
Import-Module WebAdministration

# Create application pool
New-WebAppPool -Name "MochaCafePool"
Set-ItemProperty -Path "IIS:\AppPools\MochaCafePool" -Name processModel.identityType -Value ApplicationPoolIdentity

# Create website
New-Website -Name "MochaCafe" -Port 80 -PhysicalPath "C:\MochaCafe" -ApplicationPool "MochaCafePool"

# Configure bindings (add HTTPS if you have SSL certificate)
New-WebBinding -Name "MochaCafe" -Protocol "https" -Port 443 -SslFlags 1
```

### Step 9: SSL Certificate Setup (Optional)

#### Using Let's Encrypt with win-acme
```powershell
# Download win-acme from https://www.win-acme.com/
# Extract to C:\win-acme

# Run win-acme to get certificate
cd C:\win-acme
.\wacs.exe

# Follow prompts to:
# 1. Create certificate for your domain
# 2. Install certificate in IIS
# 3. Set up automatic renewal
```

### Step 10: Windows Firewall Configuration

```powershell
# Allow HTTP and HTTPS through firewall
New-NetFirewallRule -DisplayName "HTTP Inbound" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HTTPS Inbound" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# Allow Django application port (internal)
New-NetFirewallRule -DisplayName "Django App" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private
```

### Step 11: Verify Deployment

```powershell
# Check services status
Get-Service "MochaCafe*"

# Check IIS site
Get-Website -Name "MochaCafe"

# Test application
Invoke-WebRequest -Uri "http://localhost" -UseBasicParsing
```

## 🔧 Windows Service Management

### Service Control Commands

```powershell
# Start services
Start-Service "MochaCafe Web"
Start-Service "MochaCafe Worker"

# Stop services
Stop-Service "MochaCafe Web"
Stop-Service "MochaCafe Worker"

# Restart services
Restart-Service "MochaCafe Web"
Restart-Service "MochaCafe Worker"

# Check service status
Get-Service "MochaCafe*" | Format-Table Name, Status, StartType

# View service logs
Get-Content "C:\MochaCafe\logs\web_output.log" -Tail 50
Get-Content "C:\MochaCafe\logs\web_error.log" -Tail 50
```

### Update Service Configuration

```powershell
# Stop service before making changes
nssm stop "MochaCafe Web"

# Update service parameters
nssm set "MochaCafe Web" AppParameters "-m waitress --host=127.0.0.1 --port=8000 --threads=4 MochaCafe.wsgi:application"

# Start service
nssm start "MochaCafe Web"
```

## 📊 Windows Task Scheduler for Maintenance

### Create Backup Task

```powershell
# Create backup script directory
New-Item -ItemType Directory -Path "C:\MochaCafe\scripts" -Force
```

Create `C:\MochaCafe\scripts\backup.ps1`:
```powershell
# MochaCafe Backup Script for Windows
$BackupDir = "C:\MochaCafe\backups"
$LogFile = "C:\MochaCafe\logs\backup.log"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Create backup directory
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force
}

# Log function
function Write-Log {
    param($Message)
    $LogEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
    Add-Content -Path $LogFile -Value $LogEntry
    Write-Host $LogEntry
}

Write-Log "Starting backup process"

try {
    # Database backup
    $DbBackupFile = "$BackupDir\mochacafe_backup_$Timestamp.sql"
    & "C:\Program Files\PostgreSQL\15\bin\pg_dump.exe" -h localhost -U mochacafe_app -d mochacafe_prod -f $DbBackupFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Database backup completed: $DbBackupFile"
        
        # Compress backup
        Compress-Archive -Path $DbBackupFile -DestinationPath "$DbBackupFile.zip"
        Remove-Item $DbBackupFile
        Write-Log "Database backup compressed"
    } else {
        Write-Log "ERROR: Database backup failed"
    }
    
    # Media backup
    $MediaBackupFile = "$BackupDir\media_backup_$Timestamp.zip"
    Compress-Archive -Path "C:\MochaCafe\media" -DestinationPath $MediaBackupFile
    Write-Log "Media backup completed: $MediaBackupFile"
    
    # Cleanup old backups (keep 30 days)
    Get-ChildItem $BackupDir -Filter "*.zip" | Where-Object {$_.CreationTime -lt (Get-Date).AddDays(-30)} | Remove-Item
    Write-Log "Old backups cleaned up"
    
} catch {
    Write-Log "ERROR: Backup failed - $($_.Exception.Message)"
}

Write-Log "Backup process completed"
```

### Schedule Backup Task

```powershell
# Create scheduled task for daily backup
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File C:\MochaCafe\scripts\backup.ps1"
$Trigger = New-ScheduledTaskTrigger -Daily -At "2:00AM"
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "MochaCafe Daily Backup" -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description "Daily backup of MochaCafe database and media files"
```

## 🔄 Maintenance Commands

### Update Application

Create `C:\MochaCafe\scripts\update.ps1`:
```powershell
# MochaCafe Update Script
$LogFile = "C:\MochaCafe\logs\update.log"

function Write-Log {
    param($Message)
    $LogEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $Message"
    Add-Content -Path $LogFile -Value $LogEntry
    Write-Host $LogEntry
}

Write-Log "Starting application update"

try {
    # Stop services
    Stop-Service "MochaCafe Web" -Force
    Stop-Service "MochaCafe Worker" -Force
    Write-Log "Services stopped"
    
    # Backup current version
    $BackupDir = "C:\MochaCafe\backups\app_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item "C:\MochaCafe" -Destination $BackupDir -Recurse -Exclude @("backups", "logs", "venv")
    Write-Log "Current version backed up to: $BackupDir"
    
    # Pull latest code
    cd C:\MochaCafe
    git pull origin main
    Write-Log "Code updated from repository"
    
    # Update dependencies
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Write-Log "Dependencies updated"
    
    # Run migrations
    python manage.py migrate
    Write-Log "Database migrations completed"
    
    # Collect static files
    python manage.py collectstatic --noinput
    Write-Log "Static files collected"
    
    # Start services
    Start-Service "MochaCafe Web"
    Start-Service "MochaCafe Worker"
    Write-Log "Services started"
    
    Write-Log "Application update completed successfully"
    
} catch {
    Write-Log "ERROR: Update failed - $($_.Exception.Message)"
    
    # Attempt to start services anyway
    try {
        Start-Service "MochaCafe Web"
        Start-Service "MochaCafe Worker"
        Write-Log "Services restarted after error"
    } catch {
        Write-Log "CRITICAL: Could not restart services"
    }
}
```

## ⚠️ Windows-Specific Troubleshooting

### Common Windows Issues

#### Service Won't Start
```powershell
# Check service status
Get-Service "MochaCafe Web" | Format-List *

# Check event logs
Get-EventLog -LogName Application -Source "MochaCafe Web" -Newest 10

# Check NSSM service configuration
nssm dump "MochaCafe Web"
```

#### Permission Issues
```powershell
# Fix file permissions
icacls "C:\MochaCafe" /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls "C:\MochaCafe" /grant "Network Service:(OI)(CI)F" /T

# Check current permissions
icacls "C:\MochaCafe"
```

#### Port Conflicts
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process using port (replace PID)
taskkill /PID 1234 /F
```

### Windows Performance Monitoring

```powershell
# Monitor CPU and memory usage
Get-Counter "\Processor(_Total)\% Processor Time", "\Memory\Available MBytes" -SampleInterval 5 -MaxSamples 12

# Monitor specific process
Get-Process python | Select-Object Name, CPU, WorkingSet, VirtualMemorySize

# Check disk space
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="FreeSpace(GB)";Expression={[math]::Round($_.FreeSpace/1GB,2)}}
```

---

**Note**: This Windows deployment provides the same functionality as the Linux systemd services but uses Windows-native tools like NSSM for service management and Task Scheduler for maintenance tasks.