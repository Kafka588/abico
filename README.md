## Abico Project Avatar Generator

This project uses open source projects that allow you to generate talking avatars using F5-TTS and Easy-Wav2Lip models.

### Demo

![Demo](demo/demo.gif)

It uses fine-tuned models for F5-TTS to generate speech in Mongolian. The model is trained on 100 hours of Mongolian speech. 

### Sample Outputs

#### Generated Audio Sample:
https://user-images.githubusercontent.com/Kafka588/abico/demo/demo.wav

#### Lip Synchronized Video Sample:
https://user-images.githubusercontent.com/Kafka588/abico/demo/demo.mp4

### Installation

1. Clone the repository
2. Install the dependencies
```bash
# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install PyTorch 2.0.1 with CUDA 11.8
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118
pip install -r requirements.txt

mkdir models

cd models

git clone https://github.com/SWivid/F5-TTS.git
git clone https://github.com/anothermartz/Easy-Wav2Lip.git

cd ..
```

3. Run the app.py file
```bash
python app.py
```

### Sources

- [F5-TTS](https://github.com/SWivid/F5-TTS)
- [Easy-Wav2Lip](https://github.com/anothermartz/Easy-Wav2Lip)
