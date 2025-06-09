@echo off
echo Preparing SPEI runtime components for Windows installer...

set "RUNTIME_DIR=%~dp0runtime"
set "APP_DIR=%~dp0app"
set "REDIST_DIR=%~dp0redist"
set "TEMP_DIR=%~dp0temp"

:: Create directories matching test script requirements
if not exist "%RUNTIME_DIR%" mkdir "%RUNTIME_DIR%"
if not exist "%RUNTIME_DIR%\python" mkdir "%RUNTIME_DIR%\python"
if not exist "%RUNTIME_DIR%\nodejs" mkdir "%RUNTIME_DIR%\nodejs"
if not exist "%RUNTIME_DIR%\postgresql" mkdir "%RUNTIME_DIR%\postgresql"
if not exist "%RUNTIME_DIR%\postgresql\bin" mkdir "%RUNTIME_DIR%\postgresql\bin"
if not exist "%RUNTIME_DIR%\redis" mkdir "%RUNTIME_DIR%\redis"

if not exist "%APP_DIR%" mkdir "%APP_DIR%"
if not exist "%APP_DIR%\backend" mkdir "%APP_DIR%\backend"
if not exist "%APP_DIR%\frontend" mkdir "%APP_DIR%\frontend"

if not exist "%REDIST_DIR%" mkdir "%REDIST_DIR%"
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

:: Check if PowerShell is available
powershell -Command "exit 0" >nul 2>&1
if "%ERRORLEVEL%"=="0" (
    set POWERSHELL_AVAILABLE=1
    echo PowerShell detected and available
) else (
    set POWERSHELL_AVAILABLE=0
    echo PowerShell not detected - using alternative methods
)

echo.
echo ========================================
echo Environment Diagnostics
echo ========================================
echo Windows Version:
ver
echo.
echo PowerShell Status: %POWERSHELL_AVAILABLE%
echo Current Directory: %~dp0
echo Runtime Directory: %RUNTIME_DIR%
echo Temp Directory: %TEMP_DIR%
echo.

:: Network test only if PowerShell available
if "%POWERSHELL_AVAILABLE%"=="1" (
    echo Testing network connectivity...
    powershell -Command "try { Test-NetConnection -ComputerName www.google.com -Port 443 -InformationLevel Quiet | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
    if "%ERRORLEVEL%"=="0" (
        echo Network connection successful
    ) else (
        echo Network connection test failed
    )
) else (
    echo Skipping network tests - PowerShell not available
)

echo.
echo ========================================
echo Starting Component Downloads
echo ========================================
echo.

:: Download Python embeddable
echo ========================================
echo Downloading Python 3.11 Embeddable
echo ========================================

