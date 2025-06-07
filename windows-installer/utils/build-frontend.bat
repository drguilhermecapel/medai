@echo off
echo Building SPEI frontend...

set "SPEI_HOME=%~dp0.."
set "NODE_HOME=%SPEI_HOME%\runtime\nodejs"

:: Set PATH
set "PATH=%NODE_HOME%;%PATH%"

:: Build frontend
if exist "%SPEI_HOME%\frontend\package.json" (
    echo Building frontend...
    cd /d "%SPEI_HOME%\frontend"
    npm install
    npm run build
    echo Frontend build completed!
) else (
    echo Frontend package.json not found, creating minimal structure...
    mkdir "%SPEI_HOME%\frontend\dist"
    echo ^<html^>^<head^>^<title^>SPEI^</title^>^</head^>^<body^>^<h1^>SPEI Loading...^</h1^>^</body^>^</html^> > "%SPEI_HOME%\frontend\dist\index.html"
    echo Minimal frontend structure created!
)
