@echo off
setlocal enabledelayedexpansion

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
    echo ERROR: Node.js runtime not found at %NODEJS_HOME%
    echo Please run prepare-runtime.bat first to download Node.js.
    pause
    exit /b 1
)

:: Check if frontend directory exists
if not exist "%FRONTEND_DIR%" (
    echo ERROR: Frontend directory not found at %FRONTEND_DIR%
    echo Please ensure the application files are properly installed.
    pause
    exit /b 1
)

:: Check if package.json exists
if not exist "%FRONTEND_DIR%\package.json" (
    echo ERROR: package.json not found in %FRONTEND_DIR%
    echo Cannot build frontend without package configuration.
    pause
    exit /b 1
)

:: Set Node.js environment
set "PATH=%NODEJS_HOME%;%PATH%"
set "NODE_ENV=production"

:: Verify Node.js and npm are available
echo Checking Node.js installation...
"%NODEJS_HOME%\node.exe" --version
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: Node.js is not working properly!
    pause
    exit /b 1
)

echo Checking npm installation...
"%NODEJS_HOME%\npm.cmd" --version
if !ERRORLEVEL! NEQ 0 (
    echo ERROR: npm is not working properly!
    pause
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
    echo ERROR: Failed to install Node.js dependencies!
    echo.
    echo This could be due to:
    echo - Network connectivity issues
    echo - Incompatible package versions
    echo - Missing system dependencies
    echo.
    echo Please check the error messages above and try again.
    pause
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
    echo ERROR: Frontend build failed!
    echo.
    echo Please check the error messages above for details.
    echo Common issues:
    echo - TypeScript compilation errors
    echo - Missing dependencies
    echo - Build configuration problems
    echo.
    pause
    exit /b 1
)

:: Verify build output
if not exist "dist" (
    echo ERROR: Build completed but dist directory was not created!
    pause
    exit /b 1
)

if not exist "dist\index.html" (
    echo ERROR: Build completed but index.html was not generated!
    pause
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
