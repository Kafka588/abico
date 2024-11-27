# utils/text_to_audio.py

import os
from pathlib import Path
import re
from pydub import AudioSegment
from services.f5tts_service import F5TTSService
from typing import Optional, Union

def split_text_into_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences

def generate_audio_for_text_chunks(
    text: str,
    output_dir: Union[str, Path],
    reference_audio: Optional[str] = None,
    reference_text: Optional[str] = None,
    speed: float = 1.0
) -> Optional[str]:
    try:
        # Ensure output directory exists
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create chunks directory
        chunks_dir = output_dir / "sentence_chunks"
        chunks_dir.mkdir(exist_ok=True)

        # Generate audio for the text
        print(f"Generating audio for sentence 1/1: {text}")
        
        # Build F5TTS command with proper reference text
        cmd = [
            f'"{get_f5tts_executable()}"',
            '--model "F5-TTS"',
            f'--ckpt_file "{get_model_path()}"',
            f'--vocab_file "{get_vocab_path()}"',
            f'--gen_text "{text}"',
            '--vocoder_name vocos',
            '--remove_silence false',
            f'--output_dir "{chunks_dir / "0"}"',
            f'--speed {speed}',
            f'--ref_audio "{reference_audio}"'
        ]
        
        # Add reference text if provided
        if reference_text:
            cmd.append(f'--ref_text "{reference_text}"')

        f5tts_cmd = " ".join(cmd)
        print(f"Running F5TTS command: {f5tts_cmd}")

        # Rest of the function...

    except Exception as e:
        print(f"Error generating audio chunks: {str(e)}")
        raise