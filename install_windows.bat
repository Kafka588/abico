@echo off
echo === Installing Abico Avatar Generator ===
echo This script will set up the environment and install all dependencies.

REM Check if Python 3.10 is installed
python3.10 --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python 3.10 is required but not found. Please install Python 3.10 first.
    exit /b 1
)

REM Create and activate virtual environment
echo Creating virtual environment...
python3.10 -m venv venv
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install PyTorch with CUDA 11.8 support
echo Installing PyTorch with CUDA 11.8 support...
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118

REM Install dependencies from pyproject.toml
echo Installing project dependencies...
pip install poetry
poetry install

REM Create models directory if it doesn't exist
echo Creating models directory...
if not exist models mkdir models

REM Clone F5-TTS from Hugging Face
echo Cloning F5-TTS from Hugging Face...
if not exist models\F5-TTS (
    git clone https://huggingface.co/kafka0588/F5-TTS models\F5-TTS
    cd models\F5-TTS
    powershell -Command "Expand-Archive -Path F5-TTS.zip -DestinationPath ."
    pip install -e .
    cd ..\..
) else (
    echo F5-TTS already exists, skipping...
)

REM Clone Easy-Wav2Lip
echo Cloning Easy-Wav2Lip...
if not exist models\Easy-Wav2Lip (
    git clone https://github.com/anothermartz/Easy-Wav2Lip.git models\Easy-Wav2Lip
    cd models\Easy-Wav2Lip
    python install.py
    cd ..\..
) else (
    echo Easy-Wav2Lip already exists, skipping...
)

REM Clone reference files
echo Cloning reference files...
if not exist abico-reference (
    git clone https://huggingface.co/datasets/kafka0588/abico-reference
) else (
    echo Reference files already exist, skipping...
)

echo === Installation complete! ===
echo To run the application, use: run_windows.bat 