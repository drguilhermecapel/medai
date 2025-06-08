@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Downloading Node.js 18.20.3
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

:: Download Node.js
if not exist "%RUNTIME_DIR%\nodejs" (
    echo Downloading Node.js 18.20.3...
    
    :: Multiple download strategies for Node.js
    set "NODEJS_URL=https://nodejs.org/dist/v18.20.3/node-v18.20.3-win-x64.zip"
    set "NODEJS_ALT_URL=https://github.com/nodejs/node/releases/download/v18.20.3/node-v18.20.3-win-x64.zip"
    
    echo Attempting Node.js download with multiple strategies...
    
    :: Strategy 1: PowerShell with enhanced error handling
    echo [1/4] Trying PowerShell download (primary source)...
    if %POWERSHELL_AVAILABLE% EQU 1 (
        powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; $response = Invoke-WebRequest -Uri '%NODEJS_URL%' -OutFile '%TEMP_DIR%\nodejs.zip' -UseBasicParsing -TimeoutSec 600 -PassThru; Write-Host 'Download completed. Size:' $response.Headers.'Content-Length' } catch { Write-Host 'PowerShell download failed:' $_.Exception.Message; exit 1 }"
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\nodejs.zip" goto :nodejs_verify
    )
    
    :: Strategy 2: Alternative PowerShell source
    echo [2/4] Trying PowerShell download (GitHub source)...
    if %POWERSHELL_AVAILABLE% EQU 1 (
        powershell -ExecutionPolicy Bypass -Command "try { $ProgressPreference = 'SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%NODEJS_ALT_URL%' -OutFile '%TEMP_DIR%\nodejs.zip' -UseBasicParsing -TimeoutSec 600 } catch { Write-Host 'GitHub download failed:' $_.Exception.Message; exit 1 }"
        if %ERRORLEVEL% EQU 0 if exist "%TEMP_DIR%\nodejs.zip" goto :nodejs_verify
    )
    
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
    exit /b 1
    
    :nodejs_extract
    echo Extracting Node.js...
    
    :: Clean up any existing extraction directory
    if exist "%TEMP_DIR%\node-v18.20.3-win-x64" rmdir /S /Q "%TEMP_DIR%\node-v18.20.3-win-x64" 2>nul
    
    :: Extract with detailed error handling
    if %POWERSHELL_AVAILABLE% EQU 1 (
        powershell -Command "try { Expand-Archive -Path '%TEMP_DIR%\nodejs.zip' -DestinationPath '%TEMP_DIR%' -Force; Write-Host 'Extraction completed successfully' } catch { Write-Host 'Extraction failed:' $_.Exception.Message; exit 1 }"
    ) else (
        :: Use built-in Windows extraction for older systems
        echo Using built-in extraction method...
        cd /d "%TEMP_DIR%"
        echo Set objShell = CreateObject("Shell.Application") > extract.vbs
        echo Set objFolder = objShell.NameSpace("%TEMP_DIR%") >> extract.vbs
        echo objFolder.CopyHere objShell.NameSpace("%TEMP_DIR%\nodejs.zip").Items, 16 >> extract.vbs
        cscript //nologo extract.vbs
        del extract.vbs
        cd /d "%~dp0"
    )
    
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to extract Node.js zip file!
        echo The zip file may be corrupted. Please try downloading again.
        exit /b 1
    )
    
    :: Verify extraction was successful
    if not exist "%TEMP_DIR%\node-v18.20.3-win-x64\node.exe" (
        echo ERROR: Node.js extraction incomplete! node.exe not found.
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
        exit /b 1
    )
    
    :: Verify Node.js installation
    if not exist "%RUNTIME_DIR%\nodejs\node.exe" (
        echo ERROR: Node.js executable not found after installation!
        echo Expected: %RUNTIME_DIR%\nodejs\node.exe
        exit /b 1
    )
    
    :: Test Node.js functionality
    "%RUNTIME_DIR%\nodejs\node.exe" --version >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Node.js installation is not functional!
        echo The executable exists but cannot run properly.
        exit /b 1
    )
    
    echo ✓ Node.js installation completed and verified successfully!
) else (
    echo ✓ Node.js already installed
)

:: Cleanup
if exist "%TEMP_DIR%\nodejs.zip" del "%TEMP_DIR%\nodejs.zip" 2>nul

echo Node.js download utility completed successfully!
exit /b 0
