# SPEI Windows Installer Build Instructions

## Overview

This document provides instructions for building the SPEI Windows installer package. The installer creates a self-contained Windows application that requires no technical knowledge from end users.

## Prerequisites

### Development Environment
- **Windows 10/11** (64-bit) for building
- **Inno Setup 6** - Download from https://jrsoftware.org/isinfo.php
- **Internet connection** for downloading runtime components
- **Administrator privileges** for testing

### Build Tools
1. **Inno Setup 6.2.2 or later**
   - Download and install from official website
   - Add to PATH or use default installation path

2. **PowerShell 5.1 or later** (included with Windows)

## Build Process

### Step 1: Prepare the Build Environment

```batch
cd windows-installer
```

### Step 2: Download Runtime Components

Run the preparation script to download all required runtime components:

```batch
prepare-runtime.bat
```

This script will download:
- **Python 3.11.9 Embeddable** (~15MB)
- **Node.js 18.20.3** (~50MB)
- **PostgreSQL 15.7 Portable** (~200MB)
- **Redis for Windows** (~5MB)
- **Visual C++ Redistributables** (~25MB)

Total download size: ~295MB

### Step 3: Build the Installer

```batch
build-installer.bat
```

This will:
1. Verify Inno Setup installation
2. Prepare runtime components
3. Copy application files
4. Install Python dependencies
5. Build frontend assets
6. Compile the installer using Inno Setup

### Step 4: Test the Installer

The completed installer will be in the `dist/` directory:
- **File**: `SPEI-Setup-v1.0.0.exe`
- **Size**: ~500-800MB (depending on components)

## Manual Build Process

If you prefer to build manually:

### 1. Prepare Components
```batch
# Download and extract runtimes
powershell -ExecutionPolicy Bypass -File download-runtimes.ps1

# Copy application files
xcopy ..\backend app\backend /E /I /Y
xcopy ..\frontend app\frontend /E /I /Y
```

### 2. Install Dependencies
```batch
# Install Python dependencies
runtime\python\python.exe -m pip install poetry
cd app\backend
..\..\runtime\python\python.exe -m poetry install --no-dev

# Build frontend
cd ..\frontend
..\..\runtime\nodejs\npm.cmd install
..\..\runtime\nodejs\npm.cmd run build
```

### 3. Compile Installer
```batch
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss
```

## Installer Components

### Core Files Structure
```
SPEI-Setup-v1.0.0.exe
├── runtime/
│   ├── python/          # Python 3.11 embeddable
│   ├── nodejs/          # Node.js 18 runtime
│   ├── postgresql/      # PostgreSQL 15 portable
│   └── redis/           # Redis for Windows
├── app/
│   ├── backend/         # FastAPI application
│   └── frontend/        # React web interface
├── config/
│   └── .env.windows     # Windows-specific configuration
├── utils/
│   ├── SPEI.exe.bat     # Main launcher script
│   ├── first-run-setup.bat
│   └── stop-services.bat
└── docs/                # Documentation
```

### Installation Process
1. **Welcome & License**: User accepts terms
2. **Component Selection**: Choose installation components
3. **Configuration**: Database password, admin user, ports
4. **Installation**: Extract files, install dependencies
5. **First Run Setup**: Initialize database, create admin user
6. **Launch**: Start services and open web interface

## Configuration Options

### Installer Customization

Edit `setup.iss` to customize:

```pascal
[Setup]
AppName=SPEI - Sistema de Prontuário Eletrônico Inteligente
AppVersion=1.0.0
AppPublisher=CardioAI Pro
DefaultDirName={autopf}\SPEI
```

### Runtime Versions

Update `prepare-runtime.bat` to change versions:

```batch
# Python version
set PYTHON_VERSION=3.11.9

# Node.js version  
set NODEJS_VERSION=18.20.3

# PostgreSQL version
set POSTGRES_VERSION=15.7
```

### Medical Compliance

The installer includes compliance configurations for:
- **ANVISA** (Brazil): Medical device regulations
- **FDA** (USA): Software as Medical Device guidelines
- **EU MDR**: Medical Device Regulation compliance
- **LGPD/GDPR**: Data protection compliance
- **HIPAA**: Healthcare information security

## Testing the Installer

### Automated Testing
```batch
# Test installation in silent mode
SPEI-Setup-v1.0.0.exe /SILENT /SUPPRESSMSGBOXES

# Test uninstallation
"%ProgramFiles%\SPEI\unins000.exe" /SILENT
```

### Manual Testing Checklist
- [ ] Installer runs without errors
- [ ] All components install correctly
- [ ] Database initializes successfully
- [ ] Web interface loads at http://localhost:3000
- [ ] API responds at http://localhost:8000
- [ ] Admin login works with configured credentials
- [ ] Services start automatically after reboot
- [ ] Uninstaller removes all components

### Test Environments
- **Windows 10** (minimum supported version)
- **Windows 11** (recommended)
- **Windows Server 2019/2022** (enterprise environments)

## Troubleshooting Build Issues

### Common Problems

#### Inno Setup Not Found
```
ERROR: Inno Setup 6 not found!
```
**Solution**: Install Inno Setup 6 from https://jrsoftware.org/isinfo.php

#### Download Failures
```
ERROR: Failed to download Python runtime
```
**Solution**: Check internet connection, try running as administrator

#### Build Errors
```
ERROR: Failed to build installer!
```
**Solution**: Check Inno Setup compilation log for specific errors

#### Large Installer Size
The installer will be 500-800MB due to embedded runtimes. This is normal for a self-contained medical application.

### Debug Mode

Enable debug mode in `setup.iss`:
```pascal
[Setup]
; Add for debugging
OutputDir=dist
SetupLogging=yes
```

## Distribution

### Code Signing (Recommended)
For production distribution, sign the installer:

```batch
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com SPEI-Setup-v1.0.0.exe
```

### Checksums
Generate checksums for integrity verification:

```batch
certutil -hashfile SPEI-Setup-v1.0.0.exe SHA256 > SPEI-Setup-v1.0.0.exe.sha256
```

### Distribution Channels
- **Direct Download**: Host on secure HTTPS server
- **Medical Software Portals**: Submit to medical software directories
- **Enterprise Distribution**: Use internal software deployment tools

## Support and Maintenance

### Version Updates
1. Update version numbers in `setup.iss`
2. Update application files in `app/` directory
3. Test thoroughly before distribution
4. Provide migration scripts for database updates

### User Support
- Installation logs: `%TEMP%\Setup Log YYYY-MM-DD #NNN.txt`
- Application logs: `C:\ProgramData\SPEI\logs\`
- Support email: suporte@spei.med.br

---

**Build Environment**: Windows 10/11 64-bit  
**Build Tools**: Inno Setup 6.2.2+  
**Target Platforms**: Windows 10+ 64-bit  
**Installer Size**: ~500-800MB  
**Installation Time**: 5-15 minutes (depending on hardware)
