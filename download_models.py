import os
import requests
from pathlib import Path
import gdown  # pip install gdown

def download_file(url, destination):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def setup_models():
    # Create models directory structure
    models_dir = Path("models")
    f5tts_dir = models_dir / "F5-TTS" / "custom_models" / "mongolian"
    wav2lip_dir = models_dir / "Easy-Wav2Lip" / "checkpoints"
    
    f5tts_dir.mkdir(parents=True, exist_ok=True)
    wav2lip_dir.mkdir(parents=True, exist_ok=True)

    # Download F5-TTS models (replace with your actual model URLs)
    f5tts_model_url = "YOUR_MODEL_URL"
    f5tts_vocab_url = "YOUR_VOCAB_URL"
    
    print("Downloading F5-TTS model...")
    gdown.download(f5tts_model_url, str(f5tts_dir / "model_226800.pt"), quiet=False)
    gdown.download(f5tts_vocab_url, str(f5tts_dir / "vocab.txt"), quiet=False)

    # Download Wav2Lip models
    wav2lip_model_url = "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip.pth"
    wav2lip_gan_url = "https://github.com/Rudrabha/Wav2Lip/releases/download/v1.0/wav2lip_gan.pth"
    
    print("Downloading Wav2Lip models...")
    download_file(wav2lip_model_url, wav2lip_dir / "wav2lip.pth")
    download_file(wav2lip_gan_url, wav2lip_dir / "wav2lip_gan.pth")

if __name__ == "__main__":
    setup_models()