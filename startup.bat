@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

echo.
echo ==========================================
echo AgentBot Environment Setup Script
echo ==========================================
echo.

REM Check Python
python --version
if errorlevel 1 (
    echo ERROR: Python not found
    pause
    exit /b 1
)

REM Create virtual environment
if not exist env (
    echo Creating virtual environment...
    python -m venv env
)

REM Activate virtual environment
call env\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
if exist requirements.txt (
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    echo WARNING: requirements.txt not found
)

REM Create directories
if not exist logs mkdir logs

REM Setup .env
if not exist .env (
    if exist .env.example (
        copy .env.example .env
    )
)

echo.
echo Setup complete!
echo.
pause