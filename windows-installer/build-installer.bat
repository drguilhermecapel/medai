@echo off
echo ========================================
echo SPEI Windows Installer Builder
echo ========================================

:: Check if Inno Setup is installed
if not exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo ERROR: Inno Setup 6 not found!
    echo Please download and install from: https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

:: Set paths
set "INNO_SETUP=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set "SCRIPT_PATH=%~dp0setup.iss"
set "OUTPUT_DIR=%~dp0dist"

:: Create output directory
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

:: Check if source directories exist
if not exist "..\backend" (
    echo ERROR: Backend directory not found at ..\backend
    echo Please ensure you are running this from the windows-installer directory
    pause
    exit /b 1
)

if not exist "..\frontend" (
    echo ERROR: Frontend directory not found at ..\frontend
    echo Please ensure you are running this from the windows-installer directory
    pause
    exit /b 1
)

:: Download and prepare runtime components
echo Preparing runtime components...
call prepare-runtime.bat

:: Build the installer
echo Building installer...
"%INNO_SETUP%" "%SCRIPT_PATH%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Installer built successfully!
    echo.
    echo Output: %OUTPUT_DIR%\SPEI-Setup-v1.0.0.exe
    if exist "%OUTPUT_DIR%\SPEI-Setup-v1.0.0.exe" (
        echo Size: 
        dir "%OUTPUT_DIR%\SPEI-Setup-v1.0.0.exe" | findstr "SPEI-Setup"
    ) else (
        echo WARNING: Installer file not found in expected location
    )
    echo ========================================
) else (
    echo.
    echo ERROR: Failed to build installer!
    echo Check the error messages above.
    echo.
    echo Common issues:
    echo - Missing source directories (backend/frontend)
    echo - Inno Setup not installed or wrong version
    echo - Missing runtime components
)

pause
