@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Error Handler Utility
echo ========================================

:: This utility provides centralized error handling for the SPEI installer
:: Usage: call error-handler.bat "component_name" "error_message" "suggested_solution"

set "COMPONENT=%~1"
set "ERROR_MSG=%~2"
set "SOLUTION=%~3"

if "%COMPONENT%"=="" (
    echo ERROR: Component name not provided to error handler
    exit /b 1
)

if "%ERROR_MSG%"=="" (
    echo ERROR: Error message not provided to error handler
    exit /b 1
)

echo.
echo ========================================
echo INSTALLATION ERROR DETECTED
echo ========================================
echo Component: %COMPONENT%
echo Error: %ERROR_MSG%
echo.
if not "%SOLUTION%"=="" (
    echo Suggested Solution:
    echo %SOLUTION%
    echo.
)
echo Common Solutions:
echo 1. Check your internet connection
echo 2. Run installer as Administrator
echo 3. Temporarily disable antivirus/firewall
echo 4. Ensure sufficient disk space (minimum 2GB)
echo 5. Close other applications that might interfere
echo.
echo Technical Support:
echo - Email: suporte@spei.med.br
echo - Documentation: https://spei.med.br/docs
echo.
echo The installer will attempt to continue with other components...
echo ========================================
echo.

:: Log the error for support purposes
set "LOG_FILE=%TEMP%\SPEI-Installer-Errors.log"
echo [%DATE% %TIME%] ERROR in %COMPONENT%: %ERROR_MSG% >> "%LOG_FILE%"

exit /b 0
