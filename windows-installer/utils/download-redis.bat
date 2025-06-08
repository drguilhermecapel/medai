@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Downloading Redis for Windows
echo ========================================

set "SCRIPT_DIR=%~dp0"
set "RUNTIME_DIR=%SCRIPT_DIR%..\runtime"
set "TEMP_DIR=%SCRIPT_DIR%..\temp"

:: Create directories
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Check PowerShell availability
powershell -Command "Get-Host" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "POWERSHELL_AVAILABLE=1"
    echo ✓ PowerShell detected
) else (
    set "POWERSHELL_AVAILABLE=0"
    echo ⚠ PowerShell not detected - using alternative methods
)

:: Download Redis
if not exist "%RUNTIME_DIR%\redis" (
    echo Downloading Redis 5.0.14...
    
    :: Try Redis download with retry logic
    set "REDIS_URL=https://github.com/microsoftarchive/redis/releases/download/win-3.0.504/Redis-x64-3.0.504.zip"
    
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
    exit /b 0

:redis_done
) else (
    echo ✓ Redis already installed
)

:: Cleanup
if exist "%TEMP_DIR%\redis.zip" del "%TEMP_DIR%\redis.zip" 2>nul

echo Redis download utility completed successfully!
exit /b 0
