# SPEI Windows Installation Guide

## Overview

This guide provides detailed instructions for installing and configuring SPEI (Sistema de Prontuário Eletrônico Inteligente) on Windows systems.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 64-bit (version 1903 or later)
- **Processor**: Intel Core i3 or AMD equivalent (2 cores)
- **Memory**: 4 GB RAM
- **Storage**: 2 GB available disk space
- **Network**: Internet connection for installation

### Recommended Requirements
- **Operating System**: Windows 11 64-bit
- **Processor**: Intel Core i5 or AMD equivalent (4+ cores)
- **Memory**: 8 GB RAM or more
- **Storage**: 5 GB available disk space (SSD recommended)
- **Network**: Broadband internet connection

## Installation Process

### Step 1: Download the Installer
1. Download `SPEI-Setup-v1.0.0.exe` from the official website
2. Verify the file integrity (SHA256 checksum provided)
3. Ensure you have administrator privileges

### Step 2: Run the Installer
1. Right-click on `SPEI-Setup-v1.0.0.exe`
2. Select "Run as administrator"
3. If Windows SmartScreen appears, click "More info" then "Run anyway"

### Step 3: Installation Wizard
1. **Welcome Screen**: Click "Next" to continue
2. **License Agreement**: Read and accept the license terms
3. **Installation Type**: Choose "Full Installation" (recommended)
4. **Destination Folder**: Default is `C:\Program Files\SPEI`
5. **Components**: Select components to install:
   - ✅ Core System (required)
   - ✅ Database (required)
   - ✅ AI Modules (recommended)
   - ⬜ Sample Data (optional)
   - ⬜ Documentation (optional)

### Step 4: Configuration
1. **Database Password**: Set a secure password (minimum 8 characters)
2. **Admin User**: Configure the administrator account
   - Email: `admin@hospital.local` (or your preferred email)
   - Password: Set a strong password (minimum 6 characters)
3. **Network Ports**: Configure network settings
   - API Port: `8000` (default)
   - Web Port: `3000` (default)
4. **Additional Tasks**:
   - ✅ Create desktop shortcut
   - ✅ Configure Windows Firewall
   - ✅ Start SPEI automatically with Windows

### Step 5: Installation
1. Click "Install" to begin the installation process
2. The installer will:
   - Extract and install runtime components
   - Configure the database
   - Install Python dependencies
   - Build the web interface
   - Configure Windows services
   - Set up security settings

### Step 6: First Launch
1. The installer will automatically start SPEI
2. Your default web browser will open to `http://localhost:3000`
3. Log in with the administrator credentials you configured

## Post-Installation Configuration

### Initial Setup
1. **Change Default Passwords**: Update all default passwords
2. **Configure Email**: Set up SMTP settings for notifications
3. **Import Data**: Import existing patient data if applicable
4. **User Management**: Create additional user accounts
5. **Backup Configuration**: Set up automatic backups

### Security Configuration
1. **Firewall Rules**: Verify Windows Firewall rules are correctly configured
2. **User Permissions**: Configure user roles and permissions
3. **Audit Logging**: Enable comprehensive audit logging
4. **Data Encryption**: Verify data encryption is active

## Troubleshooting

### Common Issues

#### Installation Fails
- **Cause**: Insufficient permissions
- **Solution**: Run installer as administrator

#### Ports Already in Use
- **Cause**: Another application is using ports 3000 or 8000
- **Solution**: Change ports during installation or stop conflicting services

#### Database Connection Error
- **Cause**: PostgreSQL service not starting
- **Solution**: Check Windows Services, restart PostgreSQL service

#### Web Interface Not Loading
- **Cause**: Frontend build failed or web server not starting
- **Solution**: Check logs in `C:\ProgramData\SPEI\logs`

### Log Files
- **Application Logs**: `C:\ProgramData\SPEI\logs\app.log`
- **Database Logs**: `C:\ProgramData\SPEI\logs\postgres.log`
- **Web Server Logs**: `C:\ProgramData\SPEI\logs\web.log`

### Getting Help
- **Documentation**: Check the included user manual
- **Support Email**: suporte@spei.med.br
- **Website**: https://spei.med.br/support
- **Phone**: +55 (11) 99999-9999

## Uninstallation

To remove SPEI:
1. Go to Windows Settings > Apps
2. Find "SPEI" in the list
3. Click "Uninstall"
4. Follow the uninstallation wizard
5. Optionally remove data files from `C:\ProgramData\SPEI`

## Data Backup and Recovery

### Automatic Backups
SPEI automatically creates daily backups stored in:
`C:\ProgramData\SPEI\backups`

### Manual Backup
1. Open SPEI web interface
2. Go to Administration > Backup
3. Click "Create Backup"
4. Download the backup file

### Restore from Backup
1. Stop SPEI services
2. Run the restore utility: `C:\Program Files\SPEI\utils\restore-backup.bat`
3. Select the backup file
4. Restart SPEI services

## Updates

### Automatic Updates
SPEI checks for updates automatically and notifies administrators when updates are available.

### Manual Updates
1. Download the latest installer
2. Run the installer (it will detect the existing installation)
3. Follow the update wizard
4. Your data and configuration will be preserved

## Compliance and Security

### Medical Compliance
SPEI is configured for compliance with:
- **ANVISA** (Brazil): Resolution CFM nº 1.821/2007
- **FDA** (USA): 21 CFR Part 820
- **EU MDR**: Medical Device Regulation 2017/745
- **LGPD/GDPR**: Data protection regulations
- **HIPAA**: Healthcare information security

### Security Features
- End-to-end encryption
- Secure authentication (JWT)
- Role-based access control
- Comprehensive audit logging
- Automatic security updates
- Data anonymization tools

### Audit and Compliance Reports
Generate compliance reports from:
Administration > Compliance > Generate Report

## Performance Optimization

### System Optimization
1. **SSD Storage**: Use SSD for better performance
2. **Memory**: 8GB+ RAM recommended for optimal performance
3. **Antivirus**: Add SPEI directories to antivirus exclusions
4. **Windows Updates**: Keep Windows updated

### Database Optimization
1. **Regular Maintenance**: Database maintenance runs automatically
2. **Index Optimization**: Automatic index optimization
3. **Data Archiving**: Configure automatic data archiving

## Support and Maintenance

### Professional Support
- 12 months of technical support included
- Priority support available for healthcare institutions
- On-site training and setup available

### Community Support
- User forums: https://community.spei.med.br
- Documentation wiki: https://docs.spei.med.br
- Video tutorials: https://youtube.com/speimedical

---

**Document Version**: 1.0.0  
**Last Updated**: June 2025  
**Support Contact**: suporte@spei.med.br
