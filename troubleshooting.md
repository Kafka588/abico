# Troubleshooting Guide for Abico Avatar Generator

This guide will help you resolve common issues that might occur during installation or usage of the Abico Avatar Generator.

## Installation Issues

### Python Version Issues

**Problem**: The installation script fails with "Python 3.10 is required but not found."

**Solution**:
1. Make sure Python 3.10 is installed on your system
2. If you have multiple Python versions installed, make sure Python 3.10 is in your PATH
3. On Windows, you can try running the script with the full path to Python 3.10:
   ```
   C:\Path\To\Python3.10\python.exe install_windows.bat
   ```

### Poetry Installation Issues

**Problem**: The script fails when trying to install dependencies with Poetry.

**Solution**:
1. Try installing Poetry manually first:
   ```
   pip install poetry
   ```
2. If that doesn't work, you can try installing dependencies directly:
   ```
   pip install -r requirements.txt
   ```

### Git Issues

**Problem**: The script fails when trying to clone repositories.

**Solution**:
1. Make sure Git is installed on your system
2. Check your internet connection
3. If you're behind a proxy, configure Git to use it:
   ```
   git config --global http.proxy http://proxy.example.com:8080
   ```

## Running Issues

### Virtual Environment Not Found

**Problem**: The run script fails with "Virtual environment not found."

**Solution**:
1. Make sure you've run the installation script first
2. If the installation script failed, try running it again
3. If the problem persists, you can try creating the virtual environment manually:
   ```
   python3.10 -m venv venv
   ```

### Application Crashes

**Problem**: The application crashes when you try to run it.

**Solution**:
1. Check the error message in the console
2. Make sure all dependencies are installed correctly
3. Try running the application with more verbose output:
   ```
   python -v app.py
   ```

## Model Issues

### F5-TTS Issues

**Problem**: The F5-TTS model fails to generate speech.

**Solution**:
1. Make sure the F5-TTS model is installed correctly
2. Check if the reference files are present in the abico-reference directory
3. Try reinstalling the F5-TTS model:
   ```
   cd models/F5-TTS
   pip install -e .
   cd ../..
   ```

### Easy-Wav2Lip Issues

**Problem**: The Easy-Wav2Lip model fails to synchronize lips.

**Solution**:
1. Make sure the Easy-Wav2Lip model is installed correctly
2. Check if the input video is in a compatible format
3. Try reinstalling the Easy-Wav2Lip model:
   ```
   cd models/Easy-Wav2Lip
   python install.py
   cd ../..
   ```

## Still Having Issues?

If you're still experiencing issues after trying the solutions above, please contact the Abico support team with the following information:
1. Your operating system and version
2. The Python version you're using
3. The exact error message you're seeing
4. Any steps you've already taken to try to resolve the issue 