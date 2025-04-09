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

REM Find an available port
set PORT=7860
:PORT_CHECK
netstat -ano | findstr :%PORT% >nul
if %ERRORLEVEL% EQU 0 (
    set /a PORT+=1
    goto PORT_CHECK
)

REM Run the application with the specified port
echo Running application on port %PORT%...
start http://127.0.0.1:%PORT%
python app.py --server_port %PORT%

REM Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo Application exited with error code %ERRORLEVEL%
    pause
)

REM Deactivate virtual environment when done
deactivate 