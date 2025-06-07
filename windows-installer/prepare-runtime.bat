@echo off
echo Preparing SPEI runtime components for Windows installer...

set "RUNTIME_DIR=%~dp0runtime"
set "APP_DIR=%~dp0app"
set "TEMP_DIR=%~dp0temp"

:: Create directories
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%APP_DIR%" mkdir "%APP_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Check if PowerShell is available
:check_powershell
where powershell >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "POWERSHELL_AVAILABLE=1"
    echo ✓ PowerShell detected and available
) else (
    set "POWERSHELL_AVAILABLE=0"
    echo ⚠ PowerShell not detected - using alternative methods
)
goto :eof

echo.
echo ========================================
echo Environment Diagnostics
echo ========================================
call :check_powershell

if %POWERSHELL_AVAILABLE% EQU 0 (
    echo.
    echo ========================================
    echo PowerShell Not Detected
    echo ========================================
    echo PowerShell is not available on this system.
    echo The installer will use alternative download methods.
    echo.
    echo For optimal performance, consider installing PowerShell:
    echo https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows
    echo.
    echo Alternative download methods will be used:
    echo - certutil (Windows built-in)
    echo - bitsadmin (Windows built-in)
    echo - VBScript extraction (for older systems)
    echo.
    echo Continuing with alternative methods...
    echo ========================================
    echo.
)

