@echo off
setlocal enabledelayedexpansion

call "%~dp0progress-indicator.bat" "Inicializando Banco de Dados" "6" "8" "Configurando PostgreSQL"

echo ========================================
echo SPEI Database Initialization
echo ========================================

:: Set environment variables
set "SPEI_HOME=%~dp0.."
set "POSTGRES_HOME=%SPEI_HOME%\runtime\postgresql"
set "PGDATA=%SPEI_HOME%\data\postgres"
set "PGUSER=postgres"
set "PGPORT=5432"

echo SPEI Home: %SPEI_HOME%
echo PostgreSQL Home: %POSTGRES_HOME%
echo Data Directory: %PGDATA%
echo.

:: Check if PostgreSQL runtime exists
if not exist "%POSTGRES_HOME%\bin\postgres.exe" (
    call "%~dp0error-handler.bat" "PostgreSQL Runtime" "PostgreSQL não encontrado em %POSTGRES_HOME%" "Execute o download do PostgreSQL primeiro"
    exit /b 1
)

:: Create data directory if it doesn't exist
if not exist "%PGDATA%" (
    echo Creating PostgreSQL data directory...
    mkdir "%PGDATA%" 2>nul
    if !ERRORLEVEL! NEQ 0 (
        call "%~dp0error-handler.bat" "Directory Creation" "Falha ao criar diretório de dados %PGDATA%" "Verifique permissões e execute como Administrador"
        exit /b 1
    )
)

:: Initialize database cluster if not already initialized
if not exist "%PGDATA%\postgresql.conf" (
    echo Initializing PostgreSQL database cluster...
    "%POSTGRES_HOME%\bin\initdb.exe" -D "%PGDATA%" -U postgres --auth-local=trust --auth-host=md5
    if !ERRORLEVEL! NEQ 0 (
        call "%~dp0error-handler.bat" "Database Initialization" "Falha ao inicializar cluster PostgreSQL" "Verifique permissões e espaço em disco"
        exit /b 1
    )
    echo ✓ Database cluster initialized successfully
) else (
    echo ✓ Database cluster already exists
)

:: Start PostgreSQL server
echo Starting PostgreSQL server...
"%POSTGRES_HOME%\bin\pg_ctl.exe" -D "%PGDATA%" -l "%PGDATA%\postgresql.log" start
if !ERRORLEVEL! NEQ 0 (
    call "%~dp0error-handler.bat" "PostgreSQL Server" "Falha ao iniciar servidor PostgreSQL" "Verifique o log em %PGDATA%\postgresql.log"
    exit /b 1
)

:: Wait for server to be ready
echo Waiting for PostgreSQL server to be ready...
timeout /t 5 /nobreak >nul

:: Test connection
"%POSTGRES_HOME%\bin\psql.exe" -U postgres -d postgres -c "SELECT version();" >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Cannot connect to PostgreSQL server!
    echo The server may not be ready yet or there may be a configuration issue.
    pause
    exit /b 1
)

:: Create SPEI database if it doesn't exist
echo Creating SPEI database...
"%POSTGRES_HOME%\bin\psql.exe" -U postgres -d postgres -c "SELECT 1 FROM pg_database WHERE datname='spei';" | findstr /C:"1 row" >nul
if !ERRORLEVEL! NEQ 0 (
    "%POSTGRES_HOME%\bin\psql.exe" -U postgres -d postgres -c "CREATE DATABASE spei OWNER postgres;"
    if !ERRORLEVEL! NEQ 0 (
        echo ERROR: Failed to create SPEI database!
        pause
        exit /b 1
    )
    echo ✓ SPEI database created successfully
) else (
    echo ✓ SPEI database already exists
)

:: Run database migrations if backend is available
if exist "%SPEI_HOME%\app\backend\alembic.ini" (
    echo Running database migrations...
    cd /d "%SPEI_HOME%\app\backend"
    "%SPEI_HOME%\runtime\python\python.exe" -m alembic upgrade head
    if !ERRORLEVEL! NEQ 0 (
        echo WARNING: Database migrations failed!
        echo The database structure may be incomplete.
        echo You can run migrations manually later.
        pause
    ) else (
        echo ✓ Database migrations completed successfully
    )
    cd /d "%SPEI_HOME%"
)

echo.
echo ========================================
echo Database initialization completed!
echo ========================================
echo.
echo PostgreSQL server is running on port %PGPORT%
echo Database: spei
echo User: postgres
echo.
echo To stop the database server, use stop-services.bat
echo.
pause
