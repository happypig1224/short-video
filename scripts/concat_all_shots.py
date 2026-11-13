import subprocess
import os

CLIPS_DIR = r"c:\Users\33046\Desktop\short video\rendered_clips"
OUTPUT_DIR = r"c:\Users\33046\Desktop\short video\rendered_clips"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "libai_shijianxing_full_story_7shots.mp4")

clips = [
    "shot_01_cliff_storm_kling_o3.mp4",
    "shot_02_sword_draw_kling_o3_pro.mp4",
    "shot_03_scroll_ink_burst_kling_o3_pro.mp4",
    "shot_04_sword_duel_ink_dragon_kling_o3_pro.mp4",
    "shot_05_bullet_time_minimax_h3_max.mp4",
    "shot_06_dragon_slash_minimax_h3_max.mp4",
    "shot_07_boat_farewell_minimax_h3_max.mp4",
]

# We will construct an ffmpeg filter_complex to normalize video to 1920x1080 @ 24fps
# and audio to 44.1kHz stereo, then concatenate seamlessly.

inputs_cmd = []
for c in clips:
    inputs_cmd.extend(["-i", os.path.join(CLIPS_DIR, c)])

# Construct filter_complex
filter_lines = []
# Process 0..3 (no audio)
for i in range(4):
    filter_lines.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=24[v{i}];")
    filter_lines.append(f"anullsrc=channel_layout=stereo:sample_rate=44100,atrim=duration=5.041667[a{i}];")

# Process 4..6 (has audio)
for i in range(4, 7):
    filter_lines.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=24[v{i}];")
    filter_lines.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,atrim=duration=5.184000[a{i}];")

concat_v = "".join([f"[v{i}]" for i in range(7)])
concat_a = "".join([f"[a{i}]" for i in range(7)])
filter_lines.append(f"{concat_v}concat=n=7:v=1:a=0[vout];")
filter_lines.append(f"{concat_a}concat=n=7:v=0:a=1[aout]")

filter_complex_str = "".join(filter_lines)

cmd = [
    "ffmpeg", "-y",
    *inputs_cmd,
    "-filter_complex", filter_complex_str,
    "-map", "[vout]",
    "-map", "[aout]",
    "-c:v", "libx264",
    "-crf", "18",
    "-preset", "slow",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    OUTPUT_FILE
]

print("Running FFmpeg concat command...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"Successfully generated master video: {OUTPUT_FILE}")
    size = os.path.getsize(OUTPUT_FILE)
    print(f"File size: {size / 1024 / 1024:.2f} MB")
else:
    print("FFmpeg error:", res.stderr)
