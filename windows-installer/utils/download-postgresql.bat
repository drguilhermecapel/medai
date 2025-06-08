@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Downloading PostgreSQL 15.7 Portable
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

:: Download PostgreSQL portable
if not exist "%RUNTIME_DIR%\postgresql" (
    echo Downloading PostgreSQL 15.7...
    
    :: Try primary PostgreSQL download
    set "POSTGRES_URL=https://get.enterprisedb.com/postgresql/postgresql-15.7-1-windows-x64-binaries.zip"
    set "POSTGRES_ALT_URL2=https://ftp.postgresql.org/pub/binary/v15.7/win32/postgresql-15.7-1-windows-x64-binaries.zip"
    
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
    
    if %POWERSHELL_AVAILABLE% EQU 1 (
        powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%POSTGRES_ALT_URL2%' -OutFile '%TEMP_DIR%\postgresql.zip' -UseBasicParsing -TimeoutSec 600 } catch { exit 1 }"
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\postgresql.zip" goto :postgres_verify
    ) else (
        certutil -urlcache -split -f "%POSTGRES_ALT_URL2%" "%TEMP_DIR%\postgresql.zip" >nul 2>&1
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\postgresql.zip" goto :postgres_verify
        
        bitsadmin /transfer "PostgreSQLAltDownload" /download /priority normal "%POSTGRES_ALT_URL2%" "%TEMP_DIR%\postgresql.zip" >nul 2>&1
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\postgresql.zip" goto :postgres_verify
    )
    
    goto :postgres_download_failed
    
    :postgres_verify
    :: Verify PostgreSQL download was successful
    if not exist "%TEMP_DIR%\postgresql.zip" (
        echo ERROR: PostgreSQL zip file was not downloaded successfully!
        echo File path: %TEMP_DIR%\postgresql.zip
        goto :postgres_download_failed
    )
    
    :: Check PostgreSQL file size (should be around 200MB)
    for %%A in ("%TEMP_DIR%\postgresql.zip") do set "pgfilesize=%%~zA"
    if %pgfilesize% LSS 100000000 (
        echo ERROR: PostgreSQL zip file is too small (%pgfilesize% bytes). Expected ~200MB.
        echo This indicates a partial or corrupted download.
        del "%TEMP_DIR%\postgresql.zip" 2>nul
        goto :postgres_download_failed
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
        exit /b 1
    )
    
    move "%TEMP_DIR%\pgsql" "%RUNTIME_DIR%\postgresql"
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to move PostgreSQL to runtime directory!
        echo Attempting cleanup...
        if exist "%TEMP_DIR%\pgsql" rmdir /S /Q "%TEMP_DIR%\pgsql" 2>nul
        if exist "%TEMP_DIR%\postgresql.zip" del "%TEMP_DIR%\postgresql.zip" 2>nul
        exit /b 1
    )
    
    :: Verify PostgreSQL installation
    if not exist "%RUNTIME_DIR%\postgresql\bin\postgres.exe" (
        echo ERROR: PostgreSQL executable not found after installation!
        echo Expected: %RUNTIME_DIR%\postgresql\bin\postgres.exe
        exit /b 1
    )
    
    echo ✓ PostgreSQL installation completed and verified successfully!
    goto :postgres_done
    
    :postgres_download_failed
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
    exit /b 1
    
    :postgres_done
) else (
    echo ✓ PostgreSQL already installed
)

:: Cleanup
if exist "%TEMP_DIR%\postgresql.zip" del "%TEMP_DIR%\postgresql.zip" 2>nul

echo PostgreSQL download utility completed successfully!
exit /b 0
