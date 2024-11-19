# services/f5tts_service.py
import subprocess
import os
import platform
from pathlib import Path

class F5TTSService:
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.venv_path = self.base_path / "venvs" / "f5tts"
        self.models_path = self.base_path / "models" / "F5-TTS"
        
        # Set up platform-specific paths and commands
        if os.name == 'nt':  # Windows
            self.activate_script = str(self.venv_path / "Scripts" / "activate.bat")
            self.f5tts_cli = str(self.venv_path / "Scripts" / "f5-tts_infer-cli.exe")
            self.activate_cmd = f'"{self.activate_script}" &&'
        else:  # Linux/Mac
            self.activate_script = str(self.venv_path / "bin" / "activate")
            self.f5tts_cli = str(self.venv_path / "bin" / "f5-tts_infer-cli")
            self.activate_cmd = f'source "{self.activate_script}" &&'
            
        # Config path
        self.config_path = str(self.models_path / "src" / "f5_tts" / "infer" / "examples" / "basic" / "basic.toml")
            
        print(f"Platform: {platform.system()}")
        print(f"Venv activation script: {self.activate_script}")
        print(f"F5-TTS CLI path: {self.f5tts_cli}")
        print(f"F5-TTS config path: {self.config_path}")
        print(f"Activation script exists: {Path(self.activate_script).exists()}")
        print(f"F5-TTS CLI exists: {Path(self.f5tts_cli).exists()}")
        print(f"Config file exists: {Path(self.config_path).exists()}")

    def _run_in_venv(self, cmd):
        """Run a command in the virtual environment"""
        if os.name == 'nt':  # Windows
            full_cmd = f'{self.activate_cmd} {cmd}'
            return subprocess.run(full_cmd, capture_output=True, text=True, shell=True)
        else:  # Linux/Mac
            full_cmd = f'bash -c \'{self.activate_cmd} {cmd}\''
            return subprocess.run(full_cmd, capture_output=True, text=True, shell=True)

    def verify_installation(self):
        """Verify F5-TTS installation in the virtual environment"""
        try:
            if not Path(self.activate_script).exists():
                print(f"Virtual environment activation script not found at: {self.activate_script}")
                return False

            # Verify F5-TTS CLI
            verify_cmd = f'"{self.f5tts_cli}" --help'
            result = self._run_in_venv(verify_cmd)
            
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

            # Construct the F5-TTS command
            cmd_parts = [
                f'"{self.f5tts_cli}"',
                '--model "F5-TTS"',
                f'--gen_text "{text}"',
                f'--output "{output_path}"'
            ]

            # Add reference audio and text if provided
            if reference_audio:
                cmd_parts.append(f'--ref_audio "{reference_audio}"')
                if reference_text:
                    cmd_parts.append(f'--ref_text "{reference_text}"')
                else:
                    cmd_parts.append('--ref_text ""')

            # Add config file if it exists
            if Path(self.config_path).exists():
                cmd_parts.append(f'--config "{self.config_path}"')

            # Join command parts
            cmd = ' '.join(cmd_parts)
            print(f"Running F5TTS command: {cmd}")
            
            # Run command in virtual environment
            result = self._run_in_venv(cmd)

            print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")

            if result.returncode != 0:
                raise Exception(f"Command failed with code {result.returncode}\nError: {result.stderr}")

            return True

        except Exception as e:
            print(f"F5-TTS generation failed: {str(e)}")
            raise