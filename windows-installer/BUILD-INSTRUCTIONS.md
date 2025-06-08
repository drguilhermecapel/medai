# SPEI Windows Installer Build Instructions

## Overview

This document provides comprehensive instructions for building the SPEI (Sistema de Prontuário Eletrônico Inteligente) Windows installer package. The installer creates a completely self-contained medical EMR system with AI support that requires no technical knowledge from end users.

**Key Features of the Windows Installer:**
- **Zero Technical Knowledge Required**: Fully automated installation process
- **Self-Contained**: Includes Python, Node.js, PostgreSQL, and all dependencies
- **Medical Compliance**: Pre-configured for ANVISA, FDA, EU MDR, LGPD, and HIPAA compliance
- **AI-Ready**: Includes medical diagnostic AI models and inference engine
- **Production Ready**: Suitable for medical practices and healthcare institutions

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

### Step 2: Build the Portable Installer (Single-Step Process)

```batch
build-installer.bat
```

This single command will:
1. Verify Inno Setup installation
2. Validate source application files
3. Compile the portable installer using Inno Setup
4. Create intelligent installer that downloads all components during installation
5. No manual preparation or component pre-downloading required

### Step 3: Test the Installer

The completed installer will be in the `dist/` directory:
- **File**: `SPEI-Setup-v1.0.0.exe`
- **Size**: ~50MB (components downloaded during installation)

### What Happens During Installation

The generated installer automatically:
- **Downloads Python 3.11.9 Embeddable** (~15MB)
- **Downloads Node.js 18.20.3** (~50MB)
- **Downloads PostgreSQL 15.7 Portable** (~200MB)
- **Downloads Redis for Windows** (~5MB)
- **Downloads Visual C++ Redistributables** (~25MB)
- **Configures all components**
- **Installs Python dependencies**
- **Builds frontend assets**
- **Initializes database**
- **Starts services**

Total download during installation: ~295MB

## Alternative: Manual Development Build Process

**Note**: Manual preparation is no longer required for creating the portable installer. The `build-installer.bat` script creates a fully portable installer automatically.

For development purposes only, if you need to manually prepare components:

### 1. Development Component Preparation (Optional)
```batch
# Only needed for development testing - NOT required for portable installer
prepare-runtime.bat
```

### 2. Portable Installer Compilation (Recommended)
```batch
# This is the standard approach - creates portable installer
build-installer.bat
```

The portable installer automatically handles all component downloads during installation, eliminating the need for manual preparation.

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
