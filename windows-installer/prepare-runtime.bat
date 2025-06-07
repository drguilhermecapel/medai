@echo off
echo Preparing SPEI runtime components for Windows installer...

set "RUNTIME_DIR=%~dp0runtime"
set "APP_DIR=%~dp0app"
set "TEMP_DIR=%~dp0temp"

:: Create directories
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%APP_DIR%" mkdir "%APP_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

echo.
echo ========================================
echo Downloading Python 3.11 Embeddable
echo ========================================

:: Download Python embeddable
if not exist "%RUNTIME_DIR%\python" (
    echo Downloading Python 3.11.9 embeddable...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%TEMP_DIR%\python.zip'"
    
    echo Extracting Python...
    powershell -Command "Expand-Archive -Path '%TEMP_DIR%\python.zip' -DestinationPath '%RUNTIME_DIR%\python' -Force"
    
    :: Download get-pip.py
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%RUNTIME_DIR%\python\get-pip.py'"
    
    :: Install pip
    echo Installing pip...
    "%RUNTIME_DIR%\python\python.exe" "%RUNTIME_DIR%\python\get-pip.py"
)

echo.
echo ========================================
echo Downloading Node.js
echo ========================================

:: Download Node.js
if not exist "%RUNTIME_DIR%\nodejs" (
    echo Downloading Node.js 18.20.3...
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v18.20.3/node-v18.20.3-win-x64.zip' -OutFile '%TEMP_DIR%\nodejs.zip'"
    
    echo Extracting Node.js...
    powershell -Command "Expand-Archive -Path '%TEMP_DIR%\nodejs.zip' -DestinationPath '%TEMP_DIR%' -Force"
    move "%TEMP_DIR%\node-v18.20.3-win-x64" "%RUNTIME_DIR%\nodejs"
)

echo.
echo ========================================
echo Downloading PostgreSQL Portable
echo ========================================

:: Download PostgreSQL portable
if not exist "%RUNTIME_DIR%\postgresql" (
    echo Downloading PostgreSQL 15.7...
    powershell -Command "Invoke-WebRequest -Uri 'https://get.enterprisedb.com/postgresql/postgresql-15.7-1-windows-x64-binaries.zip' -OutFile '%TEMP_DIR%\postgresql.zip'"
    
    echo Extracting PostgreSQL...
    powershell -Command "Expand-Archive -Path '%TEMP_DIR%\postgresql.zip' -DestinationPath '%TEMP_DIR%' -Force"
    move "%TEMP_DIR%\pgsql" "%RUNTIME_DIR%\postgresql"
)

echo.
echo ========================================
echo Downloading Redis for Windows
echo ========================================

:: Download Redis
if not exist "%RUNTIME_DIR%\redis" (
    echo Downloading Redis 5.0.14...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip' -OutFile '%TEMP_DIR%\redis.zip'"
    
    echo Extracting Redis...
    powershell -Command "Expand-Archive -Path '%TEMP_DIR%\redis.zip' -DestinationPath '%RUNTIME_DIR%\redis' -Force"
)

echo.
echo ========================================
echo Copying Application Files
echo ========================================

:: Copy backend
if exist "..\backend" (
    echo Copying backend files...
    xcopy "..\backend" "%APP_DIR%\backend" /E /I /Y /Q
) else (
    echo WARNING: Backend directory not found!
)

:: Copy frontend
if exist "..\frontend" (
    echo Copying frontend files...
    xcopy "..\frontend" "%APP_DIR%\frontend" /E /I /Y /Q
) else (
    echo WARNING: Frontend directory not found!
)

:: Copy other necessary files
if exist "..\docker-compose.yml" copy "..\docker-compose.yml" "%APP_DIR%\"
if exist "..\.env.example" copy "..\.env.example" "%APP_DIR%\"
if exist "..\README.md" copy "..\README.md" "%APP_DIR%\"

echo.
echo ========================================
echo Installing Python Dependencies
echo ========================================

:: Install Python dependencies in embedded Python
if exist "%APP_DIR%\backend\pyproject.toml" (
    echo Installing Poetry and dependencies...
    "%RUNTIME_DIR%\python\python.exe" -m pip install poetry
    
    cd /d "%APP_DIR%\backend"
    "%RUNTIME_DIR%\python\python.exe" -m poetry config virtualenvs.create false
    "%RUNTIME_DIR%\python\python.exe" -m poetry install --no-dev
    cd /d "%~dp0"
)

echo.
echo ========================================
echo Building Frontend
echo ========================================

:: Build frontend if package.json exists
if exist "%APP_DIR%\frontend\package.json" (
    echo Installing Node.js dependencies...
    cd /d "%APP_DIR%\frontend"
    "%RUNTIME_DIR%\nodejs\npm.cmd" install
    
    echo Building frontend...
    "%RUNTIME_DIR%\nodejs\npm.cmd" run build
    cd /d "%~dp0"
) else (
    echo Creating minimal frontend structure...
    mkdir "%APP_DIR%\frontend\dist"
    echo ^<html^>^<head^>^<title^>SPEI^</title^>^</head^>^<body^>^<h1^>SPEI Loading...^</h1^>^</body^>^</html^> > "%APP_DIR%\frontend\dist\index.html"
)

echo.
echo ========================================
echo Downloading Visual C++ Redistributables
echo ========================================

:: Download VC++ Redistributables
if not exist "%~dp0redist" mkdir "%~dp0redist"
if not exist "%~dp0redist\VC_redist.x64.exe" (
    echo Downloading Visual C++ Redistributables...
    powershell -Command "Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile '%~dp0redist\VC_redist.x64.exe'"
)

echo.
echo ========================================
echo Cleaning up temporary files
echo ========================================

if exist "%TEMP_DIR%" rmdir /S /Q "%TEMP_DIR%"

echo.
echo ========================================
echo Runtime preparation completed!
echo ========================================
echo.
echo Components prepared:
echo - Python 3.11 Embeddable: %RUNTIME_DIR%\python
echo - Node.js 18: %RUNTIME_DIR%\nodejs  
echo - PostgreSQL 15: %RUNTIME_DIR%\postgresql
echo - Redis: %RUNTIME_DIR%\redis
echo - Application: %APP_DIR%
echo - VC++ Redist: redist\VC_redist.x64.exe
echo.
echo Ready to build installer!
echo.
