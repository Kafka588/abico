import gradio as gr
import os
import subprocess
import uuid
from typing import List, Optional
from services.f5tts_service import F5TTSService
from pathlib import Path

class TalkingAvatarService:
    def __init__(self):
        try:
            # Initialize F5TTS service
            self.tts_model = F5TTSService()
            
            # Verify F5TTS installation
            if not self.tts_model.verify_installation():
                print("F5TTS verification failed. Please check your installation.")
                raise RuntimeError("F5TTS is not properly installed or accessible")
                
        except Exception as e:
            print(f"Error initializing TTS service: {e}")
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
            # Create temp directory if it doesn't exist
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True, parents=True)
            
            # Generate unique audio filename in temp directory
            output_dir = temp_dir / f"generated_audio_{uuid.uuid4()}"
            output_dir.mkdir(exist_ok=True, parents=True)
            
            # F5TTS will create infer_cli_out.wav inside this directory
            output_path = output_dir / "infer_cli_out.wav"
            
            print("\nGenerating audio with F5TTS:")
            print(f"Text: {text}")
            print(f"Reference Audio: {reference_audio}")
            print(f"Reference Text: {reference_text}")
            print(f"Output Directory: {output_dir}")
            
            # Use F5TTS service for generation
            result = self.tts_model.generate_audio(
                text=text,
                output_path=str(output_dir),  # Pass directory path
                reference_audio=reference_audio,
                reference_text=reference_text
            )
            
            # Check if the output file exists
            if result and output_path.exists():
                print(f"Audio generated successfully at: {output_path}")
                print(f"File size: {os.path.getsize(output_path)} bytes")
                
                # Create final output path
                final_path = temp_dir / f"{output_dir.name}.wav"
                
                # Move the file to the final location
                import shutil
                shutil.copy2(output_path, final_path)
                
                # Clean up the temporary directory
                shutil.rmtree(output_dir)
                
                return str(final_path)
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
        job_id: str
    ) -> str:
        """
        Advanced lip synchronization
        
        Args:
            avatar_path (str): Path to avatar image
            audio_path (str): Path to audio file
            job_id (str): Unique job identifier
        
        Returns:
            str: Path to synchronized video
        """
        try:
            # Generate unique output video path
            output_video = f"/tmp/talking_avatar_{job_id}.mp4"
            
            # Advanced Wav2Lip synchronization
            command = (
                f"wav2lip-advanced "
                f"--source {avatar_path} "
                f"--audio {audio_path} "
                f"--output {output_video} "
                f"--quality high"
            )
            
            subprocess.run(command, shell=True, check=True)
            return output_video
        
        except Exception as e:
            print(f"Lip synchronization error: {e}")
            return None

def create_gradio_interface():
    # Initialize service
    avatar_service = TalkingAvatarService()
    
    def process_talking_avatar(
        text: str, 
        avatar_image: str, 
        reference_audio: Optional[str] = None,
        reference_text: Optional[str] = None,
        progress: gr.Progress = gr.Progress()
    ):
        try:
            print("\nProcessing talking avatar request:")
            print(f"Text: {text}")
            print(f"Avatar Image: {avatar_image}")
            print(f"Reference Audio: {reference_audio}")
            print(f"Reference Text: {reference_text}")
            
            # Validate inputs
            if not text:
                return None, "Please enter text to generate"
            
            # If reference audio is provided, reference text is required
            if reference_audio and not reference_text:
                return None, "Reference text is required when using reference audio"
            
            # Generate audio first
            audio_path = avatar_service._generate_audio(
                text=text,
                reference_audio=reference_audio,
                reference_text=reference_text
            )
            
            if not audio_path:
                return None, "Failed to generate audio"
            
            if not avatar_image:
                # For now, just return the generated audio since avatar is not required yet
                return audio_path, "Audio generated successfully (avatar processing not implemented yet)"
            
            # Generate talking avatar
            video = avatar_service.generate_talking_avatar(
                text, 
                avatar_image, 
                reference_audio,
                reference_text,
                progress
            )
            
            if video:
                print(f"Video generated successfully: {video}")
                return video, None
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
                
                # Avatar Upload
                avatar_upload = gr.Image(
                    label="Upload Avatar Image", 
                    type="filepath"
                )
                
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
                reference_text
            ],
            outputs=[output_video, error_output]
        )
    
    return demo

# Launch the Interface
if __name__ == "__main__":
    # Create and launch the interface
    demo = create_gradio_interface()
    demo.launch(
        server_name="0.0.0.0",  
        server_port=7860,       
        share=False             
    )