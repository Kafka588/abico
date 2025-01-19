import gradio as gr
from f5_tts.api import F5TTS
import time
from pathlib import Path
import re
from pydub import AudioSegment
import json

class F5TTSService:
    def __init__(self):
        self.model_path = "model_226800.pt"
        self.vocab_path = "vocab.txt"
        self.references_folder = "references"
        self.use_ema = True
        
        # Load reference configurations
        with open('references/config.json', 'r', encoding='utf-8') as f:
            self.references = json.load(f)
        
        self.tts = F5TTS(
            model_type="F5-TTS",
            ckpt_file=self.model_path,
            vocab_file=self.vocab_path,
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
            "ultra_short": "speaker_353_segment_989",
            "short": "speaker_353_segment_99",
            "medium": "speaker_353_segment_228",
            "long_1": "speaker_353_segment_969_967",
            "long_2": "speaker_353_segment_625_620",
            "long_3": "speaker_353_segment_746_738_763",
            "very_long": "speaker_353_segment_587_674_708_717"
        }
        
        # Get full path to reference audio
        ref_path = Path(self.references_folder) / f"{filename_map[best_ref_key]}.wav"
        
        return {
            'text': best_ref['text'],
            'audio_path': str(ref_path)
        }

    def generate_speech(self, text: str, speed: float = 1.0, nfe_steps: int = 32) -> tuple:
        try:
            # Split text into sentences
            sentences = re.split(r'(?<=[.!?]) +', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            audio_segments = []
            total_time = 0
            
            for i, sentence in enumerate(sentences, 1):
                print(f"\nProcessing sentence {i}/{len(sentences)}: {sentence}")
                temp_path = f"temp_sentence_{i}.wav"
                start_time = time.time()
                
                # Get best matching reference for this sentence
                ref = self.get_best_reference(sentence)
                
                self.tts.infer(
                    gen_text=sentence.lower().strip(),
                    ref_text=ref['text'].lower().strip(),
                    ref_file=ref['audio_path'],
                    nfe_step=nfe_steps,
                    file_wave=temp_path,
                    speed=speed
                )
                
                sentence_time = time.time() - start_time
                total_time += sentence_time
                
                audio_segments.append(AudioSegment.from_wav(temp_path))
                print(f"Sentence {i} generated in {sentence_time:.2f} seconds")
            
            # Combine and save
            output_path = "output.wav"
            combined_audio = sum(audio_segments)
            combined_audio.export(output_path, format="wav")
            
            # Cleanup
            for i in range(len(sentences)):
                temp_file = Path(f"temp_sentence_{i+1}.wav")
                if temp_file.exists():
                    temp_file.unlink()
            
            return output_path, f"Generated {len(sentences)} sentences in {total_time:.2f} seconds"
            
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