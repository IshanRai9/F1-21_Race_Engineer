@echo off
title F1 2021 AI Race Engineer
cd /d "%~dp0"

echo ===================================================
echo   F1 2021 AI Race Engineer
echo ===================================================
echo.

:: Check python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in your system PATH!
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: Run engineer
python "%~dp0ai_engineer\main.py" %*

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The program terminated unexpectedly.
    pause
)
