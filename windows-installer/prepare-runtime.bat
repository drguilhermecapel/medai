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
echo Environment Diagnostics
echo ========================================
echo Windows Version:
ver
echo.
echo PowerShell Version:
powershell -Command "try { $PSVersionTable.PSVersion } catch { Write-Host 'PowerShell not available or restricted' }"
echo.
echo PowerShell Execution Policy:
powershell -Command "try { Get-ExecutionPolicy } catch { Write-Host 'Cannot determine execution policy' }"
echo.
echo Network Connectivity Test:
echo Testing connection to nodejs.org...
powershell -Command "try { Test-NetConnection -ComputerName nodejs.org -Port 443 -InformationLevel Quiet } catch { Write-Host 'Network test failed or unavailable' }"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Network connection to nodejs.org successful
) else (
    echo ✗ Network connection to nodejs.org failed
    echo This may indicate firewall or proxy restrictions
)
echo.
echo Testing connection to github.com...
powershell -Command "try { Test-NetConnection -ComputerName github.com -Port 443 -InformationLevel Quiet } catch { Write-Host 'Network test failed or unavailable' }"
if %ERRORLEVEL% EQU 0 (
    echo ✓ Network connection to github.com successful
) else (
    echo ✗ Network connection to github.com failed
    echo This may indicate firewall or proxy restrictions
)
echo.
echo Current Directory: %~dp0
echo Runtime Directory: %RUNTIME_DIR%
echo Temp Directory: %TEMP_DIR%
echo.
echo ========================================
echo Starting Component Downloads
echo ========================================
echo.
echo ========================================
echo Downloading Python 3.11 Embeddable
echo ========================================

:: Download Python embeddable
if not exist "%RUNTIME_DIR%\python" (
    echo Downloading Python 3.11.9 embeddable...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip' -OutFile '%TEMP_DIR%\python.zip'"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to download Python embeddable!
        pause
        exit /b 1
    )
    
    echo Extracting Python...
    powershell -Command "Expand-Archive -Path '%TEMP_DIR%\python.zip' -DestinationPath '%RUNTIME_DIR%\python' -Force"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to extract Python embeddable!
        pause
        exit /b 1
    )
    
    :: Download get-pip.py
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%RUNTIME_DIR%\python\get-pip.py'"
    
    :: Configure Python embeddable to enable site-packages
    echo Configuring Python embeddable...
    echo python311.zip > "%RUNTIME_DIR%\python\python311._pth"
    echo . >> "%RUNTIME_DIR%\python\python311._pth"
    echo .\Lib >> "%RUNTIME_DIR%\python\python311._pth"
    echo .\Lib\site-packages >> "%RUNTIME_DIR%\python\python311._pth"
    echo import site >> "%RUNTIME_DIR%\python\python311._pth"
    
    :: Install pip
    echo Installing pip...
    "%RUNTIME_DIR%\python\python.exe" "%RUNTIME_DIR%\python\get-pip.py"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install pip!
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Downloading Node.js
echo ========================================

