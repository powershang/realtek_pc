@echo off
echo ====================================================
echo Enhanced Register Signal Analyzer GUI Tool
echo Building Executable Package
echo ====================================================

echo.
echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo.
echo [2/4] Installing PyInstaller...
pip install pyinstaller>=5.0
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo [3/4] Building executable...
pyinstaller --onefile --windowed --name "RegisterAnalyzer" --icon=icon.ico register_gui_enhanced.py 2>nul || pyinstaller --onefile --windowed --name "RegisterAnalyzer" register_gui_enhanced.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to build executable
    pause
    exit /b 1
)

echo.
echo [4/4] Cleaning up...
if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__

echo.
echo ====================================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ====================================================
echo.
echo The executable file has been created:
echo   dist\RegisterAnalyzer.exe
echo.
echo You can now distribute this file to users.
echo No Python installation required on target machines.
echo.
pause 