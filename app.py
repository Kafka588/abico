import gradio as gr
import os
import subprocess
import uuid
import shutil
from typing import List, Optional
from pathlib import Path
from utils.text_to_audio import generate_audio_for_text_chunks  # Import the utility function
from utils.video_processor import preprocess_video_for_audio
import configparser

class TalkingAvatarService:
    def __init__(self):
        # Initialize output directory first
        self.output_dir = Path("temp/output")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Create fixed temp directory
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Fixed paths for intermediate files
        self.audio_dir = self.temp_dir / "audio"
        self.audio_dir.mkdir(exist_ok=True, parents=True)
        self.audio_path = self.audio_dir / "generated_audio.wav"
        
        # Add default reference paths
        self.defaults_dir = Path("defaults")
        self.default_ref_audio = self.defaults_dir / "reference_audio.wav"
        self.default_ref_text = "Лаборатори сургуулиудтай гурван жилийн өмнөөс гэрээ байгуулснаар манай сурлагын амжилт эрс сайжирсанд баяртай байгаа."
        
        # Add Wav2Lip paths
        self.wav2lip_dir = Path("models/Easy-Wav2Lip")
    
    def generate_talking_avatar(
        self, 
        text: str, 
        avatar_image: str, 
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        speed: float = 1.0,
        quality: str = "Improved",
        wav2lip_version: str = "Wav2Lip",
        nosmooth: bool = True,
        pad_up: int = 0,
        pad_down: int = 0,
        pad_left: int = 0,
        pad_right: int = 0,
        **kwargs
    ) -> str:
        try:
            # Validate inputs
            if not text or not text.strip():
                raise ValueError("Text input cannot be empty")
            if not avatar_image:
                raise ValueError("Avatar image/video input is required")
            if not os.path.exists(avatar_image):
                raise ValueError(f"Avatar file not found: {avatar_image}")

            # Generate audio
            progress = 0.0
            audio_path = self.generate_audio(
                text=text,
                output_path=self.audio_dir,
                reference_audio=reference_audio,
                reference_text=reference_text,
                speed=speed
            )
            
            if not audio_path:
                raise Exception("Audio generation failed")

            # Update progress
            progress = 0.5
            if kwargs.get('progress_callback'):
                kwargs['progress_callback'](progress, desc="Audio generated, starting lip sync...")
            
            # Generate talking avatar
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    video = self._synchronize_lips(
                        avatar_path=avatar_image,
                        audio_path=audio_path,
                        job_id=str(uuid.uuid4()),
                        **kwargs
                    )
                    
                    if video:
                        if kwargs.get('progress_callback'):
                            kwargs['progress_callback'](1.0, desc="Processing complete!")
                        return video
                    
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        if kwargs.get('progress_callback'):
                            kwargs['progress_callback'](progress, desc=f"Retry attempt {attempt + 2}...")
                        continue
                    else:
                        raise Exception(f"Failed after {max_retries} attempts")

            raise Exception("Failed to generate video")

        except Exception as e:
            print(f"Error in generate_talking_avatar: {str(e)}")
            raise
    
    def generate_audio(
        self, 
        text: str, 
        output_path: Path, 
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        speed: float = 1.0
    ) -> str:
        try:
            # Use defaults if not provided
            ref_audio = reference_audio if reference_audio else str(self.default_ref_audio)
            ref_text = reference_text if reference_text else self.default_ref_text

            print("\nGenerating audio with F5TTS:")
            print(f"Text: {text}")
            print(f"Reference Audio: {ref_audio}")
            print(f"Reference Text: {ref_text}")  # This should now show the default text
            print(f"Output Directory: {output_path}")

            # Generate audio using F5TTS
            audio_path = generate_audio_for_text_chunks(
                text=text,
                output_dir=output_path,
                reference_audio=ref_audio,
                reference_text=ref_text,  # Pass the actual reference text
                speed=speed
            )

            if not audio_path:
                raise Exception("Audio generation failed")

            print(f"Audio generated successfully at: {audio_path}")
            print(f"File size: {os.path.getsize(audio_path)} bytes")

            return audio_path

        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            raise
    
    def _synchronize_lips(self, avatar_path: str, audio_path: str, job_id: str, **kwargs) -> str:
        try:
            # Convert paths to absolute paths
            abs_audio_path = str(Path(audio_path).absolute())
            abs_avatar_path = str(Path(avatar_path).absolute())
            
            # Create explicit output path
            output_path = self.output_dir / f"output_{job_id}.mp4"
            output_path = str(output_path.absolute())
            
            # Create config.ini for Wav2Lip
            config = {
                'OPTIONS': {
                    'video_file': abs_avatar_path,
                    'vocal_file': abs_audio_path,
                    'output_file': output_path,  # Add explicit output path
                    'quality': kwargs.get('quality', 'Fast'),
                    'output_height': 'full resolution',
                    'wav2lip_version': kwargs.get('wav2lip_version', 'Wav2Lip'),
                    'use_previous_tracking_data': 'True',
                    'nosmooth': str(kwargs.get('nosmooth', True)).lower(),
                    'preview_window': 'False'
                },
                'PADDING': {
                    'U': str(kwargs.get('pad_up', 10)),
                    'D': str(kwargs.get('pad_down', 10)),
                    'L': str(kwargs.get('pad_left', 10)),
                    'R': str(kwargs.get('pad_right', 10))
                },
                'MASK': {
                    'size': '0.5',
                    'erosion': '2',
                    'blur': '3',
                    'threshold': '0.85',
                    'feathering': '3',
                    'mouth_tracking': 'False',
                    'debug_mask': 'False'
                },
                'OTHER': {
                    'batch_process': 'False',
                    'output_suffix': '',  # Remove suffix since we're using explicit path
                    'include_settings_in_suffix': 'False',  # Disable suffix settings
                    'preview_input': 'False',
                    'preview_settings': 'False',
                    'frame_to_preview': '0'
                }
            }
            
            # Write config file
            config_path = self.wav2lip_dir / "config.ini"
            self._write_config(config_path, config)
            
            print(f"\nRunning Wav2Lip with:")
            print(f"Avatar: {abs_avatar_path}")
            print(f"Audio: {abs_audio_path}")
            
            # Run Wav2Lip
            cmd = f'cd "{self.wav2lip_dir}" && python run.py'
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            print("\nWav2Lip STDOUT:")
            print(result.stdout)
            print("\nWav2Lip STDERR:")
            print(result.stderr)
            
            if result.returncode != 0:
                raise Exception(f"Wav2Lip failed with return code {result.returncode}: {result.stderr}")

            # Check for output file at explicit path
            if not Path(output_path).exists():
                raise FileNotFoundError(f"Output file not found at: {output_path}")
            
            return output_path

        except Exception as e:
            print(f"Lip synchronization error: {str(e)}")
            raise

    def _write_config(self, config_path: Path, config_data: dict):
        config = configparser.ConfigParser()
        for section, values in config_data.items():
            config[section] = {}
            for key, value in values.items():
                config[section][key] = str(value)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)

