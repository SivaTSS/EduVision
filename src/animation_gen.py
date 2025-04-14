import os
import json
import subprocess
import sys
from pathlib import Path
from typing import List
import yaml
import glob
import shutil

from llm_loader import llm

# Directories.
BASE_OUTPUT_DIR = Path("outputs")
VIDEO_DIR = BASE_OUTPUT_DIR / "videos"
AUDIO_DIR = BASE_OUTPUT_DIR / "audio"
FINAL_DIR = BASE_OUTPUT_DIR / "final"
TEMP_DIR = BASE_OUTPUT_DIR / "temp"

for folder in [BASE_OUTPUT_DIR, VIDEO_DIR, AUDIO_DIR, FINAL_DIR, TEMP_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Adjust this path if your Manim outputs are located elsewhere.
MANIM_MEDIA_DIR = Path("media") / "videos" / "temp_manim_script" / "720p30"

def generate_yaml_outline(topic_text: str) -> List[str]:
    """
    Ask the LLM to create an outline for a Manim animation based on a topic,
    and output it as a YAML list. Each item represents a self-contained animatable step.
    
    The prompt ensures:
      - The first item is a title slide explicitly labeled as "Title Slide".
      - Each step is focused, independent, and suitable for 2D Manim animations.
    """
    prompt = f"""
Create a structured YAML list for a 2D Manim animation on the topic: **"{topic_text}"**.

- The **first item** must be a **title slide** labeled as: **"Title Slide: {topic_text}"** with short, concise content.
- Each following item should describe **one self-contained animation step** with concise text.
- Steps must be **clear, independent**, and **suitable for 2D animations only** (no 3D elements).
- Each step and the title slide should be succinct, avoiding overly long descriptions.
- **Important:** Ensure that any colons (:) in the YAML output are properly escaped or enclosed in quotes to avoid parsing errors.

Return only a **valid YAML list** without extra formatting or explanations.
"""
    response = llm.invoke(prompt)
    outline_yaml = response.content.strip()
    
    # Remove YAML code fences if present.
    if outline_yaml.startswith("```yaml"):
        outline_yaml = outline_yaml.split("```yaml", 1)[1]
    if outline_yaml.endswith("```"):
        outline_yaml = outline_yaml.rsplit("```", 1)[0]
    
    try:
        outline = yaml.safe_load(outline_yaml)
        if not isinstance(outline, list):
            raise ValueError("Outline is not a list")
    except Exception as e:
        raise ValueError(f"Failed to parse YAML outline: {e}")
    
    # Save the outline to a YAML file inside the outputs folder.
    outline_path = BASE_OUTPUT_DIR / "animation_outline.yaml"
    with open(outline_path, "w", encoding="utf-8") as f:
        yaml.dump(outline, f)
    
    print(f"✅ YAML Outline saved to {outline_path}")
    return outline


def generate_manim_code_for_step(step_description: str) -> str:
    """
    Generate a self-contained Manim Python script for a single step.
    The output is raw Python code (no markdown fences or extra commentary).
    """
    prompt = f"""
You are an expert in Manim. Given the step description below,
produce a valid, self-contained, and runnable Manim Python script that implements this step.
Provide only the Python code (do not wrap your answer in markdown code fences or include extra commentary).

Step Description:
{step_description}

Your response should contain only the executable Python code.
"""
    response = llm.invoke(prompt)
    code = response.content.strip()
    if code.startswith("```python"):
        code = code.split("```python", 1)[1]
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]
    return code.strip()


