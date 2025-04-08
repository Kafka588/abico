# Abico Avatar Generator - Installation Instructions

This document provides detailed instructions for installing and running the Abico Avatar Generator.

## Automated Installation

We've created scripts to automate the installation process for both Windows and Linux users.

### For Windows Users

1. Make sure Python 3.10 is installed on your system
2. Run the installation script by double-clicking `install_windows.bat` or running it from the command prompt:
   ```
   install_windows.bat
   ```
3. To run the application, double-click `run_windows.bat` or run it from the command prompt:
   ```
   run_windows.bat
   ```

### For Linux Users

1. Make sure Python 3.10 is installed on your system
2. Make the scripts executable:
   ```
   chmod +x install_linux.sh run_linux.sh
   ```
3. Run the installation script:
   ```
   ./install_linux.sh
   ```
4. To run the application:
   ```
   ./run_linux.sh
   ```

## What the Installation Scripts Do

The installation scripts perform the following steps:

1. Check if Python 3.10 is installed
2. Create a virtual environment
3. Install PyTorch with CUDA 11.8 support
4. Install project dependencies using Poetry
5. Create the models directory
6. Clone and set up F5-TTS from Hugging Face
7. Clone and set up Easy-Wav2Lip
8. Clone reference files

## Troubleshooting

### Common Issues

1. **Python Version**: Make sure you have Python 3.10 installed. The scripts check for this version.
2. **CUDA Support**: The installation includes PyTorch with CUDA 11.8 support. If you don't have a compatible GPU, the application will still run but may be slower.
3. **Git**: The scripts use Git to clone repositories. Make sure Git is installed on your system.
4. **Disk Space**: The installation requires several GB of disk space for the models and dependencies.

### Manual Installation

If the automated scripts don't work for you, you can follow the manual installation steps in the README.md file.
