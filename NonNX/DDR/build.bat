@echo off
echo DDR Register Comparison Tool - Build Script

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/4] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo [2/4] Generating embedded register map...
python generate_embedded_regmap.py
if errorlevel 1 (
    echo [WARNING] Failed to generate embedded regmap.
)

echo [3/4] Building executable...
pyinstaller --onefile --windowed --name "DDR_Register_Comparer" --clean main.py
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)

echo [4/4] Build complete! Output: dist\DDR_Register_Comparer.exe
pause