def iterative_debug(code: str, full_error: str, max_attempts: int = 3) -> str:
    """
    Iteratively ask the LLM for a corrected version of the code based on the full error traceback.
    """
    current_code = code
    for attempt in range(1, max_attempts + 1):
        print(f"Full error traceback:\n{full_error}\n")
        prompt = f"""
Aim:
Fix the Manim code so that it runs correctly and generates the intended animation.

Current Code:
{current_code}

Full Error Traceback:
{full_error}
        
Please provide a corrected version of the above code that fixes the error.
Output only the raw Python code (no markdown or additional commentary).
"""
        response = llm.invoke(prompt, max_tokens=1500)
        corrected_code = response.content.strip()
        if corrected_code.startswith("```python"):
            corrected_code = corrected_code.split("```python", 1)[1]
        if corrected_code.endswith("```"):
            corrected_code = corrected_code.rsplit("```", 1)[0]
        current_code = corrected_code.strip()
        print(f"\nAttempt {attempt}: Updated Code\n{'-'*40}\n{current_code}\n{'-'*40}\n")
    return current_code


def run_manim_script(manim_code: str, output_filename: str) -> Path:
    """
    Write the Manim code to a temporary file, run it via subprocess,
    and then copy the generated video from the default Manim output directory
    to our designated VIDEO_DIR.
    
    Returns the new path to the copied video file.
    """
    temp_script_path = TEMP_DIR / "temp_manim_script.py"
    with open(temp_script_path, "w", encoding="utf-8") as f:
        f.write(manim_code)
    
    cmd = [
        sys.executable,
        "-m", "manim",
        str(temp_script_path),
        "-qm",
        "-o", output_filename
    ]
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Manim animation generated with base name: {output_filename}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Manim failed: {e}")
    
    # Construct expected path using glob search.
    pattern = str(MANIM_MEDIA_DIR / f"*{output_filename}*")
    matching_files = glob.glob(pattern)
    if not matching_files:
        raise FileNotFoundError(f"Could not find generated video matching {pattern}")
    
    generated_video = Path(matching_files[0])
    dest_video = VIDEO_DIR / generated_video.name
    shutil.copy(generated_video, dest_video)
    print(f"✅ Copied video to: {dest_video}")
    return dest_video


def generate_dialogue_for_step(step_description: str) -> str:
    """
    Generate a short narration line (1-2 sentences) for the step.
    Do not include any timestamps; provide only the voiceover text.
    """
    prompt = f"""
You are an expert in educational narration. Given the following step description,
provide a short narration line (1-2 sentences) for the step.
Do not include any timestamps or extraneous labels; just provide the voiceover text.

Step Description:
{step_description}
"""
    response = llm.invoke(prompt)
    dialogue_line = response.content.strip()
    return dialogue_line


# Text-to-Speech Conversion (TTS)
from gtts import gTTS

def text_to_speech(text: str, output_audio: Path):
    """
    Convert the provided text to speech using gTTS and save as an MP3 file.
    """
    tts = gTTS(text=text, lang="en")
    tts.save(str(output_audio))
    print(f"Generated TTS audio saved to: {output_audio}")


import ffmpeg
import cv2
import numpy as np

def get_duration(filepath: Path) -> float:
    """
    Returns the duration of a media file in seconds using ffmpeg.probe.
    """
    probe = ffmpeg.probe(str(filepath))
    return float(probe["format"]["duration"])

