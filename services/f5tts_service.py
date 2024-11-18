# services/f5tts_service.py
import subprocess
import os
from pathlib import Path

class F5TTSService:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.venv_path = self.base_path / "venvs" / "f5tts"
        
        if os.name == 'nt':  # Windows
            self.activate_script = str(self.venv_path / "Scripts" / "activate.bat")
            self.f5tts_cli = str(self.venv_path / "Scripts" / "f5-tts_infer-cli.exe")
        else:  # Linux/Mac
            self.activate_script = str(self.venv_path / "bin" / "activate")
            self.f5tts_cli = str(self.venv_path / "bin" / "f5-tts_infer-cli")
            
        print(f"Venv activation script: {self.activate_script}")
        print(f"F5-TTS CLI path: {self.f5tts_cli}")
        print(f"Activation script exists: {Path(self.activate_script).exists()}")
        print(f"F5-TTS CLI exists: {Path(self.f5tts_cli).exists()}")

    def verify_installation(self):
        """Verify F5-TTS installation in the virtual environment"""
        try:
            if os.name == 'nt':
                # Use a simpler verification on Windows
                if not Path(self.f5tts_cli).exists():
                    print("F5-TTS CLI executable not found")
                    return False
                    
                verify_cmd = f'"{self.f5tts_cli}" --help'
                result = subprocess.run(
                    verify_cmd,
                    capture_output=True,
                    text=True,
                    shell=True
                )
            else:
                verify_cmd = [
                    'bash', '-c',
                    f'source "{self.activate_script}" && which f5-tts_infer-cli'
                ]
                result = subprocess.run(
                    verify_cmd, 
                    capture_output=True, 
                    text=True
                )
            
            print(f"Verification STDOUT: {result.stdout}")
            print(f"Verification STDERR: {result.stderr}")
            print(f"Verification return code: {result.returncode}")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Verification error: {str(e)}")
            return False

    def generate_audio(self, text, output_path, reference_audio=None, reference_text=None):
        try:
            # Ensure output directory exists
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # For Windows, use direct executable path
            if os.name == 'nt':
                cmd = f'"{self.f5tts_cli}" --model "F5-TTS" --gen_text "{text}"'
            else:
                cmd = [
                    'bash', '-c',
                    f'source "{self.activate_script}" && '
                    f'"{self.f5tts_cli}" --model "F5-TTS" '
                    f'--gen_text "{text}" '
                ]

            if reference_audio:
                cmd += f' --ref_audio "{reference_audio}"'
                if reference_text:
                    cmd += f' --ref_text "{reference_text}"'
                else:
                    cmd += ' --ref_text ""'
                    
            cmd += f' --output "{output_path}"'

            print(f"Running command: {cmd}")
            
            # Run command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                shell=True  # Use shell=True for Windows
            )

            print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")

            if result.returncode != 0:
                raise Exception(f"Command failed with code {result.returncode}\nError: {result.stderr}")

            return True

        except Exception as e:
            raise Exception(f"F5-TTS generation failed: {str(e)}")