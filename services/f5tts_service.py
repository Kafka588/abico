# services/f5tts_service.py
import subprocess
import os
from pathlib import Path

class F5TTSService:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.venv_path = self.base_path / "venvs" / "f5tts"
        self.models_path = self.base_path / "models" / "F5-TTS"
        
        if os.name == 'nt':  # Windows
            self.activate_script = str(self.venv_path / "Scripts" / "activate.bat")
            self.f5tts_cli = str(self.venv_path / "Scripts" / "f5-tts_infer-cli.exe")
        else:  # Linux/Mac
            self.activate_script = str(self.venv_path / "bin" / "activate")
            self.f5tts_cli = str(self.venv_path / "bin" / "f5-tts_infer-cli")
            
        # Config path
        self.config_path = str(self.models_path / "src" / "f5_tts" / "infer" / "examples" / "basic" / "basic.toml")
            
        print(f"Venv activation script: {self.activate_script}")
        print(f"F5-TTS CLI path: {self.f5tts_cli}")
        print(f"F5-TTS config path: {self.config_path}")
        print(f"Activation script exists: {Path(self.activate_script).exists()}")
        print(f"F5-TTS CLI exists: {Path(self.f5tts_cli).exists()}")
        print(f"Config file exists: {Path(self.config_path).exists()}")

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
            output_path.mkdir(parents=True, exist_ok=True)

            # Base command with minimal required parameters
            base_cmd = [
                str(self.f5tts_cli),
                '--model', 'F5-TTS',
                '--gen_text', text,
                '--output', str(output_path)
            ]

            # Add reference audio and text if provided
            if reference_audio:
                base_cmd.extend(['--ref_audio', str(reference_audio)])
                if reference_text:
                    base_cmd.extend(['--ref_text', reference_text])
                else:
                    base_cmd.extend(['--ref_text', ''])

            # Add config file if it exists
            if Path(self.config_path).exists():
                base_cmd.extend(['--config', self.config_path])

            print(f"Running F5TTS command: {' '.join(base_cmd)}")
            
            # Run command
            result = subprocess.run(
                base_cmd,
                capture_output=True,
                text=True
            )

            print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")

            if result.returncode != 0:
                raise Exception(f"Command failed with code {result.returncode}\nError: {result.stderr}")

            return True

        except Exception as e:
            print(f"F5-TTS generation failed: {str(e)}")
            raise