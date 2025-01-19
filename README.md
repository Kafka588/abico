- Current installation process when it comes to use it on another computer

1. Clone base project
git clone https://github.com/Kafka588/abico.git // this only requires gradio for now so i dont have any specific venv
2. Clone F5TTS and Wav2Lip repos inside models folder
 - For F5TTS and Wav2Lip I put the virtual environments inside venvs folder for each of them following the original repository structure installation process
 # For F5TTS under venvs folder NOTE: I installed each environment seperately with different python versions due to dependency issues
    python3.10 -m venv f5tts
    pip install torch==2.3.0+cu118 torchaudio==2.3.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118
    pip install -e . # i feel like the only reason i need this repo is to inference because im not going to train anything, so install f5tts as a package pip install git+https://github.com/SWivid/F5-TTS.git could be great just opinion havent really tried though but im just using this command for my project
```
    f5-tts_infer-cli \
        --model "F5-TTS" \
        --ref_audio "ref_audio.wav" \
        --ref_text "The content, subtitle or transcription of reference audio." \
        --gen_text "Some text you want TTS model generate for you."
```
 # For Wav2Lip under venvs folder
    python3.9 -m venv wav2lip
    python -m pip install --upgrade pip
    python -m pip install requests
    # Download FFmpeg using PowerShell
    Invoke-WebRequest -Uri "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -OutFile "ffmpeg.zip"
    # Extract and setup FFmpeg
    Expand-Archive -Path .\ffmpeg.zip -DestinationPath .\\
    xcopy /e /i /y "ffmpeg-master-latest-win64-gpl\bin\*" .\wav2lip\Scripts
    Remove-Item ffmpeg.zip
    Remove-Item -Recurse -Force ffmpeg-master-latest-win64-gpl
    git clone https://github.com/anothermartz/Easy-Wav2Lip.git
    cd wav2lip
    pip install -r requirements.txt
    python install.py # I changed path to the models in the install.py file to the path of the models folder in the base project in case might there could be pathing issue cuz im using different structure due to my project needs
3. Download the custom models and vocab.txt file and put it in the models/f5tts/custom_models folder # For wav2lip i dont have any custom models
4. Run the app.py file