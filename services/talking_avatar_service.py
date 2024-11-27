import os
import sys
import subprocess
import configparser
from pathlib import Path
import shutil
from typing import Optional
import gradio as gr

class TalkingAvatarService:
    def __init__(self):
        # Set UTF-8 encoding for Windows
        if os.name == 'nt':
            sys.stdout.reconfigure(encoding='utf-8')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        # Initialize paths
        self.output_dir = Path("temp/output")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create temp directory
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Audio directory
        self.audio_dir = self.temp_dir / "audio"
        self.audio_dir.mkdir(exist_ok=True, parents=True)
        
        # Model paths
        self.f5tts_models = Path("models/F5-TTS/custom_models/mongolian")
        self.wav2lip_dir = Path("models/Easy-Wav2Lip")
        
        # Default reference paths
        self.defaults_dir = Path("defaults")
        self.default_ref_audio = self.defaults_dir / "reference_audio.wav"
        self.default_ref_text = "Лаборатори сургуулиудтай гурван жилийн өмнөөс гэрээ байгуулснаар манай сурлагын амжилт эрс сайжирсанд баяртай байгаа."

    def generate_audio(self, text: str, output_path: Path, reference_audio=None, reference_text=None, speed=1.0):
        try:
            cmd_parts = [
                'f5-tts_infer-cli',
                '--model "F5-TTS"',
                f'--ckpt_file "{self.f5tts_models}/model_226800.pt"',
                f'--vocab_file "{self.f5tts_models}/vocab.txt"',
                f'--gen_text "{text}"',
                '--vocoder_name vocos',
                '--remove_silence false',
                f'--output_dir "{output_path}"',
                f'--speed {speed}'
            ]

            if reference_audio:
                cmd_parts.append(f'--ref_audio "{reference_audio}"')
            if reference_text:
                cmd_parts.append(f'--ref_text "{reference_text}"')

            cmd = ' '.join(cmd_parts)
            print(f"Running F5TTS command: {cmd}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            if result.returncode != 0:
                raise Exception(f"F5TTS failed: {result.stderr}")

            output_file = output_path / "infer_cli_out.wav"
            return str(output_file) if output_file.exists() else None

        except Exception as e:
            print(f"Audio generation failed: {str(e)}")
            return None

    def generate_talking_avatar(self, text: str, avatar_path: str, reference_audio=None, 
                              reference_text=None, progress=None, **kwargs):
        try:
            # Generate audio
            audio_output = self.audio_dir / str(hash(text))
            audio_output.mkdir(exist_ok=True, parents=True)
            
            audio_path = self.generate_audio(
                text=text,
                output_path=audio_output,
                reference_audio=reference_audio,
                reference_text=reference_text,
                speed=kwargs.get('speed', 1.0)
            )
            
            if not audio_path:
                raise Exception("Audio generation failed")

            # Generate video
            output_path = self.output_dir / f"output_{hash(text)}.mp4"
            
            # Create Wav2Lip config
            config = {
                'OPTIONS': {
                    'video_file': avatar_path,
                    'vocal_file': audio_path,
                    'quality': kwargs.get('quality', 'Enhanced'),
                    'output_height': 'full resolution',
                    'wav2lip_version': kwargs.get('wav2lip_version', 'Wav2Lip'),
                    'use_previous_tracking_data': 'True',
                    'nosmooth': str(kwargs.get('nosmooth', True)).lower(),
                    'preview_window': 'False'
                },
                'PADDING': {
                    'U': str(kwargs.get('pad_up', 0)),
                    'D': str(kwargs.get('pad_down', 0)),
                    'L': str(kwargs.get('pad_left', 0)),
                    'R': str(kwargs.get('pad_right', 0))
                }
            }
            
            config_path = self.wav2lip_dir / "config.ini"
            self._write_config(config_path, config)
            
            # Run Wav2Lip
            cmd = f'cd "{self.wav2lip_dir}" && python run.py'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Wav2Lip failed: {result.stderr}")

            return str(output_path) if output_path.exists() else None

        except Exception as e:
            print(f"Error in generate_talking_avatar: {str(e)}")
            return None

    def _write_config(self, config_path: Path, config_data: dict):
        config = configparser.ConfigParser()
        for section, values in config_data.items():
            config[section] = {}
            for key, value in values.items():
                config[section][key] = str(value)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)