def create_gradio_interface():
    # Initialize service
    avatar_service = TalkingAvatarService()
    
    # Define the processing function within this scope to access avatar_service
    def process_talking_avatar(
        text: str, 
        avatar_input: str,
        use_default_ref: bool,
        custom_ref_audio: Optional[str],
        custom_ref_text: Optional[str],
        speed: float = 1.0,
        quality: str = "Improved",
        wav2lip_version: str = "Wav2Lip",
        nosmooth: bool = True,
        pad_up: int = 0,
        pad_down: int = 0,
        pad_left: int = 0,
        pad_right: int = 0
    ) -> tuple[Optional[str], str]:
        try:
            # Validate required inputs
            if not text:
                return None, "Please enter some text for the avatar to speak"
            if not avatar_input:
                return None, "Please upload an avatar image or video"

            # Print input parameters
            print("\nStarting avatar generation:")
            print(f"Input text: {text}")
            print(f"Avatar input: {avatar_input}")
            print(f"Speed: {speed}")
            print(f"Quality: {quality}")

            # Determine reference audio and text
            reference_audio = None
            reference_text = None
            
            if use_default_ref:
                reference_audio = str(avatar_service.default_ref_audio)
                reference_text = avatar_service.default_ref_text
            else:
                reference_audio = custom_ref_audio
                reference_text = custom_ref_text

            # Generate the talking avatar
            video = avatar_service.generate_talking_avatar(
                text=text,
                avatar_image=avatar_input,
                reference_audio=reference_audio,
                reference_text=reference_text,
                speed=speed,
                quality=quality,
                wav2lip_version=wav2lip_version,
                nosmooth=nosmooth,
                pad_up=pad_up,
                pad_down=pad_down,
                pad_left=pad_left,
                pad_right=pad_right
            )
            
            if video:
                return video, "Talking avatar generated successfully!"
            else:
                return None, "Failed to generate video"

        except Exception as e:
            error_msg = f"Error in processing: {str(e)}"
            print(f"\nDetailed error information:")
            print(error_msg)
            import traceback
            print(traceback.format_exc())
            return None, error_msg

    # Create the interface
    with gr.Blocks() as demo:
        gr.Markdown("# Advanced Talking Avatar Generator")
        
        with gr.Row():
            with gr.Column():
                # Text Input
                text_input = gr.Textbox(
                    label="Enter Text", 
                    placeholder="What should the avatar say?",
                    lines=3,
                    interactive=True
                )
                
                # Avatar Upload
                avatar_upload = gr.File(
                    label="Upload Avatar Image or Video", 
                    type="filepath"
                )
                
                # Add F5TTS Options accordion
                with gr.Accordion("Advanced F5TTS Options", open=False) as f5tts_options:
                    # Speed slider
                    speed_slider = gr.Slider(
                        minimum=0.5,
                        maximum=2.0,
                        value=1.0,
                        step=0.1,
                        label="Speech Speed"
                    )
                    
                    # Reference Voice Options
                    gr.Markdown("### Reference Voice Options")
                    use_default_ref = gr.Checkbox(
                        value=True,
                        label="Use Default Reference Voice",
                        interactive=True
                    )
                    
                    # Default reference info
                    default_ref_info = gr.Markdown(
                        value=f"Using default reference audio: {avatar_service.default_ref_audio.name}\n" +
                              f"Default reference text: {avatar_service.default_ref_text}",
                        visible=True
                    )
                    
                    # Custom reference options
                    reference_audio = gr.Audio(
                        label="Custom Reference Audio",
                        type="filepath",
                        interactive=True,
                        visible=False  # Initially hidden
                    )
                    reference_text = gr.Textbox(
                        label="Custom Reference Text",
                        placeholder="Enter the text content of the reference audio",
                        lines=2,
                        interactive=True,
                        visible=False  # Initially hidden
                    )
                    
                    # Add visibility toggle for reference options
                    def toggle_ref_options(use_default):
                        return [
                            gr.update(visible=use_default),  # default_ref_info
                            gr.update(visible=not use_default),  # reference_audio
                            gr.update(visible=not use_default)   # reference_text
                        ]
                    
                    use_default_ref.change(
                        fn=toggle_ref_options,
                        inputs=[use_default_ref],
                        outputs=[
                            default_ref_info,
                            reference_audio,
                            reference_text
                        ]
                    )
                
                # Existing Wav2Lip Options accordion
                with gr.Accordion("Advanced Wav2Lip Options", open=False):
                    quality = gr.Radio(
                        choices=["Fast", "Improved", "Enhanced"],
                        value="Enhanced",
                        label="Quality"
                    )
                    wav2lip_version = gr.Radio(
                        choices=["Wav2Lip", "Wav2Lip_GAN"],
                        value="Wav2Lip",
                        label="Wav2Lip Version"
                    )
                    nosmooth = gr.Checkbox(
                        value=True,
                        label="No Smooth (better for quick movements)"
                    )
                    pad_up = gr.Number(value=0, label="Pad Up")
                    pad_down = gr.Number(value=0, label="Pad Down")
                    pad_left = gr.Number(value=0, label="Pad Left")
                    pad_right = gr.Number(value=0, label="Pad Right")
                
                # Generate Button
                generate_btn = gr.Button("Generate Talking Avatar", variant="primary")
        
        with gr.Row():
            # Output Components
            output_video = gr.Video(label="Generated Talking Avatar")
            error_output = gr.Textbox(label="Status/Errors", visible=True)
        
        # Modify the process_talking_avatar function to handle validation
        def process_with_validation(*args):
            # Extract text and avatar from args
            text = args[0]
            avatar = args[1]
            
            # Validate inputs
            if not text or not text.strip():
                return None, "Please enter some text for the avatar to speak"
            if not avatar:
                return None, "Please upload an avatar image or video"
                
            # If validation passes, call the original process function
            return process_talking_avatar(*args)

        # Event Handling
        generate_btn.click(
            fn=process_with_validation,  # Use the wrapper function instead
            inputs=[
                text_input, 
                avatar_upload,
                use_default_ref,
                reference_audio,
                reference_text,
                speed_slider,
                quality,
                wav2lip_version,
                nosmooth,
                pad_up,
                pad_down,
                pad_left,
                pad_right
            ],
            outputs=[output_video, error_output]
        )
    
    return demo

# Launch the Interface
if __name__ == "__main__":
    # Create and launch the interface
    demo = create_gradio_interface()
    demo.launch(
        server_name="127.0.0.1",  
        server_port=7860,       
        share=False             
    )