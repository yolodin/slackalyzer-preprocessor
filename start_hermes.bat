@echo off
REM 🚀 Hermes Communication Intelligence System
REM Batch script launcher for Windows

echo 🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
echo 🚀 HERMES COMMUNICATION INTELLIGENCE SYSTEM
echo 🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟
echo Named after the Greek god of communication
echo AI-Powered Slack Analysis ^& Insights Platform
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not installed.
    echo Please install Python 3.7+ from https://python.org and try again.
    pause
    exit /b 1
)

REM Run the Python startup script
python start_hermes.py %*
