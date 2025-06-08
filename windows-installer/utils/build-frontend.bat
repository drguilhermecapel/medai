@echo off
setlocal enabledelayedexpansion

call "%~dp0progress-indicator.bat" "Construindo Interface Web" "8" "8" "Finalizando instalação"

echo ========================================
echo SPEI Frontend Build Process
echo ========================================

:: Set environment variables
set "SPEI_HOME=%~dp0.."
set "NODEJS_HOME=%SPEI_HOME%\runtime\nodejs"
set "FRONTEND_DIR=%SPEI_HOME%\app\frontend"

echo SPEI Home: %SPEI_HOME%
echo Node.js Home: %NODEJS_HOME%
echo Frontend Directory: %FRONTEND_DIR%
echo.

:: Check if Node.js runtime exists
if not exist "%NODEJS_HOME%\node.exe" (
    call "%~dp0error-handler.bat" "Node.js Runtime" "Node.js não encontrado em %NODEJS_HOME%" "Execute o download do Node.js primeiro"
    exit /b 1
)

:: Check if frontend directory exists
if not exist "%FRONTEND_DIR%" (
    call "%~dp0error-handler.bat" "Frontend Files" "Diretório frontend não encontrado em %FRONTEND_DIR%" "Verifique se os arquivos da aplicação foram instalados corretamente"
    exit /b 1
)

:: Check if package.json exists
if not exist "%FRONTEND_DIR%\package.json" (
    call "%~dp0error-handler.bat" "Package Configuration" "package.json não encontrado em %FRONTEND_DIR%" "Arquivo de configuração necessário para build do frontend"
    exit /b 1
)

:: Set Node.js environment
set "PATH=%NODEJS_HOME%;%PATH%"
set "NODE_ENV=production"

:: Verify Node.js and npm are available
echo Checking Node.js installation...
"%NODEJS_HOME%\node.exe" --version
if !ERRORLEVEL! NEQ 0 (
    call "%~dp0error-handler.bat" "Node.js Verification" "Node.js não está funcionando corretamente" "Verifique a instalação do Node.js"
    exit /b 1
)

echo Checking npm installation...
"%NODEJS_HOME%\npm.cmd" --version
if !ERRORLEVEL! NEQ 0 (
    call "%~dp0error-handler.bat" "NPM Verification" "npm não está funcionando corretamente" "Verifique a instalação do npm"
    exit /b 1
)

:: Change to frontend directory
cd /d "%FRONTEND_DIR%"

:: Clean previous installations
if exist "node_modules" (
    echo Cleaning previous node_modules...
    rmdir /s /q "node_modules" 2>nul
)

if exist "dist" (
    echo Cleaning previous build...
    rmdir /s /q "dist" 2>nul
)

:: Install dependencies
echo Installing Node.js dependencies...
"%NODEJS_HOME%\npm.cmd" install --production=false --no-audit --no-fund
if !ERRORLEVEL! NEQ 0 (
    call "%~dp0error-handler.bat" "Node.js Dependencies" "Falha ao instalar dependências Node.js" "Verifique conectividade com internet e arquivo package.json"
    exit /b 1
)

:: Run type checking
echo Running TypeScript type checking...
"%NODEJS_HOME%\npm.cmd" run type-check
if !ERRORLEVEL! NEQ 0 (
    echo WARNING: TypeScript type checking failed!
    echo Continuing with build process...
)

:: Build the frontend
echo Building frontend for production...
"%NODEJS_HOME%\npm.cmd" run build
if !ERRORLEVEL! NEQ 0 (
    call "%~dp0error-handler.bat" "Frontend Build" "Falha ao construir aplicação frontend" "Verifique erros de TypeScript e dependências"
    exit /b 1
)

:: Verify build output
if not exist "dist" (
    call "%~dp0error-handler.bat" "Build Output" "Build concluído mas diretório dist não foi criado" "Verifique se o processo de build foi executado corretamente"
    exit /b 1
)

if not exist "dist\index.html" (
    call "%~dp0error-handler.bat" "Build Verification" "Build concluído mas index.html não foi gerado" "Verifique configuração do build do frontend"
    exit /b 1
)

:: Check build size
echo Checking build output...
for /f %%i in ('dir /s /b "dist\*.*" ^| find /c /v ""') do set "file_count=%%i"
echo ✓ Build contains %file_count% files

:: Return to SPEI home directory
cd /d "%SPEI_HOME%"

echo.
echo ========================================
echo Frontend build completed successfully!
echo ========================================
echo.
echo The frontend has been built and is ready for production.
echo Build output is available in: %FRONTEND_DIR%\dist
echo.
pause
