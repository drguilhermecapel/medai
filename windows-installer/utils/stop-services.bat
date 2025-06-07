@echo off
echo Stopping SPEI services...

:: Stop web processes
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq SPEI-*" 2>nul
taskkill /F /IM "node.exe" /FI "WINDOWTITLE eq SPEI-*" 2>nul

:: Stop PostgreSQL
set "SPEI_HOME=%~dp0.."
set "POSTGRES_HOME=%SPEI_HOME%\runtime\postgresql"
set "PGDATA=%SPEI_HOME%\data\postgres"

if exist "%PGDATA%\postmaster.pid" (
    echo Stopping PostgreSQL...
    "%POSTGRES_HOME%\bin\pg_ctl.exe" -D "%PGDATA%" stop -m fast
)

:: Stop Redis
taskkill /F /IM "redis-server.exe" 2>nul

echo SPEI services stopped.
