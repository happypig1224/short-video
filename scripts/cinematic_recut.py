import subprocess
import os

CLIPS_DIR = r"c:\Users\33046\Desktop\short video\rendered_clips"
OUTPUT_FILE = os.path.join(CLIPS_DIR, "libai_shijianxing_cinematic_recut_preview.mp4")

# Segment trim configurations (start, duration in seconds)
# Extracting the most dynamic portions of each shot
edits = [
    {"name": "shot_01_cliff_storm_kling_o3.mp4", "start": 0.5, "dur": 3.2},
    {"name": "shot_02_sword_draw_kling_o3_pro.mp4", "start": 1.0, "dur": 2.8},
    {"name": "shot_03_scroll_ink_burst_kling_o3_pro.mp4", "start": 1.0, "dur": 2.5},
    {"name": "shot_04_sword_duel_ink_dragon_kling_o3_pro.mp4", "start": 1.2, "dur": 3.0},
    {"name": "shot_05_bullet_time_minimax_h3_max.mp4", "start": 0.8, "dur": 2.8},
    {"name": "shot_06_dragon_slash_minimax_h3_max.mp4", "start": 0.6, "dur": 2.8},
    {"name": "shot_07_boat_farewell_minimax_h3_max.mp4", "start": 0.5, "dur": 3.5},
]

# Step 1: Pre-process each clip to standardized 1920x804 (2.39:1 Cinema Scope), cropped to fill without black bars, trimmed
preprocessed_files = []
for i, item in enumerate(edits):
    inp = os.path.join(CLIPS_DIR, item["name"])
    out = os.path.join(CLIPS_DIR, f"temp_cut_{i}.mp4")
    preprocessed_files.append(out)
    
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(item["start"]),
        "-t", str(item["dur"]),
        "-i", inp,
        "-vf", "scale=1920:804:force_original_aspect_ratio=increase,crop=1920:804,setsar=1,fps=24",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "veryfast",
        "-an",
        out
    ]
    subprocess.run(cmd, check=True, capture_output=True)

# Step 2: Use xfade to chain them with 0.4s cinematic dissolve
# durations: 3.2, 2.8, 2.5, 3.0, 2.8, 2.8, 3.5
# with 0.4s overlap, offsets:
# off_0 = 3.2 - 0.4 = 2.8
# off_1 = 2.8 + (2.8 - 0.4) = 5.2
# off_2 = 5.2 + (2.5 - 0.4) = 7.3
# off_3 = 7.3 + (3.0 - 0.4) = 9.9
# off_4 = 9.9 + (2.8 - 0.4) = 12.3
# off_5 = 12.3 + (2.8 - 0.4) = 14.7
# total duration ~ 17.8s

trans_dur = 0.4
offsets = [2.8, 5.2, 7.3, 9.9, 12.3, 14.7]
transitions = ["dissolve", "fadeblack", "dissolve", "fadeblack", "dissolve", "dissolve"]

filter_parts = []
inputs_cmd = []
for i, f in enumerate(preprocessed_files):
    inputs_cmd.extend(["-i", f])

filter_parts.append(f"[0:v][1:v]xfade=transition={transitions[0]}:duration={trans_dur}:offset={offsets[0]}[v01];")
filter_parts.append(f"[v01][2:v]xfade=transition={transitions[1]}:duration={trans_dur}:offset={offsets[1]}[v02];")
filter_parts.append(f"[v02][3:v]xfade=transition={transitions[2]}:duration={trans_dur}:offset={offsets[2]}[v03];")
filter_parts.append(f"[v03][4:v]xfade=transition={transitions[3]}:duration={trans_dur}:offset={offsets[3]}[v04];")
filter_parts.append(f"[v04][5:v]xfade=transition={transitions[4]}:duration={trans_dur}:offset={offsets[4]}[v05];")
filter_parts.append(f"[v05][6:v]xfade=transition={transitions[5]}:duration={trans_dur}:offset={offsets[5]}[vout]")

final_cmd = [
    "ffmpeg", "-y",
    *inputs_cmd,
    "-filter_complex", "".join(filter_parts),
    "-map", "[vout]",
    "-c:v", "libx264",
    "-crf", "18",
    "-preset", "slow",
    "-pix_fmt", "yuv420p",
    OUTPUT_FILE
]

print("Rendering cinematic recut...")
res = subprocess.run(final_cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"Generated successfully: {OUTPUT_FILE}")
else:
    print("Error:", res.stderr)

# Clean up temp files
for f in preprocessed_files:
    if os.path.exists(f):
        os.remove(f)
