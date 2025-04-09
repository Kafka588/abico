import os
import configparser
import subprocess
from pathlib import Path
import shutil
import uuid
import sys
import platform

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
        
        # Check if the wrapper script exists, if not, create it
        self.wrapper_script = self.wav2lip_dir / ("run_wav2lip.bat" if platform.system() == "Windows" else "run_wav2lip.sh")
        if not self.wrapper_script.exists():
            self._create_wrapper_script()

    def _create_wrapper_script(self):
        """Create a wrapper script for Wav2Lip that sets the PATH correctly"""
        is_windows = platform.system() == "Windows"
        ffmpeg_path = self.project_root / "tools" / "ffmpeg-master-latest-win64-gpl" / "bin" if is_windows else "/usr/bin"
        
        with open(self.wrapper_script, 'w') as f:
            if is_windows:
                f.write('@echo off\n')
                f.write(f'set PATH=%PATH%;{ffmpeg_path}\n')
                f.write(f'echo Using ffmpeg from: {ffmpeg_path}\n')
                f.write(f'where ffmpeg\n')
                f.write(f'python "{self.wav2lip_dir}\\run.py" %*\n')
            else:
                f.write('#!/bin/bash\n')
                f.write(f'export PATH=$PATH:{ffmpeg_path}\n')
                f.write(f'echo "Using ffmpeg from: {ffmpeg_path}"\n')
                f.write(f'which ffmpeg\n')
                f.write(f'python "{self.wav2lip_dir}/run.py" "$@"\n')
        
        # Make sure the script is executable
        os.chmod(self.wrapper_script, 0o755)

    def generate_talking_avatar(self, video_path: str, audio_path: str, output_path: str, **kwargs) -> str:
        try:
            # Create config.ini with our parameters
            config_path = self.wav2lip_dir / "config.ini"
            self._create_config(config_path, video_path=video_path, audio_path=audio_path, **kwargs)
            
            # Use the wrapper script instead of running Python directly
            cmd = [str(self.wrapper_script)]
            
            # Set environment variables to ensure ffmpeg is found
            env = os.environ.copy()
            ffmpeg_path = self.project_root / "tools" / "ffmpeg-master-latest-win64-gpl" / "bin"
            if platform.system() == "Windows":
                env["PATH"] = f"{ffmpeg_path};{env.get('PATH', '')}"
            else:
                env["PATH"] = f"{ffmpeg_path}:{env.get('PATH', '')}"
            
            print(f"Running command: {' '.join(cmd)}")
            print(f"With PATH: {env['PATH']}")
            
            result = subprocess.run(cmd, 
                                  cwd=str(self.wav2lip_dir),
                                  capture_output=True, 
                                  text=True, 
                                  encoding='utf-8',
                                  env=env)

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