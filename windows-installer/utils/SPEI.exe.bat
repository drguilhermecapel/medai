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
if not exist "%SPEI_HOME%\logs" mkdir "%SPEI_HOME%\logs"
if not exist "C:\ProgramData\SPEI\logs" mkdir "C:\ProgramData\SPEI\logs"
if not exist "C:\ProgramData\SPEI\uploads" mkdir "C:\ProgramData\SPEI\uploads"
:: Add Windows Firewall rules for SPEI ports
echo Configuring Windows Firewall rules...
netsh advfirewall firewall add rule name="SPEI API Port 8000" dir=in action=allow protocol=TCP localport=8000 >nul 2>&1
netsh advfirewall firewall add rule name="SPEI Web Port 3000" dir=in action=allow protocol=TCP localport=3000 >nul 2>&1


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
start /B "PostgreSQL" "%POSTGRES_HOME%\bin\pg_ctl.exe" -D "%PGDATA%" -l "%SPEI_HOME%\logs\postgres.log" start

:: Wait for PostgreSQL to start and verify connection
set POSTGRES_RETRIES=0
:wait_postgres
timeout /t 2 /nobreak >nul
"%POSTGRES_HOME%\bin\pg_isready.exe" -h localhost -p 5432 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set /a POSTGRES_RETRIES+=1
    if !POSTGRES_RETRIES! LSS 10 goto wait_postgres
    echo ERROR: PostgreSQL failed to start after 20 seconds
    call :show_error_dialog "PostgreSQL Database Error" "PostgreSQL failed to start. Please check the logs at %SPEI_HOME%\logs\postgres.log"
    pause
    exit /b 1
)
echo PostgreSQL started successfully

:: Start Redis
echo Starting Redis cache...
start /B "Redis" "%REDIS_HOME%\redis-server.exe" --dir "%REDIS_DATA%" --logfile "%SPEI_HOME%\logs\redis.log" --daemonize yes

:: Wait for Redis to start and verify connection
set REDIS_RETRIES=0
:wait_redis
timeout /t 2 /nobreak >nul
"%REDIS_HOME%\redis-cli.exe" ping >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set /a REDIS_RETRIES+=1
    if !REDIS_RETRIES! LSS 5 goto wait_redis
    echo WARNING: Redis may not be ready, continuing anyway...
)
echo Redis started successfully

:: Start FastAPI backend
echo Starting SPEI API...
cd /d "%SPEI_HOME%\backend"
start /B "SPEI-API" cmd /c "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "%SPEI_HOME%\logs\api.log" 2>&1"

:: Start Celery worker
echo Starting background tasks...
start /B "SPEI-Celery" cmd /c "python -m celery -A app.core.celery worker --loglevel=info > "%SPEI_HOME%\logs\celery.log" 2>&1"

:: Wait for API to respond
set API_RETRIES=0
:wait_api
timeout /t 2 /nobreak >nul
curl -f http://localhost:8000/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set /a API_RETRIES+=1
    if !API_RETRIES! LSS 15 goto wait_api
    echo ERROR: API failed to start after 30 seconds
    call :show_error_dialog "API Server Error" "SPEI API failed to start. Please check the logs at %SPEI_HOME%\logs\api.log"
    pause
    exit /b 1
)
echo API started successfully

:: Start frontend (if built)
if exist "%SPEI_HOME%\frontend\dist" (
    echo Starting SPEI Web Interface...
    cd /d "%SPEI_HOME%\frontend"
    start /B "SPEI-Web" "%NODE_HOME%\npx.cmd" serve -s dist -l 3000
)

:: Wait for frontend to be ready
set FRONTEND_RETRIES=0
:wait_frontend
timeout /t 2 /nobreak >nul
curl -f http://localhost:3000 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    set /a FRONTEND_RETRIES+=1
    if !FRONTEND_RETRIES! LSS 10 goto wait_frontend
    echo WARNING: Frontend may not be ready, opening browser anyway...
)

:: Open web browser
echo Opening SPEI Medical System...
start http://localhost:3000

echo.

:: GUI Error Dialog Function
:show_error_dialog
set "title=%~1"
set "message=%~2"
powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('%message%', '%title%', 'OK', 'Error')" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo %title%: %message%
)
goto :eof

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
