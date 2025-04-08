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

### Installation Guide

Follow these steps carefully to set up the project:

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/abico.git
cd abico
```

#### 2. Set Up the Python Environment
This project requires Python 3.10. Create and activate a virtual environment:

```bash
# Create virtual environment
python3.10 -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate
```

#### 3. Install PyTorch with Specific Version
Install PyTorch 2.0.1 with CUDA 11.8 support:

```bash
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118
```

#### 4. Install Dependencies and Upgrade Pip
```bash
# Upgrade pip first
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

#### 5. Set Up the Models
Create the models directory and set up F5-TTS:

```bash
# Create models directory
mkdir -p models

# Option 1: Use the included F5-TTS archive (RECOMMENDED)
# Extract the F5-TTS archive to the models directory
# This contains version 0.1.1 which is compatible with the trained model
unzip f5tts_archive.zip -d models/

# Option 2: Clone the repository (NOT RECOMMENDED - requires version downgrade)
# cd models
# git clone https://github.com/SWivid/F5-TTS.git
# cd ..
```

> **IMPORTANT:** This project requires F5-TTS version 0.1.1 specifically. The GitHub repository may contain newer versions that are not compatible with the trained model. Using the archived version is strongly recommended.

#### 6. Install F5-TTS with Compatible Dependencies
The F5-TTS model requires specific versions of several packages to work correctly:

```bash
# Install F5-TTS in editable mode with no dependencies (we'll manage them separately)
cd models/F5-TTS
pip install -e . --no-dependencies
cd ../..

# Install compatible versions of required packages
pip install transformers==4.35.0
pip install accelerate==0.23.0
pip install gradio==3.45.2
pip install datasets==2.14.0
```

#### 7. Prepare Reference Files
The system uses specific reference audio files for speech generation. Run the preparation script:

```bash
# Run the reference preparation script
python prepare_references.py
```

#### 8. Set Up Custom Model Files
Make sure your custom model files are in the correct location:

```bash
# Create custom model directory if it doesn't exist
mkdir -p models/F5-TTS/custom_models/mongolian

# Copy your model checkpoint and vocabulary files to this directory
# Example (adjust paths as needed):
# cp /path/to/your/model_226800.pt models/F5-TTS/custom_models/mongolian/
# cp /path/to/your/vocab.txt models/F5-TTS/custom_models/mongolian/
```

#### 9. Running the Application
You can run either the main application or the standalone TTS demo:

```bash
# Run the main application
python app.py

# OR run just the TTS demo
python gradio_f5tts.py
```

### Troubleshooting

#### Common Issues:

1. **"No module named 'f5_tts'"**:
   - Make sure you've installed F5-TTS in editable mode
   - Check if your virtual environment is activated

2. **"No such file or directory: 'references/...'"**:
   - Run the `prepare_references.py` script to set up reference files
   - Ensure the reference audio files exist in the references directory

3. **Empty or noisy audio output**:
   - Verify that the reference files are properly formatted
   - Make sure you're using the correct model checkpoint

4. **Transformer module import errors**:
   - Install the specific versions of the dependencies as mentioned above

5. **Disk space errors during installation**:
   - Make sure you have at least 15GB of free disk space for model downloads

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
