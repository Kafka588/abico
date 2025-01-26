import gradio as gr
from f5_tts.api import F5TTS
import time
from pathlib import Path
import re
from pydub import AudioSegment
import json
import platform
import os

def get_base_path():
    system = platform.system()
    if system == "Windows":
        return Path(os.path.dirname(os.path.abspath(__file__)))
    elif system == "Linux":
        return Path("/path/to/your/linux/base/directory")  # Update this with your Linux path
    else:
        return Path(os.path.dirname(os.path.abspath(__file__)))

# Get base path based on OS
base_path = get_base_path()
model_folder = base_path / "models" / "F5-TTS" / "custom_models" / "mongolian"
references_folder = base_path / "references"

class F5TTSService:
    def __init__(self):
        # Ensure directories exist
        model_folder.mkdir(parents=True, exist_ok=True)
        references_folder.mkdir(parents=True, exist_ok=True)

        self.model_path = model_folder / "model_226800.pt"
        self.vocab_path = model_folder / "vocab.txt"
        self.references_folder = references_folder
        self.use_ema = True
        
        # Check if required files exist
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        if not self.vocab_path.exists():
            raise FileNotFoundError(f"Vocab file not found at {self.vocab_path}")
        
        # Load reference configurations
        config_path = references_folder / "config.json"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
            
        with open(config_path, 'r', encoding='utf-8') as f:
            self.references = json.load(f)
        
        self.tts = F5TTS(
            model_type="F5-TTS",
            ckpt_file=str(self.model_path),
            vocab_file=str(self.vocab_path),
            use_ema=self.use_ema
        )

    def get_best_reference(self, sentence: str) -> dict:
        word_count = len(sentence.split())
        
        # Find the closest reference by word count
        best_ref_key, best_ref = min(
            self.references['references'].items(),
            key=lambda x: abs(len(x[1]['text'].split()) - word_count)
        )
        
        # Map reference keys to filenames
        filename_map = {
            "ultra_short": "ultra_short",
            "short": "short",
            "medium": "medium",
            "long_1": "long_1",
            "long_2": "long_2",
            "long_3": "long_3",
            "very_long": "long_4"
        }
        
        # Get full path to reference audio
        ref_path = self.references_folder / f"{filename_map[best_ref_key]}.wav"
        
        return {
            'text': best_ref['text'],
            'audio_path': str(ref_path)
        }

    def generate_speech(self, text: str, speed: float = 1.0, nfe_steps: int = 32) -> tuple:
        try:
            # Create temp directory if it doesn't exist
            temp_dir = base_path / "temp"
            temp_dir.mkdir(exist_ok=True)
            
            # Split text into sentences
            sentences = re.split(r'(?<=[.!?]) +', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            audio_segments = []
            total_time = 0
            
            for i, sentence in enumerate(sentences, 1):
                print(f"\nProcessing sentence {i}/{len(sentences)}: {sentence}")
                temp_path = temp_dir / f"temp_sentence_{i}.wav"
                start_time = time.time()
                
                ref = self.get_best_reference(sentence)
                
                self.tts.infer(
                    gen_text=sentence.lower().strip(),
                    ref_text=ref['text'].lower().strip(),
                    ref_file=ref['audio_path'],
                    nfe_step=nfe_steps,
                    file_wave=str(temp_path),
                    speed=speed
                )
                
                sentence_time = time.time() - start_time
                total_time += sentence_time
                
                audio_segments.append(AudioSegment.from_wav(str(temp_path)))
                print(f"Sentence {i} generated in {sentence_time:.2f} seconds")
            
            # Combine and save
            output_path = base_path / "output.wav"
            combined_audio = sum(audio_segments)
            combined_audio.export(str(output_path), format="wav")
            
            # Cleanup
            for file in temp_dir.glob("temp_sentence_*.wav"):
                file.unlink()
            
            return str(output_path), f"Generated {len(sentences)} sentences in {total_time:.2f} seconds"
            
        except Exception as e:
            return None, f"Error: {str(e)}"

def demo():
    service = F5TTSService()
    
    demo = gr.Blocks()
    
    with demo:
        gr.Markdown("# F5-TTS Demo with Multiple References")
        
        with gr.Row():
            with gr.Column():
                text = gr.Textbox(
                    label="Text to speak", 
                    lines=3,
                    placeholder="Enter the text you want to convert to speech"
                )
                
        with gr.Row():
            with gr.Column():
                speed = gr.Slider(0.5, 2.0, 1.0, label="Speed")
                nfe = gr.Slider(1, 100, 32, label="NFE Steps")
                btn = gr.Button("Generate")
                
        with gr.Row():
            audio = gr.Audio(label="Output")
            status = gr.Textbox(label="Status")
        
        btn.click(
            service.generate_speech,
            inputs=[text, speed, nfe],
            outputs=[audio, status]
        )
    
    return demo

if __name__ == "__main__":
    demo().launch(server_name="127.0.0.1", server_port=7860)