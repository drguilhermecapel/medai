@echo off
echo Installing SPEI Python dependencies...

set "SPEI_HOME=%~dp0.."
set "PYTHON_HOME=%SPEI_HOME%\runtime\python"

:: Set PATH
set "PATH=%PYTHON_HOME%;%PYTHON_HOME%\Scripts;%PATH%"

:: Install Python dependencies
echo Installing Python dependencies...
cd /d "%SPEI_HOME%\backend"
python -m pip install --upgrade pip
python -m pip install poetry
poetry config virtualenvs.create false
poetry install --no-dev

:: Run database migrations
echo Running database migrations...
python -m alembic upgrade head

echo Python dependencies installation completed!
