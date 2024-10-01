import tkinter as tk
from tkinter import filedialog, simpledialog
import subprocess
import os

# Initialize the tkinter window
root = tk.Tk()
root.withdraw()  # Hide the root window

# Open file dialog to select Video 1 (to remove audio from)
video1_path = filedialog.askopenfilename(
    title="Select Video 1 File",
    filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")]
)
if not video1_path:
    print("No Video 1 file selected.")
    exit()

# Open file dialog to select Video 2 (to extract audio from)
video2_path = filedialog.askopenfilename(
    title="Select Video 2 File",
    filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")]
)
if not video2_path:
    print("No Video 2 file selected.")
    exit()

# Step 1: Get the list of audio tracks from Video 2
print("Fetching audio tracks from Video 2...")
result = subprocess.run([
    "ffmpeg",
    "-i", video2_path,
    "-hide_banner"
], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Parse the output to find audio tracks
audio_tracks = []
for line in result.stderr.splitlines():
    if "Audio:" in line:
        audio_tracks.append(line.strip())

# Debug: Print detected audio tracks
print("Detected Audio Tracks:")
for track in audio_tracks:
    print(track)

# Display available audio tracks to the user
if not audio_tracks:
    print("No audio tracks found in Video 2.")
    exit()

# Prepare a message to display the available tracks in the dialog box
audio_track_message = "\n".join([f"{i + 1}: {track}" for i, track in enumerate(audio_tracks)])
selected_track = simpledialog.askinteger(
    "Select Audio Track",
    f"Available audio tracks:\n{audio_track_message}\n\nChoose an audio track (1-{len(audio_tracks)}):",
    minvalue=1,
    maxvalue=len(audio_tracks)
)

if selected_track is None:
    print("No audio track selected.")
    exit()

# Extract the selected track index (0-based index for ffmpeg)
selected_track_index = selected_track - 1

# Temporary files
extracted_audio_path = "extracted_audio.aac"
temp_video_path = "temp_video.mp4"

# Step 2: Extract the selected audio track from Video 2
print(f"Extracting audio track {selected_track} from Video 2...")
subprocess.run([
    "ffmpeg",
    "-i", video2_path,
    "-q:a", "0",
    "-map", f"0:a:{selected_track_index}",  # Select the chosen audio track
    extracted_audio_path
], check=True)

# Step 3: Remove audio from Video 1
print("Removing audio from Video 1...")
subprocess.run([
    "ffmpeg",
    "-i", video1_path,
    "-c:v", "copy",
    "-an",  # Remove audio
    temp_video_path
], check=True)

# Ask user to select the output file path
output_file_path = filedialog.asksaveasfilename(
    title="Save Output Video As",
    defaultextension=".mp4",
    filetypes=[("MP4 files", "*.mp4")]
)
if not output_file_path:
    print("No output file path provided.")
    exit()

# Step 4: Add extracted audio to the video
print("Adding extracted audio to Video 1...")
subprocess.run([
    "ffmpeg",
    "-i", temp_video_path,
    "-i", extracted_audio_path,
    "-c:v", "copy",
    "-c:a", "aac",
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-shortest",
    output_file_path
], check=True)

# Cleanup temporary files
os.remove(extracted_audio_path)
os.remove(temp_video_path)

print(f"Video saved as {output_file_path}")