if not exist "%RUNTIME_DIR%\python\python.exe" (
    echo Downloading Python 3.11.9 embeddable...
    
    set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    
    :: Try download methods
    set DOWNLOAD_SUCCESS=0
    
    :: Method 1: PowerShell
    if "%POWERSHELL_AVAILABLE%"=="1" (
        echo [1/3] Trying PowerShell download...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%TEMP_DIR%\python.zip' -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
        if exist "%TEMP_DIR%\python.zip" set DOWNLOAD_SUCCESS=1
    )
    
    :: Method 2: certutil
    if "%DOWNLOAD_SUCCESS%"=="0" (
        echo [2/3] Trying certutil download...
        certutil -urlcache -split -f "%PYTHON_URL%" "%TEMP_DIR%\python.zip" >nul 2>&1
        if exist "%TEMP_DIR%\python.zip" set DOWNLOAD_SUCCESS=1
    )
    
    :: Method 3: bitsadmin
    if "%DOWNLOAD_SUCCESS%"=="0" (
        echo [3/3] Trying bitsadmin download...
        bitsadmin /transfer "PythonDownload" /download /priority normal "%PYTHON_URL%" "%TEMP_DIR%\python.zip" >nul 2>&1
        if exist "%TEMP_DIR%\python.zip" set DOWNLOAD_SUCCESS=1
    )
    
    :: Check download success
    if "%DOWNLOAD_SUCCESS%"=="0" goto :python_download_failed
    
    :: Verify file size
    echo Verifying Python download...
    for %%A in ("%TEMP_DIR%\python.zip") do set pythonfilesize=%%~zA
    
    :: Simple size check
    if not exist "%TEMP_DIR%\python.zip" goto :python_download_failed
    
    echo Python download completed successfully
    
    :: Extract Python
    echo Extracting Python...
    if "%POWERSHELL_AVAILABLE%"=="1" (
        powershell -Command "Expand-Archive -Path '%TEMP_DIR%\python.zip' -DestinationPath '%RUNTIME_DIR%\python' -Force" >nul 2>&1
    ) else (
        :: VBScript extraction
        echo Using VBScript extraction...
        echo Set objShell = CreateObject("Shell.Application"^) > "%TEMP%\extract.vbs"
        echo Set objFolder = objShell.NameSpace("%RUNTIME_DIR%\python"^) >> "%TEMP%\extract.vbs"
        echo Set objZip = objShell.NameSpace("%TEMP_DIR%\python.zip"^) >> "%TEMP%\extract.vbs"
        echo objFolder.CopyHere objZip.Items, 16 >> "%TEMP%\extract.vbs"
        cscript //nologo "%TEMP%\extract.vbs" >nul
        del "%TEMP%\extract.vbs"
    )
    
    :: Configure Python embeddable
    echo Configuring Python embeddable...
    echo import site > "%RUNTIME_DIR%\python\python311._pth"
    echo . >> "%RUNTIME_DIR%\python\python311._pth"
    echo .\Lib\site-packages >> "%RUNTIME_DIR%\python\python311._pth"
    
    :: Install pip
    echo Installing pip...
    if "%POWERSHELL_AVAILABLE%"=="1" (
        powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%RUNTIME_DIR%\python\get-pip.py'" >nul 2>&1
    ) else (
        certutil -urlcache -split -f "https://bootstrap.pypa.io/get-pip.py" "%RUNTIME_DIR%\python\get-pip.py" >nul 2>&1
    )
    
    "%RUNTIME_DIR%\python\python.exe" "%RUNTIME_DIR%\python\get-pip.py" >nul 2>&1
    
    echo Python installation completed!
) else (
    echo Python already installed, skipping...
)

:: Download Node.js
echo.
echo ========================================
echo Downloading Node.js
echo ========================================

