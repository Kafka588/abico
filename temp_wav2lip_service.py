import os
import configparser
import subprocess
from pathlib import Path
import shutil
import uuid
import sys

class Wav2LipService:
    def __init__(self):
        # Find the project root directory
        self.project_root = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.wav2lip_dir = self.project_root / "models" / "Easy-Wav2Lip"
        self.temp_dir = self.wav2lip_dir / "temp"
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Store the current Python executable path
        self.python_executable = sys.executable
        print(f"Using Python interpreter: {self.python_executable}")

    def generate_talking_avatar(self, video_path: str, audio_path: str, output_path: str, **kwargs) -> str:
        try:
            # Create config.ini with our parameters
            config_path = self.wav2lip_dir / "config.ini"
            self._create_config(config_path, video_path=video_path, audio_path=audio_path, **kwargs)
            
            # Get the absolute path to run.py to avoid path issues
            run_script = self.wav2lip_dir / "run.py"
            
            if not run_script.exists():
                raise FileNotFoundError(f"Wav2Lip run script not found at: {run_script}")
                
            # Run Wav2Lip - use the current Python executable from the virtual environment
            cmd = [
                self.python_executable,  # Use our current Python with all packages
                str(run_script)
            ]

            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, 
                                  cwd=str(self.wav2lip_dir),
                                  capture_output=True, 
                                  text=True, 
                                  encoding='utf-8')

            print(f"Wav2Lip STDOUT: {result.stdout}")
            print(f"Wav2Lip STDERR: {result.stderr}")

            if result.returncode != 0:
                raise Exception(f"Wav2Lip failed with code {result.returncode}")

            # Find the output file from Wav2Lip's temp directory
            temp_output = self.temp_dir / "output.mp4"
            if not temp_output.exists():
                raise FileNotFoundError(f"Wav2Lip output not found at {temp_output}")

            # Copy the file to the specified output path
            output_path = Path(output_path)
            output_path.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy2(temp_output, output_path)
            print(f"Copied Wav2Lip output to: {output_path}")

            return str(output_path)

        except Exception as e:
            print(f"Wav2Lip generation failed: {str(e)}")
            raise

    def _create_config(self, config_path: Path, **kwargs):
        """Create config.ini file for Wav2Lip"""
        # Map quality values to correct format
        quality_map = {
            'enhanced': 'Enhanced',  # Capitalize for Enhanced quality
            'fast': 'Fast',
            'improved': 'Improved'
        }
        
        # Get quality from kwargs and map it, default to 'Enhanced'
        quality = kwargs.get('quality', 'enhanced').lower()
        mapped_quality = quality_map.get(quality, 'Enhanced')

        config = configparser.ConfigParser()
        config['OPTIONS'] = {
            'video_file': kwargs['video_path'],
            'vocal_file': kwargs['audio_path'],
            'quality': mapped_quality,  # Use mapped quality value
            'output_height': 'full resolution',
            'wav2lip_version': kwargs.get('wav2lip_version', 'Wav2Lip'),
            'use_previous_tracking_data': 'True',
            'nosmooth': str(kwargs.get('nosmooth', True)).lower(),
            'preview_window': 'False'
        }
        
        config['PADDING'] = {
            'U': str(kwargs.get('pad_up', 0)),
            'D': str(kwargs.get('pad_down', 0)),
            'L': str(kwargs.get('pad_left', 0)),
            'R': str(kwargs.get('pad_right', 0))
        }
        
        config['MASK'] = {
            'size': '1',
            'feathering': '1',
            'mouth_tracking': 'False',
            'debug_mask': 'False'
        }
        
        config['OTHER'] = {
            'batch_process': 'False',
            'output_suffix': '_w2l',
            'include_settings_in_suffix': 'True',
            'preview_input': 'False',
            'preview_settings': 'False',
            'frame_to_preview': '1'
        }

        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)