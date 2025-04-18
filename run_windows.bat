@echo off
echo Starting Abico Avatar Generator...

REM Check if virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found. Please run install_windows.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if port 7860 is already in use
netstat -ano | findstr :7860 >nul
if %ERRORLEVEL% EQU 0 (
    echo Port 7860 is already in use. Trying to find an available port...
    set PORT=7861
    echo Using port %PORT% instead.
) else (
    set PORT=7860
)

REM Run the application with the specified port
echo Running application on port %PORT%...
python app.py --server_port %PORT%

REM Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo Application exited with error code %ERRORLEVEL%
    pause
)

REM Deactivate virtual environment when done
deactivate 