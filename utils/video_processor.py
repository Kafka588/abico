import cv2
import numpy as np
from pathlib import Path
from typing import Optional
import librosa

def preprocess_video_for_audio(video_path: str, audio_path: str, output_path: Optional[str] = None) -> str:
    """
    Preprocess video to match audio length by creating a smooth loop
    
    Args:
        video_path: Path to input video
        audio_path: Path to audio file (to get duration)
        output_path: Optional path for output video. If None, creates one in temp directory
    
    Returns:
        str: Path to processed video
    """
    try:
        # Get audio duration
        audio_duration = librosa.get_duration(path=audio_path)
        
        # Convert paths to absolute paths
        video_path = str(Path(video_path).absolute())
        
        # Create output path if not provided
        if output_path is None:
            output_path = str(Path(video_path).parent / f"preprocessed_{Path(video_path).stem}.mp4")
        output_path = str(Path(output_path).absolute())
        
        # Open the video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate required number of frames for audio duration
        required_frames = int(audio_duration * fps)
        
        # Read all frames
        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        
        # Set up video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(output_path), fourcc, fps, (frame_width, frame_height))
        
        # First, write the entire video
        current_frames = 0
        for frame in frames:
            out.write(frame)
            current_frames += 1
        
        # If we need more frames, add reversed sequences
        while current_frames < required_frames:
            # Skip first and last frame in reverse to avoid stuttering
            for frame in reversed(frames[1:-1]):
                if current_frames >= required_frames:
                    break
                out.write(frame)
                current_frames += 1
            
            # If we still need more frames, go forward again
            if current_frames < required_frames:
                for frame in frames:
                    if current_frames >= required_frames:
                        break
                    out.write(frame)
                    current_frames += 1
        
        cap.release()
        out.release()
        
        print(f"Successfully preprocessed video: {output_path}")
        print(f"Original frames: {len(frames)}, Required frames: {required_frames}, Generated frames: {current_frames}")
        return str(output_path)
        
    except Exception as e:
        print(f"Error in video preprocessing: {str(e)}")
        raise