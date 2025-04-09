import os
import sys
import ffmpeg

def test_ffmpeg():
    print("Testing ffmpeg-python library...")
    print(f"Python version: {sys.version}")
    
    # Check if ffmpeg is available in the system
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        print("System ffmpeg is available")
    except Exception as e:
        print(f"System ffmpeg not found: {str(e)}")
    
    # Test ffmpeg-python functionality
    try:
        # Try to use ffmpeg-python to probe a dummy file
        stream = ffmpeg.input("dummy.txt")
        print("Successfully created ffmpeg stream")
    except Exception as e:
        print(f"Error testing ffmpeg-python: {str(e)}")

if __name__ == "__main__":
    test_ffmpeg() 