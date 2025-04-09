#!/bin/bash

# Exit on error
set -e

echo "=== Fixing dlib Installation ==="
echo "This script will install dlib and its dependencies."

# Check if Python 3.10 is installed
if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10 is required but not found. Please install Python 3.10 first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run install_linux.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Install system dependencies for dlib
echo "Installing system dependencies for dlib..."
if command -v apt-get &> /dev/null; then
    # Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y build-essential cmake libx11-dev libopenblas-dev liblapack-dev
elif command -v yum &> /dev/null; then
    # CentOS/RHEL
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y cmake libX11-devel openblas-devel lapack-devel
elif command -v pacman &> /dev/null; then
    # Arch Linux
    sudo pacman -S --noconfirm base-devel cmake libx11 openblas lapack
fi

# Install dlib
echo "Installing dlib..."
pip install dlib==19.24.2

echo "=== dlib Installation Complete! ==="
echo "You can now run the application using ./run_linux.sh" 