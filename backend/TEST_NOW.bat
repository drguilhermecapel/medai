@echo off
title MedAI - Executando Testes

echo ==========================================
echo     MedAI - Sistema de Testes
echo ==========================================
echo.

cd /d C:\Users\lucie\Documents\GitHub\medai\backend

if exist medai_env\Scripts\python.exe (
    echo Usando ambiente virtual existente...
    medai_env\Scripts\python.exe run_tests.py
) else (
    echo Executando com Python do sistema...
    python run_tests.py
)

echo.
echo ==========================================
echo     Testes Finalizados!
echo ==========================================
echo.
echo Pressione qualquer tecla para fechar...
pause > nul