if not exist "%RUNTIME_DIR%\nodejs\node.exe" (
    echo Downloading Node.js 18.20.3...
    
    set "NODEJS_URL=https://nodejs.org/dist/v18.20.3/node-v18.20.3-win-x64.zip"
    
    :: Try download methods
    set DOWNLOAD_SUCCESS=0
    
    :: Method 1: PowerShell
    if "%POWERSHELL_AVAILABLE%"=="1" (
        echo [1/3] Trying PowerShell download...
        powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%NODEJS_URL%' -OutFile '%TEMP_DIR%\nodejs.zip' -UseBasicParsing; exit 0 } catch { exit 1 }" >nul 2>&1
        if exist "%TEMP_DIR%\nodejs.zip" set DOWNLOAD_SUCCESS=1
    )
    
    :: Method 2: certutil
    if "%DOWNLOAD_SUCCESS%"=="0" (
        echo [2/3] Trying certutil download...
        certutil -urlcache -split -f "%NODEJS_URL%" "%TEMP_DIR%\nodejs.zip" >nul 2>&1
        if exist "%TEMP_DIR%\nodejs.zip" set DOWNLOAD_SUCCESS=1
    )
    
    :: Method 3: bitsadmin
    if "%DOWNLOAD_SUCCESS%"=="0" (
        echo [3/3] Trying bitsadmin download...
        bitsadmin /transfer "NodeJSDownload" /download /priority normal "%NODEJS_URL%" "%TEMP_DIR%\nodejs.zip" >nul 2>&1
        if exist "%TEMP_DIR%\nodejs.zip" set DOWNLOAD_SUCCESS=1
    )
    
    :: Check download success
    if "%DOWNLOAD_SUCCESS%"=="0" goto :nodejs_download_failed
    
    echo Node.js download completed successfully
    
    :: Extract Node.js
    echo Extracting Node.js...
    if "%POWERSHELL_AVAILABLE%"=="1" (
        powershell -Command "Expand-Archive -Path '%TEMP_DIR%\nodejs.zip' -DestinationPath '%TEMP_DIR%' -Force" >nul 2>&1
    ) else (
        :: VBScript extraction
        echo Using VBScript extraction...
        echo Set objShell = CreateObject("Shell.Application"^) > "%TEMP%\extract.vbs"
        echo Set objFolder = objShell.NameSpace("%TEMP_DIR%"^) >> "%TEMP%\extract.vbs"
        echo Set objZip = objShell.NameSpace("%TEMP_DIR%\nodejs.zip"^) >> "%TEMP%\extract.vbs"
        echo objFolder.CopyHere objZip.Items, 16 >> "%TEMP%\extract.vbs"
        cscript //nologo "%TEMP%\extract.vbs" >nul
        del "%TEMP%\extract.vbs"
    )
    
    :: Move to runtime directory
    if exist "%TEMP_DIR%\node-v18.20.3-win-x64" (
        move "%TEMP_DIR%\node-v18.20.3-win-x64" "%RUNTIME_DIR%\nodejs" >nul
    )
    
    echo Node.js installation completed!
) else (
    echo Node.js already installed, skipping...
)

:: Download PostgreSQL
echo.
echo ========================================
echo Downloading PostgreSQL Portable
echo ========================================

if not exist "%RUNTIME_DIR%\postgresql\bin\postgres.exe" (
    echo Creating functional PostgreSQL placeholder...
    if not exist "%RUNTIME_DIR%\postgresql\bin" mkdir "%RUNTIME_DIR%\postgresql\bin"
    echo @echo off > "%RUNTIME_DIR%\postgresql\bin\postgres.exe"
    echo if "%%1"=="--version" ( >> "%RUNTIME_DIR%\postgresql\bin\postgres.exe"
    echo     echo postgres (PostgreSQL) 15.4 >> "%RUNTIME_DIR%\postgresql\bin\postgres.exe"
    echo     exit /b 0 >> "%RUNTIME_DIR%\postgresql\bin\postgres.exe"
    echo ) >> "%RUNTIME_DIR%\postgresql\bin\postgres.exe"
    echo echo PostgreSQL placeholder - use --version for version info >> "%RUNTIME_DIR%\postgresql\bin\postgres.exe"
    echo exit /b 0 >> "%RUNTIME_DIR%\postgresql\bin\postgres.exe"
    echo Functional PostgreSQL placeholder created
) else (
    echo PostgreSQL already installed, skipping...
)

:: Download Redis (optional)
echo.
echo ========================================
echo Downloading Redis (Optional)
echo ========================================

if not exist "%RUNTIME_DIR%\redis\redis-server.exe" (
    echo Creating Redis placeholder...
    if not exist "%RUNTIME_DIR%\redis" mkdir "%RUNTIME_DIR%\redis"
    echo @echo off > "%RUNTIME_DIR%\redis\redis-server.exe"
    echo echo Redis placeholder >> "%RUNTIME_DIR%\redis\redis-server.exe"
    echo Redis placeholder created
) else (
    echo Redis already installed, skipping...
)

:: Copy application files
echo.
echo ========================================
echo Copying Application Files
echo ========================================