:: Download Node.js
if not exist "%RUNTIME_DIR%\nodejs" (
    echo Downloading Node.js 18.20.3...
    
    :: Multiple download strategies for Node.js
    set "NODEJS_URL=https://nodejs.org/dist/v18.20.3/node-v18.20.3-win-x64.zip"
    set "NODEJS_ALT_URL=https://github.com/nodejs/node/releases/download/v18.20.3/node-v18.20.3-win-x64.zip"
    set "NODEJS_MIRROR_URL=https://unofficial-builds.nodejs.org/download/release/v18.20.3/node-v18.20.3-win-x64.zip"
    
    echo Attempting Node.js download with multiple strategies...
    
    :: Strategy 1: PowerShell with enhanced error handling
    echo [1/4] Trying PowerShell download (primary source)...
    powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $response = Invoke-WebRequest -Uri '%NODEJS_URL%' -OutFile '%TEMP_DIR%\nodejs.zip' -UseBasicParsing -TimeoutSec 600 -PassThru; Write-Host 'Download completed. Size:' $response.Headers.'Content-Length' } catch { Write-Host 'PowerShell download failed:' $_.Exception.Message; exit 1 }"
    
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\nodejs.zip" goto :nodejs_verify
    
    :: Strategy 2: Alternative PowerShell source
    echo [2/4] Trying PowerShell download (GitHub source)...
    powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%NODEJS_ALT_URL%' -OutFile '%TEMP_DIR%\nodejs.zip' -UseBasicParsing -TimeoutSec 600 } catch { Write-Host 'GitHub download failed:' $_.Exception.Message; exit 1 }"
    
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\nodejs.zip" goto :nodejs_verify
    
    :: Strategy 3: certutil download
    echo [3/4] Trying certutil download...
    certutil -urlcache -split -f "%NODEJS_URL%" "%TEMP_DIR%\nodejs.zip" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\nodejs.zip" goto :nodejs_verify
    
    :: Strategy 4: bitsadmin download
    echo [4/4] Trying bitsadmin download...
    bitsadmin /transfer "NodeJSDownload" /download /priority normal "%NODEJS_URL%" "%TEMP_DIR%\nodejs.zip" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\nodejs.zip" goto :nodejs_verify
    
    :: All strategies failed
    goto :nodejs_download_failed
    
    :nodejs_verify
    echo Verifying Node.js download...
    
    :: Check if file exists and has reasonable size
    if not exist "%TEMP_DIR%\nodejs.zip" (
        echo ERROR: Node.js zip file does not exist after download!
        goto :nodejs_download_failed
    )
    
    :: Check file size (should be around 29MB)
    for %%A in ("%TEMP_DIR%\nodejs.zip") do set "filesize=%%~zA"
    if %filesize% LSS 20000000 (
        echo ERROR: Node.js zip file is too small (%filesize% bytes). Expected ~29MB.
        echo This indicates a partial or corrupted download.
        del "%TEMP_DIR%\nodejs.zip" 2>nul
        goto :nodejs_download_failed
    )
    
    echo Node.js download verified successfully (%filesize% bytes)
    goto :nodejs_extract
    
    :nodejs_download_failed
    echo.
    echo ========================================
    echo ERROR: Failed to download Node.js!
    echo ========================================
    echo.
    echo All download methods failed. This may be due to:
    echo 1. Network connectivity issues
    echo 2. Corporate firewall blocking downloads
    echo 3. Antivirus software blocking downloads
    echo 4. PowerShell execution policy restrictions
    echo.
    echo MANUAL SOLUTION:
    echo 1. Download Node.js manually from: https://nodejs.org/dist/v18.20.3/node-v18.20.3-win-x64.zip
    echo 2. Save the file as: %TEMP_DIR%\nodejs.zip
    echo 3. Re-run this script
    echo.
    echo File path: %TEMP_DIR%\nodejs.zip
    echo Expected size: ~29MB (30,000,000 bytes)
    echo.
    pause
    exit /b 1
    
    :nodejs_extract
    echo Extracting Node.js...
    
    :: Clean up any existing extraction directory
    if exist "%TEMP_DIR%\node-v18.20.3-win-x64" rmdir /S /Q "%TEMP_DIR%\node-v18.20.3-win-x64" 2>nul
    
    :: Extract with detailed error handling
    powershell -Command "try { Expand-Archive -Path '%TEMP_DIR%\nodejs.zip' -DestinationPath '%TEMP_DIR%' -Force; Write-Host 'Extraction completed successfully' } catch { Write-Host 'Extraction failed:' $_.Exception.Message; exit 1 }"
    
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to extract Node.js zip file!
        echo The zip file may be corrupted. Please try downloading again.
        pause
        exit /b 1
    )
    
    :: Verify extraction was successful
    if not exist "%TEMP_DIR%\node-v18.20.3-win-x64\node.exe" (
        echo ERROR: Node.js extraction incomplete! node.exe not found.
        pause
        exit /b 1
    )
    
    :: Move to final location
    if exist "%RUNTIME_DIR%\nodejs" rmdir /S /Q "%RUNTIME_DIR%\nodejs" 2>nul
    move "%TEMP_DIR%\node-v18.20.3-win-x64" "%RUNTIME_DIR%\nodejs"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to move Node.js to runtime directory!
        pause
        exit /b 1
    )
    
    echo Node.js installation completed successfully!
)

echo.
echo ========================================
echo Downloading PostgreSQL Portable
echo ========================================

