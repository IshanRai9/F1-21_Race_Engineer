@echo off
title F1 2021 Telemetry Simulator
cd /d "%~dp0"

echo ===================================================
echo   F1 2021 Telemetry Simulator (Monza Test)
echo ===================================================
echo.
echo Make sure run_engineer.bat is running in another CMD window first!
echo.
pause

python "%~dp0ai_engineer\simulate_telemetry.py" 15

echo.
pause
