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
set "INNO_SETUP_ALT=C:\Program Files\Inno Setup 6\ISCC.exe"
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
echo Looking for: "%INNO_SETUP%"
if not exist "%INNO_SETUP%" (
    echo Primary location not found, checking alternative location...
    echo Looking for: "%INNO_SETUP_ALT%"
    if not exist "%INNO_SETUP_ALT%" (
        echo ERROR: Inno Setup 6 not found!
        echo Checked locations:
        echo - "%INNO_SETUP%"
        echo - "%INNO_SETUP_ALT%"
        echo.
        echo SOLUTION:
        echo 1. Download Inno Setup 6 from: https://jrsoftware.org/isinfo.php
        echo 2. Install with default settings
        echo 3. Re-run this script
        echo.
        pause
        exit /b 1
    ) else (
        set "INNO_SETUP=%INNO_SETUP_ALT%"
        echo ✓ Inno Setup 6 found at alternative location
    )
) else (
    echo ✓ Inno Setup 6 found at primary location
)


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

:: Validate icon files (optional - warn if corrupted but don't fail)
echo Validating icon files...
if exist "assets\spei-icon.ico" (
    for %%A in ("assets\spei-icon.ico") do (
        if %%~zA LSS 1000 (
            echo WARNING: spei-icon.ico appears to be corrupted (%%~zA bytes)
            echo Icon references have been disabled in setup.iss
        ) else (
            echo ✓ spei-icon.ico appears valid (%%~zA bytes)
        )
    )
) else (
    echo INFO: spei-icon.ico not found - using default system icons
)

if exist "assets\web-icon.ico" (
    for %%A in ("assets\web-icon.ico") do (
        if %%~zA LSS 1000 (
            echo WARNING: web-icon.ico appears to be corrupted (%%~zA bytes)
            echo Icon references have been disabled in setup.iss
        ) else (
            echo ✓ web-icon.ico appears valid (%%~zA bytes)
        )
    )
) else (
    echo INFO: web-icon.ico not found - using default system icons
)

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
echo Installer Configuration
echo ========================================

echo ✓ Self-contained installer mode enabled
echo ✓ Runtime components configured for automatic installation
echo ✓ Automated setup process for end users
echo ✓ Creates fully functional SPEI medical EMR system

:: Check for source application files (will be copied during installation)
echo Validating source application files...
if not exist "..\backend" (
    echo ERROR: Backend source files not found!
    echo Expected: ..\backend
    echo Please ensure you are running this script from the windows-installer directory.
    pause
    exit /b 1
)
echo ✓ Backend source files found

if not exist "..\frontend" (
    echo ERROR: Frontend source files not found!
    echo Expected: ..\frontend
    echo Please ensure you are running this script from the windows-installer directory.
    pause
    exit /b 1
)
echo ✓ Frontend source files found

:: Verify backend requirements.txt exists in source
if not exist "..\backend\requirements.txt" (
    echo ERROR: Backend requirements.txt not found in source!
    echo Expected: ..\backend\requirements.txt
    echo This file is required for Python dependency installation.
    pause
    exit /b 1
)
echo ✓ Backend requirements.txt found in source

:: Verify frontend package.json exists in source
if not exist "..\frontend\package.json" (
    echo ERROR: Frontend package.json not found in source!
    echo Expected: ..\frontend\package.json
    echo This file is required for Node.js dependency installation.
    pause
    exit /b 1
)
echo ✓ Frontend package.json found in source

echo.
echo ========================================
echo Building Installer
echo ========================================

echo Running Inno Setup compiler...
echo Command: "%INNO_SETUP%" "%SCRIPT_PATH%"
echo.
echo Compiling installer... This may take several minutes.
echo Please wait while the installer is being built...
echo.
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

:: Check installer file size (should be reasonable for self-contained installer)
for %%A in ("%INSTALLER_PATH%") do set "installer_size=%%~zA"
if %installer_size% LSS 5000000 (
    echo WARNING: Installer file is smaller than expected (%installer_size% bytes).
    echo Expected minimum size: ~5MB
    echo This may indicate missing application files or incomplete build.
    echo.
    echo The installer should contain:
    echo - Application source files
    echo - Configuration files
    echo - Utility scripts
    echo - Installation wizard
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
set /a "installer_mb=%installer_size% / 1048576"
echo - Size: %installer_size% bytes (~%installer_mb% MB)
echo - Created: %DATE% %TIME%
echo.

:: Show directory listing
echo Output directory contents:
dir "%DIST_DIR%" /B

echo.
echo ========================================
echo SPEI Installer Ready!
echo ========================================
echo.
echo Your SPEI installer is ready for distribution:
echo - Double-click to install on any Windows 10/11 system
echo - User-friendly installation wizard
echo - Automatically configures all components
echo - Creates fully functional medical EMR system
echo.
echo Testing checklist:
echo 1. Test installer on clean Windows system
echo 2. Verify all components install correctly
echo 3. Confirm application launches after installation
echo 4. Test medical record functionality
echo 5. Validate compliance and security features
echo.
echo The installer is ready for distribution!
echo.

pause
