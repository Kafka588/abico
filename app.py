import gradio as gr
import os
import subprocess
import uuid
import shutil
from typing import List, Optional
from services.f5tts_service import F5TTSService
from services.wav2lip_service import Wav2LipService
from pathlib import Path
from utils.text_to_audio import generate_audio_for_text_chunks  # Import the utility function
from utils.video_processor import preprocess_video_for_audio

class TalkingAvatarService:
    def __init__(self):
        # Initialize output directory first
        self.output_dir = Path("temp/output")
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Then initialize the models
        self.tts_model = F5TTSService()
        self.wav2lip_model = Wav2LipService()
        
        # Create fixed temp directory
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Fixed paths for intermediate files
        self.audio_dir = self.temp_dir / "audio"
        self.audio_dir.mkdir(exist_ok=True, parents=True)
        self.audio_path = self.audio_dir / "generated_audio.wav"
        
        # Verify F5TTS installation
        if not self.tts_model.verify_installation():
            print("F5TTS verification failed. Please check your installation.")
            raise RuntimeError("F5TTS is not properly installed or accessible")
                
        # Add default reference paths
        self.defaults_dir = Path("defaults")
        self.default_ref_audio = self.defaults_dir / "reference_audio.wav"
        self.default_ref_text = "Лаборатори сургуулиудтай гурван жилийн өмнөөс гэрээ байгуулснаар манай сурлагын амжилт эрс сайжирсанд баяртай байгаа."
        
    def generate_talking_avatar(
        self, 
        text: str, 
        avatar_image: str, 
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        progress_callback: Optional[gr.Progress] = None
    ) -> str:
        """
        Comprehensive method to generate a talking avatar
        """
        try:
            print("\nProcessing talking avatar request:")
            print(f"Text: {text}")
            print(f"Avatar Input: {avatar_image}")
            print(f"Reference Audio: {reference_audio}")
            print(f"Reference Text: {reference_text}")

            # Step 1: Generate audio using F5TTS
            if progress_callback is not None:
                progress_callback(0.3, desc="Generating audio...")
            
            audio_path = self._generate_audio(
                text=text,
                reference_audio=reference_audio,
                reference_text=reference_text
            )
            
            if not audio_path:
                raise Exception("Audio generation failed")

            # Step 2: Generate talking avatar using Wav2Lip
            if progress_callback is not None:
                progress_callback(0.6, desc="Synchronizing lips...")
                
            # Add retry logic for Wav2Lip
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    video = self._synchronize_lips(
                        avatar_path=avatar_image,
                        audio_path=audio_path,
                        job_id=str(uuid.uuid4()),
                        quality="Enhanced",  # Use faster processing to reduce potential face detection issues
                        wav2lip_version="Wav2Lip",  # Use standard Wav2Lip instead of GAN version
                        nosmooth=True,  # Keep nosmooth for better frame-by-frame sync
                        pad_up=10,      # Add some padding to help with face detection
                        pad_down=10,
                        pad_left=10,
                        pad_right=10
                    )
                    
                    if video:
                        print(f"Video generated successfully: {video}")
                        if progress_callback is not None:
                            progress_callback(1.0, desc="Processing complete!")
                        return video
                    
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        print("Retrying...")
                        continue
                    else:
                        raise Exception(f"Failed after {max_retries} attempts")

            raise Exception("Failed to generate video")

        except Exception as e:
            error_msg = f"Error in processing: {str(e)}"
            print(error_msg)
            raise
    
    def _generate_audio(
        self, 
        text: str, 
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        speed: float = 1.0
    ) -> Optional[str]:
        """
        Advanced audio generation with F5TTS
        
        Args:
            text (str): Text to convert to speech
            reference_audio (Optional[str]): Reference audio for voice style
            reference_text (Optional[str]): Reference text for voice cloning
        
        Returns:
            str: Path to generated audio file
        """
        try:
            print("\nGenerating audio with F5TTS:")
            print(f"Text: {text}")
            print(f"Reference Audio: {reference_audio}")
            print(f"Reference Text: {reference_text}")
            print(f"Output Directory: {self.audio_dir}")
            
            # Use the utility function to handle sentence splitting and audio generation
            combined_audio_path = generate_audio_for_text_chunks(
                text=text,
                reference_audio_path=reference_audio,
                output_dir=str(self.audio_dir)
            )
            
            if combined_audio_path:
                print(f"Audio generated successfully at: {combined_audio_path}")
                print(f"File size: {os.path.getsize(combined_audio_path)} bytes")
                return combined_audio_path
            else:
                print("Audio generation failed!")
                return None
                
        except Exception as e:
            print(f"Audio generation error: {e}")
            return None
    
    def _synchronize_lips(
        self,
        avatar_path: str,
        audio_path: str,
        job_id: str,
        **kwargs
    ) -> str:
        try:
            # Convert paths to absolute paths
            abs_audio_path = str(Path(audio_path).absolute())
            abs_avatar_path = str(Path(avatar_path).absolute())
            
            if not Path(abs_audio_path).exists():
                raise FileNotFoundError(f"Audio file not found: {abs_audio_path}")
            if not Path(abs_avatar_path).exists():
                raise FileNotFoundError(f"Avatar file not found: {abs_avatar_path}")

            print(f"Using audio file (absolute path): {abs_audio_path}")
            print(f"Using avatar file (absolute path): {abs_avatar_path}")
            
            # Create preprocessed video path with absolute path
            preprocessed_video = self.temp_dir / f"preprocessed_{job_id}.mp4"
            preprocessed_video = preprocessed_video.absolute()
            
            # Ensure temp directory exists
            preprocessed_video.parent.mkdir(parents=True, exist_ok=True)
            
            # Preprocess video
            processed_avatar_path = preprocess_video_for_audio(
                video_path=abs_avatar_path,
                audio_path=abs_audio_path,
                output_path=str(preprocessed_video)
            )
            
            if not Path(processed_avatar_path).exists():
                raise FileNotFoundError(f"Preprocessed video not found: {processed_avatar_path}")
            
            # Generate output path for this job
            output_video = self.output_dir / f"output_{job_id}.mp4"
            output_video = output_video.absolute()
            
            # Generate the talking avatar using preprocessed video
            result_path = self.wav2lip_model.generate_talking_avatar(
                video_path=processed_avatar_path,
                audio_path=abs_audio_path,
                output_path=str(output_video),
                **kwargs
            )
            
            # Clean up preprocessed video
            try:
                if Path(processed_avatar_path).exists():
                    Path(processed_avatar_path).unlink()
            except Exception as e:
                print(f"Warning: Failed to clean up preprocessed video: {e}")
            
            if not result_path or not Path(result_path).exists():
                raise FileNotFoundError(f"Wav2Lip failed to generate output video: {result_path}")
            
            print(f"Wav2Lip output video generated at: {result_path}")
            return str(result_path)
            
        except Exception as e:
            print(f"Lip synchronization error: {str(e)}")
            raise

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
    pad_right: int = 0,
    progress: gr.Progress = gr.Progress()
):
    try:
        # Initialize service if not already initialized
        avatar_service = TalkingAvatarService()
        
        # Input validation
        if not text:
            return None, "Please provide input text"
        if not avatar_input:
            return None, "Please provide an avatar video/image"

        # Handle reference audio and text
        try:
            if use_default_ref:
                # Check if default reference exists
                if not avatar_service.default_ref_audio.exists():
                    return None, f"Default reference audio not found at {avatar_service.default_ref_audio}"
                reference_audio = str(avatar_service.default_ref_audio)
                reference_text = avatar_service.default_ref_text
            else:
                # Validate custom reference
                if not custom_ref_audio:
                    return None, "Please provide a custom reference audio file"
                if not custom_ref_text:
                    return None, "Please provide the text content of the reference audio"
                reference_audio = custom_ref_audio
                reference_text = custom_ref_text

            print(f"\nReference settings:")
            print(f"Using default reference: {use_default_ref}")
            print(f"Reference audio path: {reference_audio}")
            print(f"Reference text: {reference_text}")

        except Exception as e:
            print(f"Error setting up references: {str(e)}")
            return None, f"Error with reference setup: {str(e)}"

        # Generate the talking avatar
        print("\nStarting avatar generation:")
        print(f"Input text: {text}")
        print(f"Avatar input: {avatar_input}")
        print(f"Speed: {speed}")
        print(f"Quality: {quality}")

        video = avatar_service.generate_talking_avatar(
            text=text,
            avatar_image=avatar_input,
            reference_audio=reference_audio,
            reference_text=reference_text,
            progress_callback=progress
        )
        
        if video:
            print(f"Successfully generated video at: {video}")
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

def create_gradio_interface():
    # Initialize service
    avatar_service = TalkingAvatarService()
    
    with gr.Blocks() as demo:
        gr.Markdown("# Advanced Talking Avatar Generator")
        
        with gr.Row():
            with gr.Column():
                # Text Input
                text_input = gr.Textbox(
                    label="Enter Text", 
                    placeholder="What should the avatar say?",
                    lines=3
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
        
        # Event Handling
        generate_btn.click(
            fn=process_talking_avatar,
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