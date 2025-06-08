# SPEI Windows Installer

## Overview

This directory contains a complete Windows installer package for SPEI (Sistema de Prontuário Eletrônico Inteligente), a medical EMR system with AI diagnostics. The installer creates a self-contained Windows application that requires no technical knowledge from end users.

## 🎯 Key Features

- **Self-Contained**: No external dependencies or Docker required
- **User-Friendly**: GUI wizard with simple configuration
- **Medical Compliance**: Pre-configured for ANVISA, FDA, HIPAA, LGPD
- **One-Click Installation**: Automated setup of all components
- **Professional**: Suitable for medical institutions and non-technical users

## 📦 What's Included

### Runtime Components (Auto-Downloaded)
- **Python 3.11** - Backend runtime environment
- **Node.js 18** - Frontend build and runtime
- **PostgreSQL 15** - Medical-grade database
- **Redis** - Caching and session management
- **Visual C++ Redistributables** - Required system libraries

### Application Components
- **FastAPI Backend** - Medical EMR API with AI diagnostics
- **React Frontend** - Modern web interface
- **Medical AI Models** - ECG analysis and diagnostic support
- **Compliance Tools** - Audit logging and data protection
- **Documentation** - User guides and technical documentation

## 🚀 Quick Start

### For End Users
1. Download `SPEI-Setup-v1.0.0.exe`
2. Run as Administrator
3. Follow the installation wizard
4. Access SPEI at http://localhost:3000

### For Developers
1. Install Inno Setup 6
2. Run `build-installer.bat`
3. Test the generated installer

## 📋 System Requirements

- **OS**: Windows 10 64-bit or later
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for installation
- **Privileges**: Administrator rights required

## 🔧 Build Process

### Prerequisites
- Windows 10/11 development machine
- Inno Setup 6.2.2 or later
- Internet connection for downloading components
- Administrator privileges

### Build Steps
```batch
cd windows-installer
build-installer.bat    # Build the installer (downloads components during installation)
```

### Output
- **File**: `dist/SPEI-Setup-v1.0.0.exe`
- **Size**: ~50MB (components downloaded during installation)
- **Type**: Windows executable installer

## 📁 Directory Structure

```
windows-installer/
├── setup.iss                 # Inno Setup script
├── build-installer.bat       # Main build script
├── config/
│   └── .env.windows          # Windows-specific configuration
├── utils/
│   ├── SPEI.exe.bat         # Main application launcher
│   ├── first-run-setup.bat  # Initial setup script
│   ├── stop-services.bat    # Service management
│   ├── download-python.bat  # Python runtime download utility
│   ├── download-nodejs.bat  # Node.js runtime download utility
│   ├── download-postgresql.bat # PostgreSQL download utility
│   ├── download-redis.bat   # Redis download utility
│   ├── error-handler.bat    # Centralized error handling
│   └── progress-indicator.bat # Installation progress tracking
├── assets/
│   ├── spei-icon.ico        # Application icon
│   └── web-icon.ico         # Web interface icon
├── docs/
│   └── INSTALLATION-GUIDE.md # Detailed installation guide
├── LICENSE.txt              # Software license
├── README.txt              # User-facing readme
└── BUILD-INSTRUCTIONS.md   # Developer build guide
```

## 🏥 Medical Compliance

The installer configures SPEI for compliance with:

- **ANVISA** (Brazil): Resolution CFM nº 1.821/2007
- **FDA** (USA): 21 CFR Part 820, Software as Medical Device
- **EU MDR**: Medical Device Regulation 2017/745
- **LGPD/GDPR**: Data protection and privacy
- **HIPAA**: Healthcare information security
- **ISO 13485**: Quality management for medical devices

## 🔒 Security Features

- **Data Encryption**: AES-256 encryption for sensitive data
- **Secure Authentication**: JWT-based authentication system
- **Audit Logging**: Comprehensive activity logging
- **Role-Based Access**: Granular permission system
- **Automatic Backups**: Daily encrypted backups
- **Firewall Configuration**: Automatic Windows Firewall setup

## 🎛️ Installation Options

### Installation Types
- **Full**: Complete installation with all features
- **Compact**: Essential components only
- **Custom**: User-selected components

### Configurable Components
- ✅ Core System (required)
- ✅ Database (required)
- ⬜ AI Modules (optional)
- ⬜ Sample Data (optional)
- ⬜ Documentation (optional)

### User Configuration
- Database password setup
- Administrator account creation
- Network port configuration
- Windows service integration
- Firewall rule creation

## 🧪 Testing

### Automated Tests
```batch
# Silent installation test
SPEI-Setup-v1.0.0.exe /SILENT

# Uninstallation test
"%ProgramFiles%\SPEI\unins000.exe" /SILENT
```

### Manual Testing Checklist
- [ ] Installer runs without errors
- [ ] All services start correctly
- [ ] Web interface accessible
- [ ] Database connection works
- [ ] Admin login successful
- [ ] AI modules functional
- [ ] Backup system operational

## 📞 Support

### For End Users
- **Email**: suporte@spei.med.br
- **Website**: https://spei.med.br
- **Phone**: +55 (11) 99999-9999
- **Documentation**: Included in installation

### For Developers
- **GitHub Issues**: Report bugs and feature requests
- **Build Guide**: See BUILD-INSTRUCTIONS.md
- **API Docs**: http://localhost:8000/docs (after installation)

## 📄 License

This software is licensed under the MIT License with additional medical compliance terms. See LICENSE.txt for full details.

## 🏆 About SPEI

SPEI (Sistema de Prontuário Eletrônico Inteligente) is a comprehensive electronic medical record system with artificial intelligence capabilities, designed specifically for healthcare professionals and medical institutions.

**Key Capabilities:**
- Complete patient record management
- AI-assisted diagnostics and analysis
- Telemedicine integration
- Regulatory compliance tools
- Advanced reporting and analytics
- Multi-user collaboration
- Data security and privacy protection

---

**Version**: 1.0.0  
**Build Date**: June 2025  
**Compatibility**: Windows 10+ 64-bit  
**Support**: Professional medical software support included
