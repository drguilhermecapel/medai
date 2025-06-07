@echo off
setlocal enabledelayedexpansion

echo ========================================
echo SPEI First Run Setup
echo ========================================

set "SPEI_HOME=%~dp0.."
set "PYTHON_HOME=%SPEI_HOME%\runtime\python"
set "POSTGRES_HOME=%SPEI_HOME%\runtime\postgresql"
set "PGDATA=%SPEI_HOME%\data\postgres"

:: Set PATH
set "PATH=%PYTHON_HOME%;%PYTHON_HOME%\Scripts;%POSTGRES_HOME%\bin;%PATH%"

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

:: Install Python dependencies
echo Installing Python dependencies...
cd /d "%SPEI_HOME%\backend"
python -m pip install --upgrade pip
if exist "%SPEI_HOME%\backend\requirements.txt" (
    python -m pip install -r "%SPEI_HOME%\backend\requirements.txt"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install Python dependencies!
        pause
        exit /b 1
    )
) else (
    echo WARNING: requirements.txt not found!
    pause
)

:: Run database migrations
echo Running database migrations...
python -m alembic upgrade head

:: Create admin user
echo Creating admin user...
python -c "
import asyncio
import os
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

async def create_admin():
    db = next(get_db())
    admin_email = os.getenv('INITIAL_ADMIN_EMAIL', 'admin@spei.local')
    admin_password = os.getenv('INITIAL_ADMIN_PASSWORD', 'admin123')
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.email == admin_email).first()
    if not existing_admin:
        admin_user = User(
            email=admin_email,
            hashed_password=get_password_hash(admin_password),
            full_name='Administrator',
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
        print(f'Admin user created: {admin_email}')
    else:
        print('Admin user already exists')

asyncio.run(create_admin())
"

:: Build frontend
if exist "%SPEI_HOME%\frontend\package.json" (
    echo Building frontend...
    cd /d "%SPEI_HOME%\frontend"
    npm install
    npm run build
) else (
    echo Frontend package.json not found, skipping build...
)

:: Stop temporary PostgreSQL
echo Stopping temporary PostgreSQL...
"%POSTGRES_HOME%\bin\pg_ctl.exe" -D "%PGDATA%" stop

echo.
echo ========================================
echo First run setup completed successfully!
echo ========================================
echo.
