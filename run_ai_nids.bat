@echo off
TITLE AI-NIDS Launcher
COLOR 0A
CD /D "%~dp0"

IF EXIST ".venv\Scripts\python.exe" (
    SET "PYTHON_EXE=.venv\Scripts\python.exe"
) ELSE (
    SET "PYTHON_EXE=python"
)

"%PYTHON_EXE%" run.py

IF ERRORLEVEL 1 (
    echo.
    echo [ERROR] AI-NIDS failed to start.
    echo Please ensure Python and required dependencies are installed.
    echo.
    pause
)
