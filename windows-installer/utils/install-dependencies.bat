@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SPEI Python Dependencies Installation
echo ========================================

:: Set environment variables
set "SPEI_HOME=%~dp0.."
set "PYTHON_HOME=%SPEI_HOME%\runtime\python"
set "BACKEND_DIR=%SPEI_HOME%\app\backend"

echo SPEI Home: %SPEI_HOME%
echo Python Home: %PYTHON_HOME%
echo Backend Directory: %BACKEND_DIR%
echo.

:: Check if Python runtime exists
if not exist "%PYTHON_HOME%\python.exe" (
    echo ERROR: Python runtime not found at %PYTHON_HOME%
    echo Please run prepare-runtime.bat first to download Python.
    pause
    exit /b 1
)

:: Check if backend directory exists
if not exist "%BACKEND_DIR%" (
    echo ERROR: Backend directory not found at %BACKEND_DIR%
    echo Please ensure the application files are properly installed.
    pause
    exit /b 1
)

:: Check if requirements.txt exists
if not exist "%BACKEND_DIR%\requirements.txt" (
    echo ERROR: requirements.txt not found in %BACKEND_DIR%
    echo Cannot install Python dependencies without requirements file.
    pause
    exit /b 1
)

:: Verify pip is available
echo Checking pip installation...
"%PYTHON_HOME%\python.exe" -m pip --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: pip is not available in the Python environment!
    echo Please run prepare-runtime.bat to properly configure Python.
    pause
    exit /b 1
)
echo ✓ pip is available

:: Upgrade pip to latest version
echo Upgrading pip to latest version...
"%PYTHON_HOME%\python.exe" -m pip install --upgrade pip
if !ERRORLEVEL! NEQ 0 (
    echo WARNING: Failed to upgrade pip, continuing with current version...
)

:: Install Python dependencies
echo Installing Python dependencies from requirements.txt...
cd /d "%BACKEND_DIR%"
"%PYTHON_HOME%\python.exe" -m pip install -r requirements.txt --no-warn-script-location
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Failed to install Python dependencies!
    echo.
    echo This could be due to:
    echo - Network connectivity issues
    echo - Missing system dependencies
    echo - Incompatible package versions
    echo.
    echo Please check the error messages above and try again.
    pause
    exit /b 1
)

:: Verify critical packages are installed
echo Verifying critical packages installation...
set "CRITICAL_PACKAGES=fastapi uvicorn sqlalchemy alembic psycopg2-binary"

for %%p in (%CRITICAL_PACKAGES%) do (
    echo Checking %%p...
    "%PYTHON_HOME%\python.exe" -c "import %%p" >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo WARNING: Package %%p may not be properly installed!
    ) else (
        echo ✓ %%p is available
    )
)

:: Test FastAPI import specifically
echo Testing FastAPI application import...
"%PYTHON_HOME%\python.exe" -c "from app.main import app; print('FastAPI app imported successfully')" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo WARNING: FastAPI application import failed!
    echo The backend may not start properly.
    echo Check the application code for import errors.
) else (
    echo ✓ FastAPI application can be imported
)

cd /d "%SPEI_HOME%"

echo.
echo ========================================
echo Python dependencies installation completed!
echo ========================================
echo.
echo All required Python packages have been installed.
echo The backend should now be ready to run.
echo.
pause
