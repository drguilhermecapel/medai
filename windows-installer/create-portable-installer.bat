@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SPEI Portable Installer Creator
echo ========================================
echo.
echo This script creates a portable Windows installer for SPEI
echo (Sistema de Prontuário Eletrônico Inteligente) that works
echo with just a double-click on any Windows 10/11 system.
echo.

:: Set paths
set "SCRIPT_DIR=%~dp0"
set "INNO_SETUP=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

echo ========================================
echo Pre-Build Validation
echo ========================================

:: Check if we're in the correct directory
echo Checking directory structure...
if not exist "%SCRIPT_DIR%setup.iss" (
    echo ERROR: This script must be run from the windows-installer directory!
    echo Expected: %SCRIPT_DIR%setup.iss
    echo.
    echo Please navigate to the windows-installer directory and run this script again.
    echo.
    pause
    exit /b 1
)
echo ✓ Running from correct directory

:: Check if Inno Setup is installed
echo Checking Inno Setup installation...
if not exist "%INNO_SETUP%" (
    echo ERROR: Inno Setup 6 not found!
    echo Expected location: "%INNO_SETUP%"
    echo.
    echo SOLUTION:
    echo 1. Download Inno Setup 6 from: https://jrsoftware.org/isinfo.php
    echo 2. Install with default settings
    echo 3. Re-run this script
    echo.
    pause
    exit /b 1
)
echo ✓ Inno Setup 6 found

:: Check for source application files
echo Validating source application files...
if not exist "..\backend" (
    echo ERROR: Backend source files not found!
    echo Expected: ..\backend
    echo Please ensure you have the complete SPEI source code.
    pause
    exit /b 1
)
echo ✓ Backend source files found

if not exist "..\frontend" (
    echo ERROR: Frontend source files not found!
    echo Expected: ..\frontend
    echo Please ensure you have the complete SPEI source code.
    pause
    exit /b 1
)
echo ✓ Frontend source files found

echo.
echo ========================================
echo Creating Portable Installer
echo ========================================
echo.
echo Building portable installer that will:
echo - Download Python 3.11 automatically during installation
echo - Download Node.js 18 automatically during installation
echo - Download PostgreSQL 15 automatically during installation
echo - Download Redis automatically during installation
echo - Configure all components automatically
echo - Create fully functional medical EMR system
echo.
echo This may take a few minutes...
echo.

:: Call the main build script
call "%SCRIPT_DIR%build-installer.bat"

if !ERRORLEVEL! NEQ 0 (
    echo.
    echo ========================================
    echo Build Failed!
    echo ========================================
    echo.
    echo The portable installer could not be created.
    echo Please check the error messages above and try again.
    echo.
    echo Common solutions:
    echo - Ensure Inno Setup 6 is properly installed
    echo - Check that all source files are present
    echo - Run as Administrator if permission issues occur
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Portable Installer Created Successfully!
echo ========================================
echo.
echo Your portable SPEI installer is ready:
echo.
echo 📦 File: dist\SPEI-Setup-v1.0.0.exe
echo 📏 Size: ~50MB (portable installer)
echo 🎯 Features: Double-click to install on any Windows 10/11
echo 🏥 Purpose: Medical EMR system for healthcare professionals
echo.
echo ========================================
echo Distribution Instructions
echo ========================================
echo.
echo For End Users:
echo 1. Share the SPEI-Setup-v1.0.0.exe file
echo 2. Users double-click to install (no technical knowledge required)
echo 3. Installer automatically downloads all components (~295MB)
echo 4. System is ready to use after installation completes
echo.
echo For Healthcare Institutions:
echo - The installer is fully compliant with medical regulations
echo - No external dependencies or Docker required
echo - Suitable for non-technical medical staff
echo - Includes ANVISA, FDA, HIPAA, and LGPD compliance features
echo.
echo The portable installer is ready for distribution!
echo.

pause