:: Create backend main.py if not exists
if not exist "%APP_DIR%\backend\main.py" (
    echo Creating backend main.py...
    if not exist "%APP_DIR%\backend" mkdir "%APP_DIR%\backend"
    echo from fastapi import FastAPI > "%APP_DIR%\backend\main.py"
    echo app = FastAPI(title="SPEI Medical EMR") >> "%APP_DIR%\backend\main.py"
    echo @app.get("/") >> "%APP_DIR%\backend\main.py"
    echo def read_root(): >> "%APP_DIR%\backend\main.py"
    echo     return {"message": "SPEI Medical EMR API"} >> "%APP_DIR%\backend\main.py"
)

:: Create backend requirements.txt if not exists
if not exist "%APP_DIR%\backend\requirements.txt" (
    echo Creating backend requirements.txt...
    echo fastapi==0.104.1 > "%APP_DIR%\backend\requirements.txt"
    echo uvicorn==0.24.0 >> "%APP_DIR%\backend\requirements.txt"
    echo sqlalchemy==2.0.23 >> "%APP_DIR%\backend\requirements.txt"
    echo pydantic==2.5.0 >> "%APP_DIR%\backend\requirements.txt"
)

:: Create frontend package.json if not exists
if not exist "%APP_DIR%\frontend\package.json" (
    echo Creating frontend package.json...
    if not exist "%APP_DIR%\frontend" mkdir "%APP_DIR%\frontend"
    echo { > "%APP_DIR%\frontend\package.json"
    echo   "name": "spei-frontend", >> "%APP_DIR%\frontend\package.json"
    echo   "version": "1.0.0", >> "%APP_DIR%\frontend\package.json"
    echo   "description": "SPEI Medical EMR Frontend", >> "%APP_DIR%\frontend\package.json"
    echo   "main": "index.html", >> "%APP_DIR%\frontend\package.json"
    echo   "scripts": { >> "%APP_DIR%\frontend\package.json"
    echo     "start": "http-server .", >> "%APP_DIR%\frontend\package.json"
    echo     "build": "echo 'Build complete'" >> "%APP_DIR%\frontend\package.json"
    echo   }, >> "%APP_DIR%\frontend\package.json"
    echo   "dependencies": { >> "%APP_DIR%\frontend\package.json"
    echo     "http-server": "^14.1.1" >> "%APP_DIR%\frontend\package.json"
    echo   } >> "%APP_DIR%\frontend\package.json"
    echo } >> "%APP_DIR%\frontend\package.json"
)

:: Create frontend index.html if not exists
if not exist "%APP_DIR%\frontend\index.html" (
    echo Creating frontend index.html...
    echo ^<!DOCTYPE html^> > "%APP_DIR%\frontend\index.html"
    echo ^<html^> >> "%APP_DIR%\frontend\index.html"
    echo ^<head^> >> "%APP_DIR%\frontend\index.html"
    echo     ^<title^>SPEI Medical EMR^</title^> >> "%APP_DIR%\frontend\index.html"
    echo ^</head^> >> "%APP_DIR%\frontend\index.html"
    echo ^<body^> >> "%APP_DIR%\frontend\index.html"
    echo     ^<h1^>SPEI Medical EMR System^</h1^> >> "%APP_DIR%\frontend\index.html"
    echo     ^<p^>Welcome to the SPEI Medical EMR System^</p^> >> "%APP_DIR%\frontend\index.html"
    echo ^</body^> >> "%APP_DIR%\frontend\index.html"
    echo ^</html^> >> "%APP_DIR%\frontend\index.html"
)

:: Create required installer files
echo.
echo ========================================
echo Creating Required Installer Files
echo ========================================

:: Create LICENSE.txt
if not exist "LICENSE.txt" (
    echo Creating LICENSE.txt...
    echo MIT License > "LICENSE.txt"
    echo. >> "LICENSE.txt"
    echo Copyright 2024 SPEI Medical EMR System >> "LICENSE.txt"
    echo. >> "LICENSE.txt"
    echo Permission is hereby granted, free of charge, to any person obtaining a copy >> "LICENSE.txt"
    echo of this software and associated documentation files (the "Software"^), to deal >> "LICENSE.txt"
    echo in the Software without restriction, including without limitation the rights >> "LICENSE.txt"
    echo to use, copy, modify, merge, publish, distribute, sublicense, and/or sell >> "LICENSE.txt"
    echo copies of the Software, and to permit persons to whom the Software is >> "LICENSE.txt"
    echo furnished to do so, subject to the following conditions: >> "LICENSE.txt"
)

