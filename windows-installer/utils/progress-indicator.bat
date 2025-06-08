@echo off
setlocal enabledelayedexpansion

echo ========================================
echo Progress Indicator Utility
echo ========================================

:: This utility provides visual progress feedback during installation
:: Usage: call progress-indicator.bat "step_name" "current_step" "total_steps" "status"

set "STEP_NAME=%~1"
set "CURRENT_STEP=%~2"
set "TOTAL_STEPS=%~3"
set "STATUS=%~4"

if "%STEP_NAME%"=="" (
    echo ERROR: Step name not provided to progress indicator
    exit /b 1
)

if "%CURRENT_STEP%"=="" set "CURRENT_STEP=1"
if "%TOTAL_STEPS%"=="" set "TOTAL_STEPS=10"
if "%STATUS%"=="" set "STATUS=Em progresso"

:: Calculate progress percentage
set /a "PROGRESS_PERCENT=(%CURRENT_STEP% * 100) / %TOTAL_STEPS%"

:: Create progress bar
set "PROGRESS_BAR="
set /a "FILLED_BARS=%PROGRESS_PERCENT% / 10"
set /a "EMPTY_BARS=10 - %FILLED_BARS%"

for /l %%i in (1,1,%FILLED_BARS%) do set "PROGRESS_BAR=!PROGRESS_BAR!█"
for /l %%i in (1,1,%EMPTY_BARS%) do set "PROGRESS_BAR=!PROGRESS_BAR!░"

echo.
echo ========================================
echo INSTALAÇÃO SPEI - PROGRESSO
echo ========================================
echo Etapa: %STEP_NAME%
echo Progresso: [%PROGRESS_BAR%] %PROGRESS_PERCENT%%%
echo Status: %STATUS%
echo Etapa %CURRENT_STEP% de %TOTAL_STEPS%
echo ========================================
echo.

exit /b 0
