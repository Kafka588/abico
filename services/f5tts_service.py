# services/f5tts_service.py
import os
from pathlib import Path
import subprocess
import sys
import json
import re
from pydub import AudioSegment

class F5TTSService:
    def __init__(self):
        # Set UTF-8 encoding for Windows
        if os.name == 'nt':
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        
        # Get project root
        self.project_root = Path(__file__).parent.parent
        
        # Model paths
        self.models_path = self.project_root / "models" / "F5-TTS" / "custom_models" / "mongolian"
        self.custom_model = self.models_path / "model_226800.pt"
        self.custom_vocab = self.models_path / "vocab.txt"
        
        # References path
        self.references_folder = self.project_root / "references"
        self.references_folder.mkdir(parents=True, exist_ok=True)
        
        # Load reference configurations
        config_path = self.references_folder / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            self.references = json.load(f)
        
        # Set up CLI path
        self.f5tts_cli = "f5-tts_infer-cli"
        
        # Add output directory
        self.output_dir = self.project_root / "temp" / "generated_audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def verify_installation(self):
        """Verify F5TTS installation"""
        try:
            # Test F5TTS CLI with --help
            result = subprocess.run([self.f5tts_cli, "--help"], 
                                  capture_output=True, 
                                  text=True, 
                                  encoding='utf-8')
            return result.returncode == 0
        except Exception as e:
            print(f"F5TTS verification failed: {e}")
            return False

    def get_best_reference(self, sentence: str) -> dict:
        word_count = len(sentence.split())
        
        # Find the closest reference by word count
        best_ref_key, best_ref = min(
            self.references['references'].items(),
            key=lambda x: abs(len(x[1]['text'].split()) - word_count)
        )
        
        # Map reference keys to filenames
        filename_map = {
            "ultra_short": "utlra_short",
            "short": "short",
            "medium": "medium",
            "long_1": "long_1",
            "long_2": "long_2",
            "long_3": "long_3",
            "very_long": "very_long"
        }
        
        # Get full path to reference audio
        ref_path = self.references_folder / f"{filename_map[best_ref_key]}.wav"
        
        return {
            'text': best_ref['text'],
            'audio_path': str(ref_path)
        }

    def generate_audio(self, text: str, output_path: str, speed: float = 1.0) -> str:
        try:
            # Create temp directory if it doesn't exist
            temp_dir = Path(output_path) / "temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Split text into sentences
            sentences = re.split(r'(?<=[.!?]) +', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            audio_segments = []
            
            for i, sentence in enumerate(sentences, 1):
                print(f"\nProcessing sentence {i}/{len(sentences)}: {sentence}")
                temp_path = temp_dir / f"temp_sentence_{i}.wav"
                
                # Get best reference for this sentence
                ref = self.get_best_reference(sentence)
                
                # Build command for this sentence
                cmd = [
                    self.f5tts_cli,
                    '--model', 'F5-TTS',
                    '--ckpt_file', str(self.custom_model),
                    '--vocab_file', str(self.custom_vocab),
                    '--gen_text', sentence.lower().strip(),
                    '--ref_text', ref['text'].lower().strip(),
                    '--ref_audio', str(ref['audio_path']),
                    '--vocoder_name', 'vocos',
                    '--remove_silence', 'false',
                    '--output_dir', str(temp_dir),
                    '--speed', str(speed)
                ]

                print(f"Running command: {' '.join(cmd)}")
                
                # Run command with proper environment
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    env=env
                )
                
                if result.returncode != 0:
                    print(f"Command STDOUT: {result.stdout}")
                    print(f"Command STDERR: {result.stderr}")
                    raise Exception(f"F5TTS command failed with return code {result.returncode}")

                # Check if the output file exists
                expected_output = temp_dir / "infer_cli_out.wav"
                if not expected_output.exists():
                    raise Exception(f"Output file not found at {expected_output}")

                # Rename to our temp file name
                expected_output.rename(temp_path)
                
                # Add to audio segments
                audio_segments.append(AudioSegment.from_wav(str(temp_path)))
            
            # Combine all segments
            combined_audio = sum(audio_segments)
            
            # Save final output
            output_file = Path(output_path) / "generated_audio.wav"
            combined_audio.export(str(output_file), format="wav")
            
            # Cleanup
            for file in temp_dir.glob("temp_sentence_*.wav"):
                file.unlink()
            temp_dir.rmdir()
            
            return str(output_file)

        except Exception as e:
            print(f"F5-TTS generation failed: {str(e)}")
            raise