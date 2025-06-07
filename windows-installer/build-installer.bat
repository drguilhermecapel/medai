@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SPEI Windows Installer Builder
echo ========================================
echo.

:: Set paths
set "SCRIPT_DIR=%~dp0"
set "DIST_DIR=%SCRIPT_DIR%dist"
set "UTILS_DIR=%SCRIPT_DIR%utils"
set "RUNTIME_DIR=%SCRIPT_DIR%runtime"
set "APP_DIR=%SCRIPT_DIR%app"
set "CONFIG_DIR=%SCRIPT_DIR%config"
set "MODELS_DIR=%SCRIPT_DIR%models"
set "SAMPLES_DIR=%SCRIPT_DIR%samples"
set "INNO_SETUP=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set "SCRIPT_PATH=%SCRIPT_DIR%setup.iss"

echo Build Environment:
echo - Script Directory: %SCRIPT_DIR%
echo - Output Directory: %DIST_DIR%
echo - Utilities Directory: %UTILS_DIR%
echo - Runtime Directory: %RUNTIME_DIR%
echo.

echo ========================================
echo Pre-Build Validation
echo ========================================

:: Check if Inno Setup is installed
echo Checking Inno Setup installation...
if not exist "%INNO_SETUP%" (
    echo ERROR: Inno Setup 6 not found!
    echo Expected location: %INNO_SETUP%
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

:: Check for setup.iss script
echo Checking setup script...
if not exist "%SCRIPT_PATH%" (
    echo ERROR: Setup script not found!
    echo Expected: %SCRIPT_PATH%
    echo Please ensure setup.iss exists in the windows-installer directory.
    pause
    exit /b 1
)
echo ✓ Setup script found

:: Validate required utility scripts
echo Validating required utility scripts...

if not exist "%UTILS_DIR%\init-database.bat" (
    echo ERROR: Missing required utility script: init-database.bat
    echo This file is required for database initialization during installation.
    echo Expected: %UTILS_DIR%\init-database.bat
    pause
    exit /b 1
)
echo ✓ init-database.bat found

if not exist "%UTILS_DIR%\install-dependencies.bat" (
    echo ERROR: Missing required utility script: install-dependencies.bat
    echo This file is required for Python dependency installation.
    echo Expected: %UTILS_DIR%\install-dependencies.bat
    pause
    exit /b 1
)
echo ✓ install-dependencies.bat found

if not exist "%UTILS_DIR%\build-frontend.bat" (
    echo ERROR: Missing required utility script: build-frontend.bat
    echo This file is required for frontend building during installation.
    echo Expected: %UTILS_DIR%\build-frontend.bat
    pause
    exit /b 1
)
echo ✓ build-frontend.bat found

if not exist "%UTILS_DIR%\SPEI.exe.bat" (
    echo ERROR: Missing required launcher script: SPEI.exe.bat
    echo This file is required for launching the application.
    echo Expected: %UTILS_DIR%\SPEI.exe.bat
    pause
    exit /b 1
)
echo ✓ SPEI.exe.bat found

if not exist "%UTILS_DIR%\stop-services.bat" (
    echo ERROR: Missing required utility script: stop-services.bat
    echo This file is required for stopping services during uninstallation.
    echo Expected: %UTILS_DIR%\stop-services.bat
    pause
    exit /b 1
)
echo ✓ stop-services.bat found

:: Check for configuration files
echo Validating configuration files...
if not exist "%CONFIG_DIR%\.env.windows" (
    echo ERROR: Missing Windows configuration file!
    echo Expected: %CONFIG_DIR%\.env.windows
    echo This file is required for Windows-specific environment configuration.
    pause
    exit /b 1
)
echo ✓ Windows configuration file found

:: Check for required directories
echo Validating required directories...
if not exist "%MODELS_DIR%" (
    echo ERROR: Missing models directory!
    echo Expected: %MODELS_DIR%
    echo This directory is required for AI model storage.
    pause
    exit /b 1
)
echo ✓ Models directory found

if not exist "%SAMPLES_DIR%" (
    echo ERROR: Missing samples directory!
    echo Expected: %SAMPLES_DIR%
    echo This directory is required for sample data storage.
    pause
    exit /b 1
)
echo ✓ Samples directory found

:: Create output directory
echo Creating output directory...
if not exist "%DIST_DIR%" (
    mkdir "%DIST_DIR%"
    if !ERRORLEVEL! NEQ 0 (
        echo ERROR: Failed to create output directory!
        echo Path: %DIST_DIR%
        echo Please check permissions and try running as Administrator.
        pause
        exit /b 1
    )
)
echo ✓ Output directory ready

echo.
echo ========================================
echo Runtime Components Preparation
echo ========================================

:: Check if runtime components exist, if not prepare them
if not exist "%RUNTIME_DIR%\python\python.exe" (
    echo Python runtime not found. Preparing runtime components...
    call prepare-runtime.bat
    if !ERRORLEVEL! NEQ 0 (
        echo ERROR: Failed to prepare runtime components!
        echo Please check the error messages above and resolve any issues.
        pause
        exit /b 1
    )
) else (
    echo ✓ Python runtime found
)

if not exist "%RUNTIME_DIR%\nodejs\node.exe" (
    echo ERROR: Node.js runtime not found after preparation!
    echo Expected: %RUNTIME_DIR%\nodejs\node.exe
    echo Please run prepare-runtime.bat manually to resolve this issue.
    pause
    exit /b 1
)
echo ✓ Node.js runtime found

if not exist "%RUNTIME_DIR%\postgresql\bin\postgres.exe" (
    echo ERROR: PostgreSQL runtime not found after preparation!
    echo Expected: %RUNTIME_DIR%\postgresql\bin\postgres.exe
    echo Please run prepare-runtime.bat manually to resolve this issue.
    pause
    exit /b 1
)
echo ✓ PostgreSQL runtime found

:: Check for application files
echo Validating application files...
if not exist "%APP_DIR%\backend" (
    echo ERROR: Backend application files not found!
    echo Expected: %APP_DIR%\backend
    echo Please run prepare-runtime.bat to copy application files.
    pause
    exit /b 1
)
echo ✓ Backend application files found

if not exist "%APP_DIR%\frontend" (
    echo ERROR: Frontend application files not found!
    echo Expected: %APP_DIR%\frontend
    echo Please run prepare-runtime.bat to copy application files.
    pause
    exit /b 1
)
echo ✓ Frontend application files found

:: Verify backend requirements.txt exists
if not exist "%APP_DIR%\backend\requirements.txt" (
    echo ERROR: Backend requirements.txt not found!
    echo Expected: %APP_DIR%\backend\requirements.txt
    echo This file is required for Python dependency installation.
    pause
    exit /b 1
)
echo ✓ Backend requirements.txt found

:: Verify frontend package.json exists
if not exist "%APP_DIR%\frontend\package.json" (
    echo ERROR: Frontend package.json not found!
    echo Expected: %APP_DIR%\frontend\package.json
    echo This file is required for Node.js dependency installation.
    pause
    exit /b 1
)
echo ✓ Frontend package.json found

echo.
echo ========================================
echo Building Installer
echo ========================================

echo Running Inno Setup compiler...
"%INNO_SETUP%" "%SCRIPT_PATH%"

if !ERRORLEVEL! NEQ 0 (
    echo.
    echo ERROR: Failed to build installer!
    echo.
    echo Common issues and solutions:
    echo 1. Missing files referenced in setup.iss
    echo 2. Syntax errors in setup.iss
    echo 3. Insufficient disk space
    echo 4. Permission issues
    echo.
    echo Please check the Inno Setup output above for specific error details.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Post-Build Validation
echo ========================================

:: Verify installer was created
set "INSTALLER_PATH=%DIST_DIR%\SPEI-Setup-v1.0.0.exe"
if not exist "%INSTALLER_PATH%" (
    echo ERROR: Installer file was not created!
    echo Expected: %INSTALLER_PATH%
    echo.
    echo This indicates the build process failed silently.
    echo Please check the Inno Setup output for warnings or errors.
    pause
    exit /b 1
)
echo ✓ Installer file created successfully

:: Check installer file size (should be substantial)
for %%A in ("%INSTALLER_PATH%") do set "installer_size=%%~zA"
if %installer_size% LSS 50000000 (
    echo WARNING: Installer file is smaller than expected (%installer_size% bytes).
    echo Expected size: ~200MB or more
    echo This may indicate missing components or incomplete build.
    echo.
    echo Please verify the installer contains all required components:
    echo - Python runtime (~50MB)
    echo - Node.js runtime (~30MB)
    echo - PostgreSQL runtime (~200MB)
    echo - Application files
    echo.
    pause
)

:: Display build results
echo.
echo ========================================
echo Build Completed Successfully!
echo ========================================
echo.
echo Installer Details:
echo - File: %INSTALLER_PATH%
echo - Size: %installer_size% bytes (~!installer_size:~0,-6! MB)
echo - Created: %DATE% %TIME%
echo.

:: Show directory listing
echo Output directory contents:
dir "%DIST_DIR%" /B

echo.
echo ========================================
echo Next Steps
echo ========================================
echo.
echo 1. Test the installer on a clean Windows system
echo 2. Verify all components install correctly
echo 3. Test the application functionality after installation
echo 4. Check that all services start properly
echo 5. Validate database initialization and data persistence
echo.
echo The installer is ready for distribution!
echo.

pause