:: Download PostgreSQL portable
if not exist "%RUNTIME_DIR%\postgresql" (
    echo Downloading PostgreSQL 15.7...
    
    :: Try primary PostgreSQL download
    set "POSTGRES_URL=https://get.enterprisedb.com/postgresql/postgresql-15.7-1-windows-x64-binaries.zip"
    set "POSTGRES_ALT_URL=https://sbp.enterprisedb.com/getfile.jsp?fileid=1258893"
    
    echo Attempting to download PostgreSQL from primary source...
    powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%POSTGRES_URL%' -OutFile '%TEMP_DIR%\postgresql.zip' -UseBasicParsing -TimeoutSec 600 } catch { exit 1 }"
    
    if %ERRORLEVEL% NEQ 0 (
        echo Primary PostgreSQL download failed, trying alternative approach...
        echo NOTE: PostgreSQL download may require manual intervention due to licensing requirements.
        echo Attempting alternative download...
        powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://ftp.postgresql.org/pub/binary/v15.7/win32/postgresql-15.7-1-windows-x64-binaries.zip' -OutFile '%TEMP_DIR%\postgresql.zip' -UseBasicParsing -TimeoutSec 600 } catch { exit 1 }"
        
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: Failed to download PostgreSQL from all sources!
            echo This may be due to:
            echo 1. Network connectivity issues
            echo 2. PostgreSQL download server restrictions
            echo 3. Corporate firewall blocking downloads
            echo.
            echo Please manually download PostgreSQL 15.7 Windows binaries and place in:
            echo %TEMP_DIR%\postgresql.zip
            echo.
            echo Download from: https://www.enterprisedb.com/download-postgresql-binaries
            pause
            exit /b 1
        )
    )
    
    :: Verify PostgreSQL download was successful
    if not exist "%TEMP_DIR%\postgresql.zip" (
        echo ERROR: PostgreSQL zip file was not downloaded successfully!
        echo File path: %TEMP_DIR%\postgresql.zip
        pause
        exit /b 1
    )
    
    echo Extracting PostgreSQL...
    powershell -Command "Expand-Archive -Path '%TEMP_DIR%\postgresql.zip' -DestinationPath '%TEMP_DIR%' -Force"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to extract PostgreSQL!
        pause
        exit /b 1
    )
    
    move "%TEMP_DIR%\pgsql" "%RUNTIME_DIR%\postgresql"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to move PostgreSQL to runtime directory!
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Downloading Redis for Windows
echo ========================================

:: Download Redis
if not exist "%RUNTIME_DIR%\redis" (
    echo Downloading Redis 5.0.14...
    
    :: Try Redis download with retry logic
    set "REDIS_URL=https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
    set "REDIS_ALT_URL=https://download.redis.io/redis-stable/src/redis-stable.tar.gz"
    
    echo Attempting to download Redis...
    powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%REDIS_URL%' -OutFile '%TEMP_DIR%\redis.zip' -UseBasicParsing -TimeoutSec 300 } catch { exit 1 }"
    
    if %ERRORLEVEL% NEQ 0 (
        echo Redis download failed. Redis is optional for basic functionality.
        echo Continuing without Redis...
        goto :skip_redis
    )
    
    :: Verify Redis download was successful
    if not exist "%TEMP_DIR%\redis.zip" (
        echo WARNING: Redis zip file was not downloaded successfully!
        echo Redis is optional, continuing without it...
        goto :skip_redis
    )
    
    echo Extracting Redis...
    powershell -Command "Expand-Archive -Path '%TEMP_DIR%\redis.zip' -DestinationPath '%RUNTIME_DIR%\redis' -Force"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to extract Redis!
        pause
        exit /b 1
    )
    goto :redis_done

:skip_redis
    echo Redis installation skipped - continuing without Redis support.
    echo Note: Some caching features may not be available.

:redis_done
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
if exist "%APP_DIR%\backend\requirements.txt" (
    echo Installing Python dependencies...
    "%RUNTIME_DIR%\python\python.exe" -m pip install --upgrade pip
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to upgrade pip!
        pause
        exit /b 1
    )
    
    "%RUNTIME_DIR%\python\python.exe" -m pip install -r "%APP_DIR%\backend\requirements.txt"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install Python dependencies!
        pause
        exit /b 1
    )
) else (
    echo WARNING: requirements.txt not found in backend directory!
    pause
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
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to download Visual C++ Redistributables!
        pause
        exit /b 1
    )
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
