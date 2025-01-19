import pkg_resources
import torch
import torchaudio
import numpy as np

def check_packages():
    print("=== Package Versions ===")
    packages = [
        'torch',
        'torchaudio',
        'numpy',
        'f5-tts',
        'jieba',
        'transformers',
        'scipy'
    ]
    
    for package in packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"{package}: {version}")
        except:
            print(f"{package}: Not found")
    
    print(f"\nPyTorch CUDA: {torch.version.cuda}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name()}")

if __name__ == "__main__":
    check_packages()