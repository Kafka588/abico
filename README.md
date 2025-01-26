## Abico Project: AI-Powered Avatar Generator

An advanced AI-driven solution developed specifically for Abico LLC, a leading Japanese product distributor in Mongolia. This project combines cutting-edge speech synthesis and lip synchronization technologies to create engaging, multilingual content featuring digital avatars.

### Overview

This project leverages artificial intelligence to generate talking avatars, enabling Abico to create compelling, personalized content for their Japanese product marketing in Mongolia. By combining fine-tuned speech synthesis with precise lip synchronization, we've created a system that bridges language and cultural gaps in content creation.

### Key Features

- **Mongolian Speech Synthesis**: Utilizes a custom-trained F5-TTS model
- **Precise Lip Synchronization**: Powered by Easy-Wav2Lip technology
- **Digital Avatar Integration**: Supports various avatar formats
- **High-Quality Output**: Produces professional-grade video content

### Technical Specifications

#### Speech Synthesis (F5-TTS)
- **Training Data**: 96,000 samples from 500 unique speeches
- **Training Duration**: 26,000 steps
- **Dataset Size**: Approximately 140 hours of Mongolian speech
- **Model Architecture**: Based on F5-TTS framework with custom modifications

#### Lip Synchronization
- **Technology**: Easy-Wav2Lip implementation
- **Features**: 
  - Real-time lip movement synchronization
  - Support for multiple avatar formats
  - Enhanced facial movement precision

### Demo

![Demo](demo/demo.gif)

It uses fine-tuned models for F5-TTS to generate speech in Mongolian. The model is trained on Mongolian speech data to ensure natural pronunciation and intonation.

### Sample Outputs

#### Video Demo on YouTube:
[![Watch the demo](https://img.youtube.com/vi/YzPnC2BntIw/maxresdefault.jpg)](https://www.youtube.com/watch?v=YzPnC2BntIw)

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

### Business Impact

This solution enables Abico LLC to:
- Create engaging multilingual content efficiently
- Maintain cultural authenticity in communications
- Scale content production cost-effectively
- Enhance digital marketing capabilities

### Technology Stack

- **Speech Synthesis**: Custom-trained F5-TTS model
- **Lip Synchronization**: Easy-Wav2Lip implementation
- **Framework**: PyTorch 2.0.1
- **CUDA Support**: Version 11.8
- **Python Version**: 3.10

### Sources

- [F5-TTS](https://github.com/SWivid/F5-TTS)
- [Easy-Wav2Lip](https://github.com/anothermartz/Easy-Wav2Lip)

### License

This project is developed for Abico LLC. All rights reserved.