echo Windows Version:
ver
echo.
echo PowerShell Status:
if %POWERSHELL_AVAILABLE% EQU 1 (
    powershell -Command "try { $PSVersionTable.PSVersion } catch { Write-Host 'PowerShell restricted' }"
    echo PowerShell Execution Policy:
    powershell -Command "try { Get-ExecutionPolicy } catch { Write-Host 'Cannot determine execution policy' }"
) else (
    echo PowerShell not available - using alternative download methods
)
echo.
echo Network Connectivity Test:
if %POWERSHELL_AVAILABLE% EQU 1 (
    echo Testing connection to nodejs.org...
    powershell -Command "try { Test-NetConnection -ComputerName nodejs.org -Port 443 -InformationLevel Quiet } catch { Write-Host 'Network test failed' }"
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Network connection to nodejs.org successful
    ) else (
        echo ✗ Network connection to nodejs.org failed
        echo This may indicate firewall or proxy restrictions
    )
    
    echo Testing connection to github.com...
    powershell -Command "try { Test-NetConnection -ComputerName github.com -Port 443 -InformationLevel Quiet } catch { Write-Host 'Network test failed' }"
    if %ERRORLEVEL% EQU 0 (
        echo ✓ Network connection to github.com successful
    ) else (
        echo ✗ Network connection to github.com failed
        echo This may indicate firewall or proxy restrictions
    )
) else (
    echo Skipping network connectivity tests (PowerShell not available)
    echo Will attempt downloads using alternative methods
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
    
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    
    :: Strategy 1: PowerShell (if available)
    if %POWERSHELL_AVAILABLE% EQU 1 (
        echo [1/3] Trying PowerShell download...
        powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%TEMP_DIR%\python.zip' -UseBasicParsing -TimeoutSec 600 } catch { exit 1 }"
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\python.zip" goto :python_verify
    )
    
    :: Strategy 2: certutil download
    echo [2/3] Trying certutil download...
    certutil -urlcache -split -f "%PYTHON_URL%" "%TEMP_DIR%\python.zip" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\python.zip" goto :python_verify
    
    :: Strategy 3: bitsadmin download
    echo [3/3] Trying bitsadmin download...
    bitsadmin /transfer "PythonDownload" /download /priority normal "%PYTHON_URL%" "%TEMP_DIR%\python.zip" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\python.zip" goto :python_verify
    
    :: All strategies failed
    goto :python_download_failed
    
    :python_verify
    echo Verifying Python download...
    if not exist "%TEMP_DIR%\python.zip" goto :python_download_failed
    
    :: Check file size (should be around 9MB)
    for %%A in ("%TEMP_DIR%\python.zip") do set "pythonfilesize=%%~zA"
    if %pythonfilesize% LSS 5000000 (
        echo ERROR: Python zip file is too small (%pythonfilesize% bytes). Expected ~9MB.
        del "%TEMP_DIR%\python.zip" 2>nul
        goto :python_download_failed
    )
    
    echo Python download verified successfully (%pythonfilesize% bytes)
    goto :python_extract
    
    :python_download_failed
    echo ERROR: Failed to download Python embeddable!
    echo MANUAL SOLUTION:
    echo 1. Download Python manually from: %PYTHON_URL%
    echo 2. Save the file as: %TEMP_DIR%\python.zip
    echo 3. Re-run this script
    pause
    exit /b 1
    
    :python_extract
    echo Extracting Python...
    if %POWERSHELL_AVAILABLE% EQU 1 (
        powershell -Command "Expand-Archive -Path '%TEMP_DIR%\python.zip' -DestinationPath '%RUNTIME_DIR%\python' -Force"
    ) else (
        :: Use built-in Windows extraction for older systems
        echo Using built-in extraction method...
        if not exist "%RUNTIME_DIR%\python" mkdir "%RUNTIME_DIR%\python"
        cd /d "%TEMP_DIR%"
        echo Set objShell = CreateObject("Shell.Application") > extract.vbs
        echo Set objFolder = objShell.NameSpace("%RUNTIME_DIR%\python") >> extract.vbs
        echo objFolder.CopyHere objShell.NameSpace("%TEMP_DIR%\python.zip").Items, 16 >> extract.vbs
        cscript //nologo extract.vbs
        del extract.vbs
        cd /d "%~dp0"
    )
    
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to extract Python embeddable!
        pause
        exit /b 1
    )
    
    :: Download get-pip.py using same fallback strategy
    echo Downloading get-pip.py...
    if %POWERSHELL_AVAILABLE% EQU 1 (
        powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%RUNTIME_DIR%\python\get-pip.py'"
    ) else (
        certutil -urlcache -split -f "https://bootstrap.pypa.io/get-pip.py" "%RUNTIME_DIR%\python\get-pip.py" >nul 2>&1
    )
    
    if %ERRORLEVEL% NEQ 0 (
        echo WARNING: Failed to download get-pip.py automatically
        echo You may need to install pip manually later
    )
    
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
        echo Attempting cleanup...
        if exist "%TEMP_DIR%\node-v18.20.3-win-x64" rmdir /S /Q "%TEMP_DIR%\node-v18.20.3-win-x64" 2>nul
        if exist "%TEMP_DIR%\nodejs.zip" del "%TEMP_DIR%\nodejs.zip" 2>nul
        pause
        exit /b 1
    )
    
    :: Verify Node.js installation
    if not exist "%RUNTIME_DIR%\nodejs\node.exe" (
        echo ERROR: Node.js executable not found after installation!
        echo Expected: %RUNTIME_DIR%\nodejs\node.exe
        pause
        exit /b 1
    )
    
    :: Test Node.js functionality
    "%RUNTIME_DIR%\nodejs\node.exe" --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Node.js installation is not functional!
        echo The executable exists but cannot run properly.
        pause
        exit /b 1
    )
    
    echo ✓ Node.js installation completed and verified successfully!
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
    
    :: Strategy 1: PowerShell (if available)
    if %POWERSHELL_AVAILABLE% EQU 1 (
        echo [1/3] Trying PowerShell download...
        powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%POSTGRES_URL%' -OutFile '%TEMP_DIR%\postgresql.zip' -UseBasicParsing -TimeoutSec 600 } catch { exit 1 }"
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\postgresql.zip" goto :postgres_verify
    )
    
    :: Strategy 2: certutil download
    echo [2/3] Trying certutil download...
    certutil -urlcache -split -f "%POSTGRES_URL%" "%TEMP_DIR%\postgresql.zip" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\postgresql.zip" goto :postgres_verify
    
    :: Strategy 3: bitsadmin download
    echo [3/3] Trying bitsadmin download...
    bitsadmin /transfer "PostgreSQLDownload" /download /priority normal "%POSTGRES_URL%" "%TEMP_DIR%\postgresql.zip" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\postgresql.zip" goto :postgres_verify
    
    :: Primary source failed, try alternative
    echo Primary PostgreSQL download failed, trying alternative approach...
    echo NOTE: PostgreSQL download may require manual intervention due to licensing requirements.
    echo Attempting alternative download...
    
    set "POSTGRES_ALT_URL2=https://ftp.postgresql.org/pub/binary/v15.7/win32/postgresql-15.7-1-windows-x64-binaries.zip"
    
    if %POWERSHELL_AVAILABLE% EQU 1 (
        powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%POSTGRES_ALT_URL2%' -OutFile '%TEMP_DIR%\postgresql.zip' -UseBasicParsing -TimeoutSec 600 } catch { exit 1 }"
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\postgresql.zip" goto :postgres_verify
    ) else (
        certutil -urlcache -split -f "%POSTGRES_ALT_URL2%" "%TEMP_DIR%\postgresql.zip" >nul 2>&1
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\postgresql.zip" goto :postgres_verify
        
        bitsadmin /transfer "PostgreSQLAltDownload" /download /priority normal "%POSTGRES_ALT_URL2%" "%TEMP_DIR%\postgresql.zip" >nul 2>&1
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\postgresql.zip" goto :postgres_verify
    )
    
    :postgres_verify
        
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
    
    :: Check PostgreSQL file size (should be around 200MB)
    for %%A in ("%TEMP_DIR%\postgresql.zip") do set "pgfilesize=%%~zA"
    if %pgfilesize% LSS 100000000 (
        echo ERROR: PostgreSQL zip file is too small (%pgfilesize% bytes). Expected ~200MB.
        echo This indicates a partial or corrupted download.
        del "%TEMP_DIR%\postgresql.zip" 2>nul
        echo.
        echo ======================================== 
        echo ERROR: PostgreSQL download failed!
        echo.
        echo MANUAL SOLUTION:
        echo 1. Download PostgreSQL manually from: https://www.enterprisedb.com/download-postgresql-binaries
        echo 2. Save the file as: %TEMP_DIR%\postgresql.zip
        echo 3. Re-run this script
        echo ======================================== 
        pause
        exit /b 1
    )
    echo ✓ PostgreSQL download verified (%pgfilesize% bytes)
    
    echo Extracting PostgreSQL...
    if %POWERSHELL_AVAILABLE% EQU 1 (
        powershell -Command "Expand-Archive -Path '%TEMP_DIR%\postgresql.zip' -DestinationPath '%TEMP_DIR%' -Force"
    ) else (
        :: Use built-in Windows extraction for older systems
        echo Using built-in extraction method...
        cd /d "%TEMP_DIR%"
        echo Set objShell = CreateObject("Shell.Application") > extract_pg.vbs
        echo Set objFolder = objShell.NameSpace("%TEMP_DIR%") >> extract_pg.vbs
        echo objFolder.CopyHere objShell.NameSpace("%TEMP_DIR%\postgresql.zip").Items, 16 >> extract_pg.vbs
        cscript //nologo extract_pg.vbs
        del extract_pg.vbs
        cd /d "%~dp0"
    )
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to extract PostgreSQL!
        pause
        exit /b 1
    )
    
    move "%TEMP_DIR%\pgsql" "%RUNTIME_DIR%\postgresql"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to move PostgreSQL to runtime directory!
        echo Attempting cleanup...
        if exist "%TEMP_DIR%\pgsql" rmdir /S /Q "%TEMP_DIR%\pgsql" 2>nul
        if exist "%TEMP_DIR%\postgresql.zip" del "%TEMP_DIR%\postgresql.zip" 2>nul
        pause
        exit /b 1
    )
    
    :: Verify PostgreSQL installation
    if not exist "%RUNTIME_DIR%\postgresql\bin\postgres.exe" (
        echo ERROR: PostgreSQL executable not found after installation!
        echo Expected: %RUNTIME_DIR%\postgresql\bin\postgres.exe
        pause
        exit /b 1
    )
    
    echo ✓ PostgreSQL installation completed and verified successfully!
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
    
    :: Strategy 1: PowerShell (if available)
    if %POWERSHELL_AVAILABLE% EQU 1 (
        echo [1/3] Trying PowerShell download...
        powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%REDIS_URL%' -OutFile '%TEMP_DIR%\redis.zip' -UseBasicParsing -TimeoutSec 300 } catch { exit 1 }"
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\redis.zip" goto :redis_verify_download
    )
    
    :: Strategy 2: certutil download
    echo [2/3] Trying certutil download...
    certutil -urlcache -split -f "%REDIS_URL%" "%TEMP_DIR%\redis.zip" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\redis.zip" goto :redis_verify_download
    
    :: Strategy 3: bitsadmin download
    echo [3/3] Trying bitsadmin download...
    bitsadmin /transfer "RedisDownload" /download /priority normal "%REDIS_URL%" "%TEMP_DIR%\redis.zip" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\redis.zip" goto :redis_verify_download
    
    :: All strategies failed
    echo Redis download failed. Redis is optional for basic functionality.
    echo Continuing without Redis...
    goto :skip_redis
    
    :redis_verify_download
    
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
    
    :: Check Redis file size (should be around 5MB)
    for %%A in ("%TEMP_DIR%\redis.zip") do set "redisfilesize=%%~zA"
    if %redisfilesize% LSS 1000000 (
        echo WARNING: Redis zip file is too small (%redisfilesize% bytes). Expected ~5MB.
        echo This indicates a partial or corrupted download.
        del "%TEMP_DIR%\redis.zip" 2>nul
        echo Redis is optional, continuing without it...
        goto :skip_redis
    )
    echo ✓ Redis download verified (%redisfilesize% bytes)
    
    echo Extracting Redis...
    if %POWERSHELL_AVAILABLE% EQU 1 (
        powershell -Command "Expand-Archive -Path '%TEMP_DIR%\redis.zip' -DestinationPath '%RUNTIME_DIR%\redis' -Force"
    ) else (
        :: Use built-in Windows extraction for older systems
        echo Using built-in extraction method...
        if not exist "%RUNTIME_DIR%\redis" mkdir "%RUNTIME_DIR%\redis"
        cd /d "%TEMP_DIR%"
        echo Set objShell = CreateObject("Shell.Application") > extract_redis.vbs
        echo Set objFolder = objShell.NameSpace("%RUNTIME_DIR%\redis") >> extract_redis.vbs
        echo objFolder.CopyHere objShell.NameSpace("%TEMP_DIR%\redis.zip").Items, 16 >> extract_redis.vbs
        cscript //nologo extract_redis.vbs
        del extract_redis.vbs
        cd /d "%~dp0"
    )
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to extract Redis!
        echo Attempting cleanup...
        if exist "%TEMP_DIR%\redis.zip" del "%TEMP_DIR%\redis.zip" 2>nul
        if exist "%RUNTIME_DIR%\redis" rmdir /S /Q "%RUNTIME_DIR%\redis" 2>nul
        echo Redis is optional, continuing without it...
        goto :skip_redis
    )
    
    :: Verify Redis installation
    if not exist "%RUNTIME_DIR%\redis\redis-server.exe" (
        echo WARNING: Redis executable not found after extraction!
        echo Redis is optional, continuing without it...
        goto :skip_redis
    )
    
    echo ✓ Redis installation completed and verified successfully!
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
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to copy backend files!
        echo Source: ..\backend
        echo Destination: %APP_DIR%\backend
        pause
        exit /b 1
    )
    echo ✓ Backend files copied successfully
) else (
    echo ERROR: Backend directory not found!
    echo Expected location: ..\backend
    echo Please ensure you are running this script from the windows-installer directory.
    pause
    exit /b 1
)

