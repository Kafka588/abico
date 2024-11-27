# services/f5tts_service.py
import os
from pathlib import Path
import subprocess
import sys

class F5TTSService:
    def __init__(self):
        # Set UTF-8 encoding for Windows
        if os.name == 'nt':
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        
        # Get project root
        self.project_root = Path(__file__).parent.parent
        
        # Virtual environment path (relative to project root)
        self.venv_path = self.project_root / "venvs" / "f5tts"
        
        # Model paths
        self.models_path = self.project_root / "models" / "F5-TTS" / "custom_models" / "mongolian"
        self.custom_model = self.models_path / "model_226800.pt"
        self.custom_vocab = self.models_path / "vocab.txt"
        
        # Set up CLI paths
        if os.name == 'nt':  # Windows
            self.activate_script = self.venv_path / "Scripts" / "activate.bat"
            self.f5tts_cli = self.venv_path / "Scripts" / "f5-tts_infer-cli.exe"
        else:  # Linux/Mac
            self.activate_script = self.venv_path / "bin" / "activate"
            self.f5tts_cli = self.venv_path / "bin" / "f5-tts_infer-cli"
        
        # Add output directory
        self.output_dir = self.project_root / "temp" / "generated_audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def verify_installation(self):
        """Verify F5TTS installation"""
        try:
            # Test F5TTS CLI with --help
            cmd = f'"{self.f5tts_cli}" --help'
            result = self._run_in_venv(cmd)
            return result.returncode == 0
        except Exception as e:
            print(f"F5TTS verification failed: {e}")
            return False

    def _run_in_venv(self, cmd):
        """Run a command in the virtual environment with UTF-8 encoding"""
        try:
            if os.name == 'nt':  # Windows
                # Force UTF-8 encoding for Windows command prompt
                full_cmd = f'cmd /c "chcp 65001 > nul && {self.activate_script} && {cmd}"'
            else:  # Linux/Mac
                full_cmd = f'source "{self.activate_script}" && {cmd}'
            
            print(f"Running command: {full_cmd}")
            
            # Set UTF-8 encoding for subprocess
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            return subprocess.run(
                full_cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env
            )
        except Exception as e:
            print(f"Error running command: {str(e)}")
            raise

    def generate_audio(self, text, output_path, reference_audio=None, reference_text=None, speed=1.0):
        try:
            # Convert output_path to Path object and ensure it's a directory
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Build command
            cmd_parts = [
                f'"{self.f5tts_cli}"',
                '--model "F5-TTS"',
                f'--ckpt_file "{self.custom_model}"',
                f'--vocab_file "{self.custom_vocab}"',
                f'--gen_text "{text}"',
                '--vocoder_name vocos',
                '--remove_silence false',
                f'--output_dir "{output_dir}"',
                f'--speed {speed}'
            ]

            if reference_audio:
                cmd_parts.append(f'--ref_audio "{reference_audio}"')
                if reference_text:
                    cmd_parts.append(f'--ref_text "{reference_text}"')
                else:
                    cmd_parts.append('--ref_text ""')

            cmd = ' '.join(cmd_parts)
            print(f"Running F5TTS command: {cmd}")
            
            result = self._run_in_venv(cmd)
            print(f"STDOUT: {result.stdout}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")

            if result.returncode != 0:
                raise Exception(f"Command failed with code {result.returncode}")

            # The output file will be 'infer_cli_out.wav' in the specified directory
            output_file = output_dir / "infer_cli_out.wav"
            if output_file.exists():
                print(f"Generated audio file: {output_file}")
                return str(output_file)
            else:
                raise FileNotFoundError(f"Generated audio file not found at {output_file}")

        except Exception as e:
            print(f"F5-TTS generation failed: {str(e)}")
            raise