@echo off
echo Installing Abico...

:: Create a virtual environment
python -m venv abico_env
call abico_env\Scripts\activate

:: Upgrade pip
python -m pip install --upgrade pip

:: Install F5-TTS and Wav2Lip dependencies
pip install git+https://github.com/SWivid/F5-TTS.git
pip install basicsr==1.4.2 batch-face==1.4.0 dlib==19.24.2 facexlib==0.3.0 gdown==4.7.1 gfpgan==1.3.8 imageio-ffmpeg==0.4.9 importlib-metadata==6.8.0 ipython==8.16.1 moviepy==1.0.3 opencv-python==4.8.1.78 scipy==1.11.3 torch==2.1.0+cu121 torchaudio==2.1.0+cu121 torchvision==0.16.0+cu121 --extra-index-url https://download.pytorch.org/whl/cu121

:: Clone Wav2Lip repository
echo Cloning Wav2Lip repository...
git clone https://github.com/Rudrabha/Wav2Lip.git models/Easy-Wav2Lip

:: Run Wav2Lip install script
echo Running Wav2Lip install script...
cd models/Easy-Wav2Lip
python install.py
cd ../..

:: Install FFmpeg
echo Installing FFmpeg...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'"
powershell -Command "Expand-Archive -Path ffmpeg.zip -DestinationPath .\"
xcopy /e /i /y "ffmpeg-master-latest-win64-gpl\bin\*" .\abico_env\Scripts
del ffmpeg.zip
rmdir /s /q ffmpeg-master-latest-win64-gpl

:: Create necessary directories
mkdir temp
mkdir temp\output
mkdir temp\audio
mkdir defaults

echo Installation complete!