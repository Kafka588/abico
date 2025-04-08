#!/bin/bash

# Exit on error
set -e

echo "=== Installing Abico Avatar Generator ==="
echo "This script will set up the environment and install all dependencies."

# Check if Python 3.10 is installed
if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10 is required but not found. Please install Python 3.10 first."
    exit 1
fi

# Create and activate virtual environment
echo "Creating virtual environment..."
python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install PyTorch with CUDA 11.8 support
echo "Installing PyTorch with CUDA 11.8 support..."
pip install torch==2.0.1+cu118 torchvision==0.15.2+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118

# Install dependencies from pyproject.toml
echo "Installing project dependencies..."
pip install poetry
poetry install

# Create models directory if it doesn't exist
echo "Creating models directory..."
mkdir -p models

# Clone F5-TTS from Hugging Face
echo "Cloning F5-TTS from Hugging Face..."
if [ ! -d "models/F5-TTS" ]; then
    git clone https://huggingface.co/kafka0588/F5-TTS models/F5-TTS
    cd models/F5-TTS
    unzip F5-TTS.zip -d .
    pip install -e .
    cd ../..
else
    echo "F5-TTS already exists, skipping..."
fi

# Clone Easy-Wav2Lip
echo "Cloning Easy-Wav2Lip..."
if [ ! -d "models/Easy-Wav2Lip" ]; then
    git clone https://github.com/anothermartz/Easy-Wav2Lip.git models/Easy-Wav2Lip
    cd models/Easy-Wav2Lip
    python install.py
    cd ../..
else
    echo "Easy-Wav2Lip already exists, skipping..."
fi

# Clone reference files
echo "Cloning reference files..."
if [ ! -d "abico-reference" ]; then
    git clone https://huggingface.co/datasets/kafka0588/abico-reference
else
    echo "Reference files already exist, skipping..."
fi

echo "=== Installation complete! ==="
echo "To run the application, use: ./run_linux.sh" 