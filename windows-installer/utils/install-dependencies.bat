@echo off
setlocal enabledelayedexpansion

call "%~dp0progress-indicator.bat" "Instalando Dependências Python" "7" "8" "Configurando backend"

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
    call "%~dp0error-handler.bat" "Python Runtime" "Python não encontrado em %PYTHON_HOME%" "Execute o download do Python primeiro"
    exit /b 1
)

:: Check if backend directory exists
if not exist "%BACKEND_DIR%" (
    call "%~dp0error-handler.bat" "Backend Files" "Diretório backend não encontrado em %BACKEND_DIR%" "Verifique se os arquivos da aplicação foram instalados corretamente"
    exit /b 1
)

:: Check if requirements.txt exists
if not exist "%BACKEND_DIR%\requirements.txt" (
    call "%~dp0error-handler.bat" "Requirements File" "requirements.txt não encontrado em %BACKEND_DIR%" "Arquivo de dependências necessário para instalação"
    exit /b 1
)

:: Verify pip is available
echo Checking pip installation...
"%PYTHON_HOME%\python.exe" -m pip --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    call "%~dp0error-handler.bat" "Pip Installation" "pip não está disponível no ambiente Python" "Execute o download e configuração do Python primeiro"
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
    call "%~dp0error-handler.bat" "Python Dependencies" "Falha ao instalar dependências Python" "Verifique conectividade com internet e arquivo requirements.txt"
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
