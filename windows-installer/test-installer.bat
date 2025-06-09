@echo off
echo ========================================
echo SPEI Installer Test and Verification
echo ========================================
echo.

set "ERRORS=0"
set "WARNINGS=0"

REM Test 1: Check directory structure
echo [TEST 1] Checking directory structure...
if exist "runtime" (
    echo [PASS] runtime directory exists
) else (
    echo [FAIL] runtime directory missing
    set /a ERRORS+=1
)

if exist "app" (
    echo [PASS] app directory exists
) else (
    echo [FAIL] app directory missing
    set /a ERRORS+=1
)

if exist "redist" (
    echo [PASS] redist directory exists
) else (
    echo [FAIL] redist directory missing
    set /a ERRORS+=1
)

echo.

REM Test 2: Check runtime components
echo [TEST 2] Checking runtime components...
if exist "runtime\python\python.exe" (
    echo [PASS] Python runtime found
    "runtime\python\python.exe" --version 2>nul
    if errorlevel 1 (
        echo [WARN] Python may not be functional
        set /a WARNINGS+=1
    )
) else (
    echo [FAIL] Python runtime missing
    set /a ERRORS+=1
)

if exist "runtime\nodejs\node.exe" (
    echo [PASS] Node.js runtime found
    "runtime\nodejs\node.exe" --version 2>nul
    if errorlevel 1 (
        echo [WARN] Node.js may not be functional
        set /a WARNINGS+=1
    )
) else (
    echo [FAIL] Node.js runtime missing
    set /a ERRORS+=1
)

if exist "runtime\postgresql\bin\postgres.exe" (
    echo [PASS] PostgreSQL runtime found
    "runtime\postgresql\bin\postgres.exe" --version 2>nul
    if errorlevel 1 (
        echo [WARN] PostgreSQL may not be functional
        set /a WARNINGS+=1
    )
) else (
    echo [FAIL] PostgreSQL runtime missing
    set /a ERRORS+=1
)

if exist "runtime\redis\redis-server.exe" (
    echo [PASS] Redis runtime found (optional)
) else (
    echo [INFO] Redis runtime not installed (optional)
)

echo.

REM Test 3: Check application files
echo [TEST 3] Checking application files...
if exist "app\backend\main.py" (
    echo [PASS] Backend main.py found
) else (
    echo [FAIL] Backend main.py missing
    set /a ERRORS+=1
)

if exist "app\backend\requirements.txt" (
    echo [PASS] Backend requirements.txt found
) else (
    echo [WARN] Backend requirements.txt missing
    set /a WARNINGS+=1
)

if exist "app\frontend\package.json" (
    echo [PASS] Frontend package.json found
) else (
    echo [FAIL] Frontend package.json missing
    set /a ERRORS+=1
)

if exist "app\frontend\index.html" (
    echo [PASS] Frontend index.html found
) else (
    echo [WARN] Frontend index.html missing
    set /a WARNINGS+=1
)

echo.

REM Test 4: Check installer files
echo [TEST 4] Checking installer files...
if exist "spei_installer.nsi" (
    echo [PASS] NSIS script found
) else (
    echo [FAIL] NSIS script missing
    set /a ERRORS+=1
)

if exist "spei.ico" (
    echo [PASS] Icon file found
    for %%A in ("spei.ico") do (
        if %%~zA EQU 0 (
            echo [WARN] Icon file is empty
            set /a WARNINGS+=1
        )
    )
) else (
    echo [FAIL] Icon file missing
    set /a ERRORS+=1
)

if exist "LICENSE.txt" (
    echo [PASS] License file found
) else (
    echo [FAIL] License file missing
    set /a ERRORS+=1
)

echo.

REM Test 5: Check Python packages
echo [TEST 5] Checking Python packages...
if exist "runtime\python\python.exe" (
    "runtime\python\python.exe" -m pip list >nul 2>&1
    if errorlevel 1 (
        echo [WARN] pip not functional
        set /a WARNINGS+=1
    ) else (
        echo [PASS] pip is functional
        "runtime\python\python.exe" -c "import site; print('Site packages:', site.getsitepackages())" 2>nul
    )
) else (
    echo [SKIP] Python not available
)

echo.

REM Test 6: Check Node.js packages
echo [TEST 6] Checking Node.js packages...
if exist "runtime\nodejs\npm.cmd" (
    echo [PASS] npm found
    if exist "app\frontend\node_modules" (
        echo [PASS] Frontend dependencies installed
    ) else (
        echo [INFO] Frontend dependencies not yet installed
    )
) else (
    echo [FAIL] npm not found
    set /a ERRORS+=1
)

echo.

REM Test 7: Check for compiled installer
echo [TEST 7] Checking for compiled installer...
if exist "SPEI-System-Installer.exe" (
    echo [PASS] Compiled installer found
    for %%A in ("SPEI-System-Installer.exe") do echo       Size: %%~zA bytes
) else (
    echo [INFO] Compiled installer not yet created
)

echo.

REM Test 8: Port availability
echo [TEST 8] Checking port availability...
netstat -an | find ":8000" >nul
if errorlevel 1 (
    echo [PASS] Port 8000 (backend) is available
) else (
    echo [WARN] Port 8000 (backend) is in use
    set /a WARNINGS+=1
)

netstat -an | find ":3000" >nul
if errorlevel 1 (
    echo [PASS] Port 3000 (frontend) is available
) else (
    echo [WARN] Port 3000 (frontend) is in use
    set /a WARNINGS+=1
)

netstat -an | find ":5432" >nul
if errorlevel 1 (
    echo [PASS] Port 5432 (PostgreSQL) is available
) else (
    echo [WARN] Port 5432 (PostgreSQL) is in use
    set /a WARNINGS+=1
)

echo.

REM Summary
echo ========================================
echo Test Summary
echo ========================================
echo Total Errors: %ERRORS%
echo Total Warnings: %WARNINGS%
echo.

if %ERRORS% GTR 0 (
    echo RESULT: FAILED - %ERRORS% critical error(s) found
    echo.
    echo Please run prepare-runtime.bat to fix missing components.
) else (
    if %WARNINGS% GTR 0 (
        echo RESULT: PASSED WITH WARNINGS
        echo.
        echo The installer can be built, but some issues should be addressed.
    ) else (
        echo RESULT: PASSED
        echo.
        echo All tests passed! The installer is ready to be built.
    )
)

echo.

REM Provide quick fixes
if %ERRORS% GTR 0 (
    echo ========================================
    echo Quick Fix Suggestions
    echo ========================================
    
    if not exist "runtime" (
        echo - Run: prepare-runtime.bat
    )
    
    if not exist "spei_installer.nsi" (
        echo - Missing NSIS script file
    )
    
    if not exist "spei.ico" (
        echo - Create an icon file or use the script to generate one
    )
    
    echo.
)

pause
exit /b %ERRORS%