:: Copy frontend
if exist "..\frontend" (
    echo Copying frontend files...
    xcopy "..\frontend" "%APP_DIR%\frontend" /E /I /Y /Q
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to copy frontend files!
        echo Source: ..\frontend
        echo Destination: %APP_DIR%\frontend
        pause
        exit /b 1
    )
    echo ✓ Frontend files copied successfully
) else (
    echo ERROR: Frontend directory not found!
    echo Expected location: ..\frontend
    echo Please ensure you are running this script from the windows-installer directory.
    pause
    exit /b 1
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
    
    :: Verify Python is functional
    "%RUNTIME_DIR%\python\python.exe" --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Python runtime is not functional!
        echo Please run prepare-runtime.bat again to reinstall Python.
        pause
        exit /b 1
    )
    
    "%RUNTIME_DIR%\python\python.exe" -m pip install --upgrade pip
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to upgrade pip!
        echo This may indicate Python embeddable configuration issues.
        echo Please check that python311._pth file exists and is configured correctly.
        pause
        exit /b 1
    )
    
    "%RUNTIME_DIR%\python\python.exe" -m pip install -r "%APP_DIR%\backend\requirements.txt"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install Python dependencies!
        echo.
        echo This could be due to:
        echo 1. Network connectivity issues
        echo 2. Missing system dependencies
        echo 3. Incompatible package versions
        echo 4. Python embeddable configuration problems
        echo.
        echo Please check the error messages above for specific details.
        pause
        exit /b 1
    )
    
    :: Verify critical packages are installed
    echo Verifying critical package installations...
    "%RUNTIME_DIR%\python\python.exe" -c "import fastapi, uvicorn, sqlalchemy" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Critical Python packages are not properly installed!
        echo The backend may not function correctly.
        pause
        exit /b 1
    )
    
    echo ✓ Python dependencies installed and verified successfully
) else (
    echo ERROR: requirements.txt not found in backend directory!
    echo Expected: %APP_DIR%\backend\requirements.txt
    echo Cannot proceed without Python dependencies list.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Building Frontend
echo ========================================

:: Build frontend if package.json exists
if exist "%APP_DIR%\frontend\package.json" (
    echo Installing Node.js dependencies...
    cd /d "%APP_DIR%\frontend"
    
    :: Verify Node.js and npm are functional
    "%RUNTIME_DIR%\nodejs\node.exe" --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Node.js is not functional!
        cd /d "%~dp0"
        pause
        exit /b 1
    )
    
    "%RUNTIME_DIR%\nodejs\npm.cmd" --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: npm is not functional!
        cd /d "%~dp0"
        pause
        exit /b 1
    )
    
    "%RUNTIME_DIR%\nodejs\npm.cmd" install
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to install Node.js dependencies!
        echo.
        echo This could be due to:
        echo 1. Network connectivity issues
        echo 2. Incompatible package versions
        echo 3. Missing system dependencies
        echo.
        echo Please check the error messages above for details.
        cd /d "%~dp0"
        pause
        exit /b 1
    )
    
    echo Building frontend...
    "%RUNTIME_DIR%\nodejs\npm.cmd" run build
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Frontend build failed!
        echo.
        echo Please check the error messages above for details.
        echo Common issues:
        echo 1. TypeScript compilation errors
        echo 2. Missing dependencies
        echo 3. Build configuration problems
        echo.
        cd /d "%~dp0"
        pause
        exit /b 1
    )
    
    :: Verify build output
    if not exist "dist\index.html" (
        echo ERROR: Frontend build completed but index.html was not generated!
        echo Expected: %APP_DIR%\frontend\dist\index.html
        cd /d "%~dp0"
        pause
        exit /b 1
    )
    
    echo ✓ Frontend built and verified successfully
    cd /d "%~dp0"
) else (
    echo ERROR: package.json not found in frontend directory!
    echo Expected: %APP_DIR%\frontend\package.json
    echo Cannot build frontend without package configuration.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Downloading Visual C++ Redistributables
echo ========================================

:: Download VC++ Redistributables
if not exist "%~dp0redist" mkdir "%~dp0redist"
if not exist "%~dp0redist\VC_redist.x64.exe" (
    echo Downloading Visual C++ Redistributables...
    
    set "VC_REDIST_URL=https://aka.ms/vs/17/release/vc_redist.x64.exe"
    
    :: Strategy 1: PowerShell (if available)
    if %POWERSHELL_AVAILABLE% EQU 1 (
        echo [1/3] Trying PowerShell download...
        powershell -Command "Invoke-WebRequest -Uri '%VC_REDIST_URL%' -OutFile '%~dp0redist\VC_redist.x64.exe'"
        if %ERRORLEVEL% EQU 0 if exist "%~dp0redist\VC_redist.x64.exe" goto :vc_redist_verify
    )
    
    :: Strategy 2: certutil download
    echo [2/3] Trying certutil download...
    certutil -urlcache -split -f "%VC_REDIST_URL%" "%~dp0redist\VC_redist.x64.exe" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%~dp0redist\VC_redist.x64.exe" goto :vc_redist_verify
    
    :: Strategy 3: bitsadmin download
    echo [3/3] Trying bitsadmin download...
    bitsadmin /transfer "VCRedistDownload" /download /priority normal "%VC_REDIST_URL%" "%~dp0redist\VC_redist.x64.exe" >nul 2>&1
    if %ERRORLEVEL% EQU 0 if exist "%~dp0redist\VC_redist.x64.exe" goto :vc_redist_verify
    
    :: All strategies failed
    echo ERROR: Failed to download Visual C++ Redistributables!
    echo.
    echo MANUAL SOLUTION:
    echo 1. Download VC++ Redistributables manually from: %VC_REDIST_URL%
    echo 2. Save the file as: %~dp0redist\VC_redist.x64.exe
    echo 3. Re-run this script
    pause
    exit /b 1
    
    :vc_redist_verify
    
    :: Verify VC++ Redistributables download
    if not exist "%~dp0redist\VC_redist.x64.exe" (
        echo ERROR: VC++ Redistributables file was not downloaded successfully!
        pause
        exit /b 1
    )
    
    :: Check file size (should be around 13MB)
    for %%A in ("%~dp0redist\VC_redist.x64.exe") do set "vcfilesize=%%~zA"
    if %vcfilesize% LSS 10000000 (
        echo ERROR: VC++ Redistributables file is too small (%vcfilesize% bytes). Expected ~13MB.
        echo This indicates a partial or corrupted download.
        del "%~dp0redist\VC_redist.x64.exe" 2>nul
        pause
        exit /b 1
    )
    
    echo ✓ Visual C++ Redistributables downloaded and verified (%vcfilesize% bytes)
)

echo.
echo ========================================
echo Final Verification and Cleanup
echo ========================================

:: Final verification of all components
echo Performing final component verification...

:: Verify Python runtime
if not exist "%RUNTIME_DIR%\python\python.exe" (
    echo ERROR: Python runtime verification failed!
    echo Missing: %RUNTIME_DIR%\python\python.exe
    pause
    exit /b 1
)

:: Verify Node.js runtime
if not exist "%RUNTIME_DIR%\nodejs\node.exe" (
    echo ERROR: Node.js runtime verification failed!
    echo Missing: %RUNTIME_DIR%\nodejs\node.exe
    pause
    exit /b 1
)

:: Verify PostgreSQL runtime
if not exist "%RUNTIME_DIR%\postgresql\bin\postgres.exe" (
    echo ERROR: PostgreSQL runtime verification failed!
    echo Missing: %RUNTIME_DIR%\postgresql\bin\postgres.exe
    pause
    exit /b 1
)

:: Verify application files
if not exist "%APP_DIR%\backend" (
    echo ERROR: Backend application files verification failed!
    echo Missing: %APP_DIR%\backend
    pause
    exit /b 1
)

if not exist "%APP_DIR%\frontend" (
    echo ERROR: Frontend application files verification failed!
    echo Missing: %APP_DIR%\frontend
    pause
    exit /b 1
)

:: Verify VC++ Redistributables
if not exist "%~dp0redist\VC_redist.x64.exe" (
    echo ERROR: VC++ Redistributables verification failed!
    echo Missing: %~dp0redist\VC_redist.x64.exe
    pause
    exit /b 1
)

echo ✓ All components verified successfully

echo Cleaning up temporary files...
if exist "%TEMP_DIR%" (
    rmdir /S /Q "%TEMP_DIR%" 2>nul
    if exist "%TEMP_DIR%" (
        echo WARNING: Could not completely clean temporary directory
        echo Some files may still exist in: %TEMP_DIR%
    ) else (
        echo ✓ Temporary files cleaned successfully
    )
)

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
