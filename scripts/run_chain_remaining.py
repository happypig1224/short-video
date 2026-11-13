import os
import sys
import subprocess
from run_frame_chain_pipeline import run_step, CHAIN_STEPS

def main():
    # Run steps 2, 3, 4, 5 (corresponding to shots 4, 5, 6, 7)
    for step_idx in range(2, len(CHAIN_STEPS)):
        print(f"\n>>> Running step index {step_idx} (Shot {CHAIN_STEPS[step_idx]['shot_num']})...")
        run_step(step_idx)
    
    print("\n==========================================")
    print("=== 所有链式镜头递推完成！开始无缝总成拼合 ===")
    print("==========================================")
    
    # Assembly:
    # Shot 01: c:\Users\33046\Desktop\short video\rendered_clips\shot_01_cliff_storm_kling_o3.mp4
    # Shot 02: c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_02_sword_draw.mp4
    # Shot 03: c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_03_scroll_ink_burst.mp4
    # Shot 04: c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_04_water_mirror_duel.mp4
    # Shot 05: c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_05_bullet_time_awakening.mp4
    # Shot 06: c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_06_cloud_cleaving_slash.mp4
    # Shot 07: c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_07_flatboat_farewell.mp4
    
    clips = [
        r"c:\Users\33046\Desktop\short video\rendered_clips\shot_01_cliff_storm_kling_o3.mp4",
        r"c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_02_sword_draw.mp4",
        r"c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_03_scroll_ink_burst.mp4",
        r"c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_04_water_mirror_duel.mp4",
        r"c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_05_bullet_time_awakening.mp4",
        r"c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_06_cloud_cleaving_slash.mp4",
        r"c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain\chain_shot_07_flatboat_farewell.mp4"
    ]
    
    master_output = r"c:\Users\33046\Desktop\short video\rendered_clips\libai_shijianxing_route_b_seamless_master.mp4"
    
    # Standardize all clips to 1920x1080 (Cinema full 16:9) @ 24fps
    # Because each clip starts from the previous clip's EXACT last frame,
    # direct cut concatenation produces an absolute pixel-level continuous sequence!
    inputs_cmd = []
    for c in clips:
        inputs_cmd.extend(["-i", c])
        
    filter_lines = []
    # Video normalization
    for i in range(7):
        filter_lines.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=24[v{i}];")
        # Audio normalization: if shot 0 has no audio, generate silent audio
        if i == 0:
            filter_lines.append(f"anullsrc=channel_layout=stereo:sample_rate=44100,atrim=duration=5.041667[a0];")
        else:
            filter_lines.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo[a{i}];")
            
    concat_v = "".join([f"[v{i}]" for i in range(7)])
    concat_a = "".join([f"[a{i}]" for i in range(7)])
    filter_lines.append(f"{concat_v}concat=n=7:v=1:a=0[vout];")
    filter_lines.append(f"{concat_a}concat=n=7:v=0:a=1[aout]")
    
    cmd = [
        "ffmpeg", "-y",
        *inputs_cmd,
        "-filter_complex", "".join(filter_lines),
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "slow",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        master_output
    ]
    
    print("Executing final seamless master render...")
    subprocess.run(cmd, check=True)
    print(f"\n==========================================")
    print(f"=== 路线 B 物理无缝母带渲染成功: {master_output} ===")
    print(f"=== 文件大小: {os.path.getsize(master_output) / 1024 / 1024:.2f} MB ===")
    print(f"==========================================")

if __name__ == "__main__":
    main()
