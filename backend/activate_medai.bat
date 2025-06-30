@echo off
echo ========================================
echo   Ativando Ambiente Virtual do MedAI
echo ========================================
echo.

cd /d C:\Users\lucie\Documents\GitHub\medai\backend

if exist medai_env (
    echo Ativando ambiente medai_env...
    call medai_env\Scripts\activate.bat
) else if exist venv (
    echo Ativando ambiente venv...
    call venv\Scripts\activate.bat
) else (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo Execute primeiro: python -m venv medai_env
    pause
    exit /b 1
)

echo.
echo ✅ Ambiente ativado com sucesso!
echo.
echo Comandos uteis:
echo   - python run_tests.py    (executar testes)
echo   - pip list               (ver pacotes instalados)
echo   - deactivate             (desativar ambiente)
echo.

cmd /k