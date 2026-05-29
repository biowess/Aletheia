@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "LAUNCHER=%ROOT_DIR%launcher.py"

if not exist "%LAUNCHER%" (
    echo Error: launcher.py not found in %ROOT_DIR%
    pause
    exit /b 1
)

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python could not be found. Please install Python 3.11 or newer and ensure it is in your PATH.
    pause
    exit /b 1
)

python "%LAUNCHER%" %*
