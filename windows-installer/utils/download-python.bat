@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Downloading Python 3.11 Embeddable
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
        exit /b 1
    )
    
    echo ✓ Python installation completed and verified successfully!
) else (
    echo ✓ Python already installed
)

:: Cleanup
if exist "%TEMP_DIR%\python.zip" del "%TEMP_DIR%\python.zip" 2>nul

echo Python download utility completed successfully!
exit /b 0
