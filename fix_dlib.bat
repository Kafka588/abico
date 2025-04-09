@echo off
echo === Fixing dlib Installation ===
echo This script will install dlib using a pre-built wheel.

REM Check if Python 3.10 is installed
python3.10 --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.10 is required but not found. Please install Python 3.10 first.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found. Please run install_windows.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dlib using pre-built wheel
echo Installing dlib using pre-built wheel...
pip install https://github.com/jloh02/dlib/releases/download/v19.22/dlib-19.22.99-cp310-cp310-win_amd64.whl

echo === dlib Installation Complete! ===
echo You can now run the application using launch_app.bat
pause 