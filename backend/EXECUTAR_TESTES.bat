@echo off
cd /d C:\Users\lucie\Documents\GitHub\medai\backend
call medai_env\Scripts\activate.bat
python run_tests.py
pause