def is_last_frame_black(video_path: Path, threshold: float = 10) -> bool:
    """
    Checks if the last frame of the video is completely black.
    Uses OpenCV to grab the last frame and computes its average brightness.
    If the average brightness is below the threshold, we consider it black.
    """
    cap = cv2.VideoCapture(str(video_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames == 0:
        cap.release()
        return False
    # Move to the last frame.
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None:
        return False
    avg_brightness = np.mean(frame)
    return avg_brightness < threshold

def combine_audio_and_video(video_path: Path, audio_path: Path, final_output_filename: str) -> Path:
    """
    Combines video and audio so that:
      - If the video is longer than the audio, the audio is padded with silence.
      - If the audio is longer than the video, the video is extended by freezing its last frame.
    
    Additionally, if the video’s last frame is completely black, then when the audio is longer,
    we trim (or extend) the video to exactly match the audio duration.
    
    This function uses ffmpeg-python so no raw command line calls are made.
    """
    final_output = FINAL_DIR / final_output_filename
    
    video_duration = get_duration(video_path)
    audio_duration = get_duration(audio_path)
    
    last_frame_black = is_last_frame_black(video_path)
    
    video_in = ffmpeg.input(str(video_path))
    audio_in = ffmpeg.input(str(audio_path))
    
    if audio_duration > video_duration:
        pad_duration = audio_duration - video_duration
        video_filtered = video_in.video.filter('tpad', stop_mode='clone', stop_duration=pad_duration)
        audio_filtered = audio_in.audio
    elif video_duration > audio_duration:
        if last_frame_black:
            video_filtered = video_in.video.filter('trim', duration=audio_duration).filter('setpts', 'PTS-STARTPTS')
            audio_filtered = audio_in.audio
        else:
            pad_duration = video_duration - audio_duration
            video_filtered = video_in.video
            audio_filtered = audio_in.audio.filter('apad', pad_dur=pad_duration)
    else:
        video_filtered = video_in.video
        audio_filtered = audio_in.audio

    out = ffmpeg.output(video_filtered, audio_filtered, str(final_output),
                        vcodec='libx264', acodec='aac', strict='experimental')
    ffmpeg.run(out, quiet=True)
    
    return final_output


def concatenate_videos(video_files: List[str], final_output: str):
    """
    Concatenate multiple video files into one final video using ffmpeg.
    """
    # Create the file list inside the outputs directory.
    list_filename = BASE_OUTPUT_DIR / "videos_to_concat.txt"
    with open(list_filename, "w", encoding="utf-8") as f:
        for vf in video_files:
            f.write(f"file '{os.path.abspath(vf)}'\n")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_filename),
        "-c", "copy",
        final_output
    ]
    subprocess.run(cmd, check=True)
    print(f"✅ Final video created: {final_output}")


def generate_animation_pipeline(topic_text: str):
    """
    Complete pipeline that performs:
      1. YAML outline generation.
      2. For each step in the outline:
            - Generate Manim code and run it.
            - Generate a narration line.
            - Convert the narration to speech.
            - Combine the video and audio.
      3. Concatenate all step videos into one final video.
    
    This is implemented as a generator that yields log messages along the way.
    When the final video is available, a log message containing its path is yielded.
    """
    yield "Generating YAML outline..."
    outline = generate_yaml_outline(topic_text)

    for idx, step in enumerate(outline, start=1):
        yield f"Step {idx}: {step}"

    yield "✅ YAML outline generated and saved to animation_outline.yaml."

    step_video_files = []
    
    for idx, step in enumerate(outline, start=1):
        yield f"\n========== Processing Step {idx}: {step} =========="
        try:
            # Filenames.
            step_video_filename = f"step_{idx}.mp4"
            step_audio_filename = f"step_{idx}.mp3"
            step_final_filename = f"step_{idx}_final.mp4"
            
            yield f"Generating Manim code for step {idx}..."
            manim_code = generate_manim_code_for_step(step)
            
            yield f"Running Manim script for step {idx}..."
            video_path = run_manim_script(manim_code, output_filename=step_video_filename)
            yield f"✅ Video generated for step {idx}: {video_path}"
            
            yield f"Generating narration for step {idx}..."
            dialogue_line = generate_dialogue_for_step(step)
            yield f"Narration: {dialogue_line}"
            
            audio_path = AUDIO_DIR / step_audio_filename
            yield f"Generating TTS audio for step {idx}..."
            text_to_speech(dialogue_line, output_audio=audio_path)
            
            yield f"Combining audio and video for step {idx}..."
            final_video_path = combine_audio_and_video(video_path, audio_path, final_output_filename=step_final_filename)
            yield f"✅ Step {idx} completed. Final video: {final_video_path}"
            step_video_files.append(str(final_video_path))
            
        except Exception as e:
            yield f"⚠️  Warning: Step {idx} failed ({str(e)}). Skipping this segment."
            continue

    if step_video_files:
        final_video = "final_animation_video.mp4"
        yield "Concatenating all step videos into final video..."
        concatenate_videos(step_video_files, final_output=final_video)
        yield f"Final video available at: {final_video}"
    else:
        yield "No valid segments were created. Pipeline finished with no output."
