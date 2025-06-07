@echo off
echo Initializing SPEI database...

set "SPEI_HOME=%~dp0.."
set "PYTHON_HOME=%SPEI_HOME%\runtime\python"
set "POSTGRES_HOME=%SPEI_HOME%\runtime\postgresql"
set "PGDATA=%SPEI_HOME%\data\postgres"

:: Set PATH
set "PATH=%PYTHON_HOME%;%PYTHON_HOME%\Scripts;%POSTGRES_HOME%\bin;%PATH%"

:: Create data directory
if not exist "%SPEI_HOME%\data" mkdir "%SPEI_HOME%\data"
if not exist "%PGDATA%" mkdir "%PGDATA%"

:: Initialize PostgreSQL database
echo Initializing PostgreSQL database...
"%POSTGRES_HOME%\bin\initdb.exe" -D "%PGDATA%" -U postgres --auth-local=trust --auth-host=md5

:: Start PostgreSQL temporarily
echo Starting PostgreSQL...
start /B "PostgreSQL-Init" "%POSTGRES_HOME%\bin\pg_ctl.exe" -D "%PGDATA%" -l "%SPEI_HOME%\data\postgres-init.log" start

:: Wait for PostgreSQL to start
timeout /t 10 /nobreak >nul

:: Create database and user
echo Creating SPEI database...
"%POSTGRES_HOME%\bin\createdb.exe" -U postgres spei_db
"%POSTGRES_HOME%\bin\psql.exe" -U postgres -d spei_db -c "CREATE USER spei WITH PASSWORD 'spei_password';"
"%POSTGRES_HOME%\bin\psql.exe" -U postgres -d spei_db -c "GRANT ALL PRIVILEGES ON DATABASE spei_db TO spei;"

:: Stop temporary PostgreSQL
echo Stopping temporary PostgreSQL...
"%POSTGRES_HOME%\bin\pg_ctl.exe" -D "%PGDATA%" stop

echo Database initialization completed!
