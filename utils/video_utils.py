"""
A module for reading and writing video files.

This module provides utility functions to load video frames into memory and save
processed frames back to video files, with support for common video formats.
"""

import cv2
import os

try:
    import imageio
except Exception:
    imageio = None

def read_video(video_path):
    """
    Read all frames from a video file into memory.

    Args:
        video_path (str): Path to the input video file.

    Returns:
        list: List of video frames as numpy arrays.
    """
    # Check file existence early to provide clearer messages
    if not os.path.exists(video_path):
        parent = os.path.dirname(video_path) or '.'
        try:
            files = os.listdir(parent)
        except Exception:
            files = []

        basename = os.path.basename(video_path)
        stem = os.path.splitext(basename)[0]
        # Try to find a close match if user passed a slightly different name
        candidates = [f for f in files if stem in f]
        if len(candidates) == 1:
            fallback = os.path.join(parent, candidates[0])
            print(f"read_video: exact file not found, using detected file {fallback}")
            video_path = fallback
        else:
            print(f"read_video: file not found: {video_path}\nAvailable files in {parent}: {files}")
            if candidates:
                print(f"Similar files: {candidates} (no automatic selection)\n")
            return []

    cap = cv2.VideoCapture(video_path)
    frames = []

    if not cap.isOpened():
        # OpenCV couldn't open the file; try imageio as a fallback if available
        if imageio is not None:
            try:
                reader = imageio.get_reader(video_path)
                for frame in reader:
                    # imageio returns RGB; convert to BGR for OpenCV compatibility
                    try:
                        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    except Exception:
                        frame_bgr = frame
                    frames.append(frame_bgr)
                return frames
            except Exception as e:
                print(f"read_video: imageio failed to read {video_path}: {e}")
                return []
        else:
            print(f"read_video: OpenCV couldn't open {video_path} and imageio is not available.\n" \
                  "Install imageio (pip install imageio imageio-ffmpeg) or convert the video to a supported codec.")
            return []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames

def save_video(ouput_video_frames,output_video_path):
    """
    Save a sequence of frames as a video file.

    Creates necessary directories if they don't exist and writes frames using XVID codec.

    Args:
        ouput_video_frames (list): List of frames to save.
        output_video_path (str): Path where the video should be saved.
    """
    # If no frames, warn and skip writing to avoid IndexError
    if not ouput_video_frames:
        print(f"save_video: no frames to write to {output_video_path}")
        return

    # If folder doesn't exist, create it (only when dirname is non-empty)
    out_dir = os.path.dirname(output_video_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video_path, fourcc, 24, (ouput_video_frames[0].shape[1], ouput_video_frames[0].shape[0]))
    for frame in ouput_video_frames:
        out.write(frame)
    out.release()