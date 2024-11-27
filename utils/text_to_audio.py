# utils/text_to_audio.py

import os
from pathlib import Path
import re
from pydub import AudioSegment
from services.f5tts_service import F5TTSService

def split_text_into_sentences(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences

def generate_audio_for_text_chunks(text, reference_audio_path, output_dir):
    tts_service = F5TTSService()
    sentences = split_text_into_sentences(text)
    audio_segments = []

    # Create directory structure
    base_dir = Path(output_dir)
    sentences_dir = base_dir / "sentence_chunks"
    sentences_dir.mkdir(parents=True, exist_ok=True)

    try:
        for i, sentence in enumerate(sentences):
            print(f"Generating audio for sentence {i+1}/{len(sentences)}: {sentence}")
            
            # Create output directory for this sentence
            sentence_output_dir = sentences_dir / str(i)
            sentence_output_dir.mkdir(exist_ok=True)
            
            # Generate audio for the sentence
            sentence_audio_path = sentence_output_dir / "audio.wav"
            
            tts_service.generate_audio(
                text=sentence,
                output_path=str(sentence_output_dir),  # Pass directory path
                reference_audio=reference_audio_path
            )
            
            # The F5TTS service generates 'infer_cli_out.wav'
            generated_audio = sentence_output_dir / "infer_cli_out.wav"
            if generated_audio.exists():
                # Load the generated audio
                audio_segment = AudioSegment.from_wav(str(generated_audio))
                audio_segments.append(audio_segment)
            else:
                raise FileNotFoundError(f"Generated audio not found at {generated_audio}")

        # Concatenate all audio segments
        combined_audio = sum(audio_segments)
        
        # Save combined audio in the main output directory
        combined_output_path = base_dir / "generated_audio.wav"
        combined_audio.export(str(combined_output_path), format="wav")
        
        print(f"Combined audio saved at: {combined_output_path}")
        return str(combined_output_path)

    except Exception as e:
        print(f"Error generating audio chunks: {str(e)}")
        raise