@echo off
setlocal enabledelayedexpansion

:: SPEI Windows Launcher
:: This script starts all SPEI services on Windows

set "SPEI_HOME=%~dp0.."
set "PYTHON_HOME=%SPEI_HOME%\runtime\python"
set "NODE_HOME=%SPEI_HOME%\runtime\nodejs"
set "POSTGRES_HOME=%SPEI_HOME%\runtime\postgresql"
set "REDIS_HOME=%SPEI_HOME%\runtime\redis"

:: Set PATH
set "PATH=%PYTHON_HOME%;%PYTHON_HOME%\Scripts;%NODE_HOME%;%POSTGRES_HOME%\bin;%REDIS_HOME%;%PATH%"

:: Set environment variables
set "PYTHONPATH=%SPEI_HOME%\backend"
set "PGDATA=%SPEI_HOME%\data\postgres"
set "REDIS_DATA=%SPEI_HOME%\data\redis"

:: Create data directories
if not exist "%SPEI_HOME%\data" mkdir "%SPEI_HOME%\data"
if not exist "%PGDATA%" mkdir "%PGDATA%"
if not exist "%REDIS_DATA%" mkdir "%REDIS_DATA%"
if not exist "C:\ProgramData\SPEI\logs" mkdir "C:\ProgramData\SPEI\logs"
if not exist "C:\ProgramData\SPEI\uploads" mkdir "C:\ProgramData\SPEI\uploads"
if not exist "C:\ProgramData\SPEI\backups" mkdir "C:\ProgramData\SPEI\backups"

:: Check if this is first run
if not exist "%PGDATA%\postgresql.conf" (
    echo Initializing SPEI for first time...
    call "%SPEI_HOME%\utils\first-run-setup.bat"
)

:: Start services
echo Starting SPEI services...

:: Start PostgreSQL
echo Starting PostgreSQL database...
start /B "PostgreSQL" "%POSTGRES_HOME%\bin\pg_ctl.exe" -D "%PGDATA%" -l "%SPEI_HOME%\data\postgres.log" start

:: Wait for PostgreSQL to start
timeout /t 5 /nobreak >nul

:: Start Redis
echo Starting Redis cache...
start /B "Redis" "%REDIS_HOME%\redis-server.exe" --dir "%REDIS_DATA%" --logfile "%SPEI_HOME%\data\redis.log" --daemonize yes

:: Wait for Redis to start
timeout /t 3 /nobreak >nul

:: Start FastAPI backend
echo Starting SPEI API...
cd /d "%SPEI_HOME%\backend"
start /B "SPEI-API" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

:: Start Celery worker
echo Starting background tasks...
start /B "SPEI-Celery" python -m celery -A app.core.celery worker --loglevel=info

:: Wait for API to start
timeout /t 10 /nobreak >nul

:: Start frontend (if built)
if exist "%SPEI_HOME%\frontend\dist" (
    echo Starting SPEI Web Interface...
    cd /d "%SPEI_HOME%\frontend"
    start /B "SPEI-Web" python -m http.server 3000 --directory dist
)

:: Open web browser
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo SPEI started successfully!
echo.
echo Web Interface: http://localhost:3000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press any key to open the web interface
echo or close this window to run in background
echo ========================================
pause >nul

start http://localhost:3000
