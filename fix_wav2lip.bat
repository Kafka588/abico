@echo off
echo === Fixing Wav2Lip Installation ===
echo This script will ensure ffmpeg is available for Wav2Lip to work properly.

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

REM Check if ffmpeg is installed
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ffmpeg not found. Installing ffmpeg...
    
    REM Create a directory for ffmpeg
    if not exist tools mkdir tools
    cd tools
    
    REM Download ffmpeg
    echo Downloading ffmpeg...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"
    
    REM Extract ffmpeg
    echo Extracting ffmpeg...
    powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"
    
    REM Add ffmpeg to PATH for this session
    set PATH=%PATH%;%CD%\ffmpeg-master-latest-win64-gpl\bin
    
    REM Create a batch file to set PATH for future sessions
    echo @echo off > ..\set_ffmpeg_path.bat
    echo set PATH=%%PATH%%;%CD%\ffmpeg-master-latest-win64-gpl\bin >> ..\set_ffmpeg_path.bat
    echo echo ffmpeg path has been set. >> ..\set_ffmpeg_path.bat
    echo pause >> ..\set_ffmpeg_path.bat
    
    cd ..
) else (
    echo ffmpeg is already installed.
)

REM Install ffmpeg-python if not already installed
pip install ffmpeg-python

REM Create a wrapper script for Wav2Lip
echo Creating Wav2Lip wrapper script...
(
echo @echo off
echo set PATH=%%PATH%%;%CD%\tools\ffmpeg-master-latest-win64-gpl\bin
echo python "%%~dp0run.py" %%*
) > models\Easy-Wav2Lip\run_wav2lip.bat

echo === Wav2Lip Fix Complete! ===
echo You can now run the application using launch_app.bat
pause 