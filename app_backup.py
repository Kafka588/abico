import gradio as gr
import os
import subprocess
import uuid
import shutil
from typing import List, Optional
from services.f5tts_service import F5TTSService
from services.wav2lip_service import Wav2LipService
from pathlib import Path

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
        
        Args:
            text (str): Input text to speak
            avatar_image (str): Path to avatar image
            reference_audio (Optional[str]): Reference audio for voice cloning
            reference_text (Optional[str]): Reference text for voice cloning
            progress_callback (Optional[gr.Progress]): Gradio progress tracker
        
        Returns:
            str: Path to generated video
        """
        try:
            # Generate unique identifier for this generation
            job_id = str(uuid.uuid4())
            
            # Update progress
            if progress_callback:
                progress_callback(0, desc="Initializing...")
            
            # Step 1: Audio Generation (with optional voice cloning)
            if progress_callback:
                progress_callback(0.2, desc="Generating Audio...")
            audio_path = self._generate_audio(
                text, 
                reference_audio=reference_audio,
                reference_text=reference_text
            )
            
            # Step 2: Lip Synchronization
            if progress_callback:
                progress_callback(0.6, desc="Synchronizing Lips...")
            synchronized_video = self._synchronize_lips(
                avatar_image, 
                audio_path, 
                job_id
            )
            
            # Final progress
            if progress_callback:
                progress_callback(1.0, desc="Generation Complete!")
            
            return synchronized_video
        
        except Exception as e:
            print(f"Avatar generation error: {e}")
            return None
    
    def _generate_audio(
        self, 
        text: str, 
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None
    ) -> str:
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
            
            # Use F5TTS service for generation
            result = self.tts_model.generate_audio(
                text=text,
                output_path=str(self.audio_dir),
                reference_audio=reference_audio,
                reference_text=reference_text
            )
            
            # Check if the output file exists
            generated_file = self.audio_dir / "infer_cli_out.wav"
            if generated_file.exists():
                # If generated_audio.wav already exists, remove it
                if self.audio_path.exists():
                    self.audio_path.unlink()
                
                # Now rename the new file
                generated_file.rename(self.audio_path)
                print(f"Audio generated successfully at: {self.audio_path}")
                print(f"File size: {os.path.getsize(self.audio_path)} bytes")
                return str(self.audio_path)
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
        """
        Synchronize lips using Wav2Lip
        
        Args:
            avatar_path (str): Path to input image/video
            audio_path (str): Path to generated audio
            job_id (str): Unique identifier for this job
            quality (str): Quality setting for Wav2Lip
            wav2lip_version (str): Version of Wav2Lip to use
            nosmooth (bool): Whether to disable smoothing
            pad_up (int): Padding from top
            pad_down (int): Padding from bottom
            pad_left (int): Padding from left
            pad_right (int): Padding from right
        
        Returns:
            str: Path to generated video
        """
        try:
            abs_audio_path = os.path.abspath(audio_path)
            abs_avatar_path = os.path.abspath(avatar_path)
            
            if not os.path.exists(abs_audio_path):
                raise FileNotFoundError(f"Audio file not found: {abs_audio_path}")
            if not os.path.exists(abs_avatar_path):
                raise FileNotFoundError(f"Avatar file not found: {abs_avatar_path}")

            print(f"Using audio file (absolute path): {abs_audio_path}")
            print(f"Using avatar file (absolute path): {abs_avatar_path}")
            
            # Generate output path for this job
            output_video = self.output_dir / f"output_{job_id}.mp4"
            
            # Generate the talking avatar
            result_path = self.wav2lip_model.generate_talking_avatar(
                video_path=abs_avatar_path,
                audio_path=abs_audio_path,
                output_path=str(output_video),
                **kwargs
            )
            
            if not result_path or not os.path.exists(result_path):
                raise FileNotFoundError(f"Wav2Lip failed to generate output video: {result_path}")
            
            print(f"Wav2Lip output video generated at: {result_path}")
            return result_path
            
        except Exception as e:
            print(f"Lip synchronization error: {str(e)}")
            raise

def create_gradio_interface():
    # Initialize service
    avatar_service = TalkingAvatarService()
    
    def process_talking_avatar(
        text: str, 
        avatar_input: str, 
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
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
            print("\nProcessing talking avatar request:")
            print(f"Text: {text}")
            print(f"Avatar Input: {avatar_input}")
            print(f"Reference Audio: {reference_audio}")
            print(f"Reference Text: {reference_text}")
            
            # Validate inputs
            if not text:
                return None, "Please enter text to generate"
            
            if not avatar_input:
                return None, "Please upload an avatar image or video"
            
            # If reference audio is provided, reference text is required
            if reference_audio and not reference_text:
                return None, "Reference text is required when using reference audio"
            
            # Step 1: Generate audio using F5TTS
            progress(0.3, desc="Generating audio...")
            audio_path = avatar_service._generate_audio(
                text=text,
                reference_audio=reference_audio,
                reference_text=reference_text
            )
            
            if not audio_path:
                return None, "Failed to generate audio"
            
            # Step 2: Generate talking avatar using Wav2Lip
            progress(0.6, desc="Synchronizing lips...")
            video = avatar_service._synchronize_lips(
                avatar_path=avatar_input,
                audio_path=audio_path,
                job_id=str(uuid.uuid4()),
                quality=quality,
                wav2lip_version=wav2lip_version,
                nosmooth=nosmooth,
                pad_up=pad_up,
                pad_down=pad_down,
                pad_left=pad_left,
                pad_right=pad_right
            )
            
            if video:
                print(f"Video generated successfully: {video}")
                progress(1.0, desc="Processing complete!")
                return video, "Talking avatar generated successfully!"
            else:
                return None, "Failed to generate video"
                
        except Exception as e:
            error_msg = f"Error in processing: {str(e)}"
            print(error_msg)
            return None, error_msg

    # Gradio Interface
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
                
                # Reference Audio Upload
                reference_audio = gr.Audio(
                    label="Optional: Reference Audio for Voice Cloning",
                    type="filepath"
                )
                
                # Reference Text Input
                reference_text = gr.Textbox(
                    label="Reference Text (required if using reference audio)",
                    placeholder="Enter the text content of the reference audio",
                    lines=2,
                    visible=True
                )
                
                # Avatar Upload (now supports both image and video)
                avatar_upload = gr.File(
                    label="Upload Avatar Image or Video", 
                    type="filepath"
                )
                
                # Wav2Lip Options
                with gr.Accordion("Advanced Wav2Lip Options", open=False):
                    quality = gr.Radio(
                        choices=["Fast", "Improved", "Enhanced"],
                        value="Improved",
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
                reference_audio,
                reference_text,
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