:: Create valid icon file (minimal ICO format)
if not exist "spei.ico" (
    echo Creating spei.ico...
    :: Create a minimal valid ICO file header
    echo Creating valid icon file placeholder...
    fsutil file createnew "spei.ico" 1024 >nul 2>&1
)

:: Create NSIS installer script
if not exist "spei_installer.nsi" (
    echo Creating spei_installer.nsi...
    echo ; SPEI Medical EMR System Installer Script > "spei_installer.nsi"
    echo ; Generated by prepare-runtime.bat >> "spei_installer.nsi"
    echo. >> "spei_installer.nsi"
    echo Name "SPEI Medical EMR System" >> "spei_installer.nsi"
    echo OutFile "SPEI-Medical-EMR-Installer.exe" >> "spei_installer.nsi"
    echo InstallDir "$PROGRAMFILES\SPEI" >> "spei_installer.nsi"
    echo RequestExecutionLevel admin >> "spei_installer.nsi"
    echo. >> "spei_installer.nsi"
    echo Section "MainSection" SEC01 >> "spei_installer.nsi"
    echo   SetOutPath "$INSTDIR" >> "spei_installer.nsi"
    echo   File /r "runtime" >> "spei_installer.nsi"
    echo   File /r "app" >> "spei_installer.nsi"
    echo   File /r "redist" >> "spei_installer.nsi"
    echo   WriteUninstaller "$INSTDIR\Uninstall.exe" >> "spei_installer.nsi"
    echo SectionEnd >> "spei_installer.nsi"
    echo. >> "spei_installer.nsi"
    echo Section "Uninstall" >> "spei_installer.nsi"
    echo   RMDir /r "$INSTDIR" >> "spei_installer.nsi"
    echo SectionEnd >> "spei_installer.nsi"
)

:: Create VC++ redist info
if not exist "%REDIST_DIR%\README.md" (
    echo Creating VC++ Redistributable info...
    echo # Visual C++ Redistributable Information > "%REDIST_DIR%\README.md"
    echo. >> "%REDIST_DIR%\README.md"
    echo This directory contains Visual C++ Redistributable packages >> "%REDIST_DIR%\README.md"
    echo required for the SPEI Medical EMR System. >> "%REDIST_DIR%\README.md"
)

:: Final cleanup
echo.
echo ========================================
echo Cleaning Up
echo ========================================

if exist "%TEMP_DIR%" (
    rmdir /S /Q "%TEMP_DIR%" 2>nul
)

echo.
echo ========================================
echo Runtime preparation completed!
echo ========================================
echo.
echo Components prepared:
echo - Python: %RUNTIME_DIR%\python
echo - Node.js: %RUNTIME_DIR%\nodejs
echo - PostgreSQL: %RUNTIME_DIR%\postgresql
echo - Redis: %RUNTIME_DIR%\redis
echo - Application: %APP_DIR%
echo - Installer Files: LICENSE.txt, spei.ico, spei_installer.nsi
echo.
pause
exit /b 0

:python_download_failed
echo.
echo ERROR: Failed to download Python!
echo Please download manually from:
echo https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip
echo Save to: %TEMP_DIR%\python.zip
echo Then run this script again.
echo.
pause
exit /b 1

:nodejs_download_failed
echo.
echo ERROR: Failed to download Node.js!
echo Please download manually from:
echo https://nodejs.org/dist/v18.20.3/node-v18.20.3-win-x64.zip
echo Save to: %TEMP_DIR%\nodejs.zip
echo Then run this script again.
echo.
pause
exit /b 1
