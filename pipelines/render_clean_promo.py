import subprocess
from pathlib import Path

out_dir = Path("c:/Users/33046/Desktop/short video/libai_v2_output")
concat_list = out_dir / "concat_clean_list.txt"
with open(concat_list, "w", encoding="utf-8") as f:
    for i in (1, 2, 3):
        f.write(f"file 'shot_{i}_video.mp4'\n")

temp_video = out_dir / "temp_clean_video.mp4"
cmd_concat = [
    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
    "-i", str(concat_list),
    "-c", "copy",
    str(temp_video)
]
subprocess.run(cmd_concat, check=True)

final_promo = out_dir / "final_15s_libai_shijianxing_clean_promo.mp4"
bgm = out_dir / "wuxia_cinematic_bgm.wav"

cmd_mix = [
    "ffmpeg", "-y",
    "-i", str(temp_video),
    "-i", str(bgm),
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "256k",
    "-shortest",
    "-t", "15.0",
    str(final_promo)
]
subprocess.run(cmd_mix, check=True)

if temp_video.exists():
    temp_video.unlink()
if concat_list.exists():
    concat_list.unlink()

print("Successfully created clean promo video:", final_promo)

