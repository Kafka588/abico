# test.py
from services.f5tts_service import F5TTSService
from pathlib import Path
import os

def test_f5tts_generation():
    # Create temp directory
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    print("\nTesting F5-TTS Service")
    print("-" * 50)
    
    service = F5TTSService()
    
    # Verify installation first
    if not service.verify_installation():
        print("Error: F5-TTS not properly installed or environment not accessible")
        return
        
    print("F5-TTS installation verified!")
    
    # Test cases
    test_cases = [
        {
            "name": "Reference Audio Generation",
            "text": "Some text you want TTS model generate for you.",
            "ref_audio": "audio.wav",
            "ref_text": "The examination and testimony of the experts enabled the Commission to conclude that five shots may have been fired,",
            "output": "temp/output_with_ref.wav"
        },
        {
            "name": "Basic Generation",
            "text": "Hello, this is a basic test without reference audio.",
            "ref_audio": None,
            "ref_text": None,
            "output": "temp/output_basic.wav"
        }
    ]
    
    for test in test_cases:
        print(f"\nRunning test: {test['name']}")
        try:
            output_path = test['output']
            result = service.generate_audio(
                text=test['text'],
                output_path=output_path,
                reference_audio=test['ref_audio'],
                reference_text=test['ref_text']
            )
            
            print(f"Generation {'successful' if result else 'failed'}!")
            if Path(output_path).exists():
                print(f"Output file created: {output_path}")
                print(f"File size: {os.path.getsize(output_path)} bytes")
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            continue

if __name__ == "__main__":
    test_f5tts_generation()