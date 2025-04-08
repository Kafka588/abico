@echo off
echo Starting Abico Avatar Generator...

REM Check if virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found. Please run install_windows.bat first.
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application
python app.py

REM Deactivate virtual environment when done
deactivate 