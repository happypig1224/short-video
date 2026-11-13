import os
import sys
import json
import time
import base64
import subprocess
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VIVIBON_302_IMAGE_API_KEY") or os.getenv("API_302_KEY") or ""
SUBMIT_URL = "https://api.302.ai/minimaxi/v2/video_generation"
QUERY_URL = "https://api.302.ai/minimaxi/v1/query/video_generation"
FILE_URL = "https://api.302.ai/minimaxi/v1/files/retrieve"

OUTPUT_DIR = r"c:\Users\33046\Desktop\short video\rendered_clips\route_b_chain"
os.makedirs(OUTPUT_DIR, exist_ok=True)

CHAIN_STEPS = [
    {
        "shot_num": 2,
        "name": "chain_shot_02_sword_draw",
        "input_frame": r"c:\Users\33046\Desktop\short video\rendered_clips\chain_shot_01_last.jpg",
        "prompt": (
            "The camera rapidly dollies in smoothly from the wide shot to a medium shot in front of Li Bai on the steep cliff peak. "
            "Li Bai, a handsome youthful swordsman 18 years old with sharp eyes, raises his right hand to grasp the sword hilt at his chest. "
            "With a decisive martial arts motion, he draws the plum blossom sword out of the black scabbard. "
            "Cold cyan sword gleam flashes across his face and the blade, glinting in the dark thunderstorm. "
            "Wind fiercely billows his moon-white ink robes and celadon ribbon. "
            "He points the gleaming sword blade downwards toward the deep abyss water below. "
            "Epic wuxia action, photorealistic 8k, flawless hand anatomy, no distortion, zero artifacts."
        )
    },
    {
        "shot_num": 3,
        "name": "chain_shot_03_scroll_ink_burst",
        "prompt": (
            "The camera immediately tracks down following the sword tip, rapidly diving down toward the dark abyss mountain lake. "
            "A piece of ancient calligraphy parchment scroll at Li Bai's waist is blown away by the violent wind and plunges into the dark lake water. "
            "The moment the parchment hits the water, it triggers a magnificent fluid explosion of black ink and cyan water splashes, "
            "swirling into a dynamic calligraphy vortex across the surface, turning the lake into a mirror of ink. "
            "Cinematic fluid dynamics, high frame rate, photorealistic 8k, majestic ink art."
        )
    },
    {
        "shot_num": 4,
        "name": "chain_shot_04_water_mirror_duel",
        "prompt": (
            "The camera rises up from the swirling ink mirror surface. "
            "A dark black-and-white ink shadow reflection of Li Bai emerges from the water mirror. "
            "Li Bai and the ink shadow clash fiercely on the water surface with their swords, sparks and golden lightning bursting on blade collision. "
            "Li Bai executes a lightning-fast thrust, his sword piercing through the heart of the ink shadow. "
            "The shadow explodes into brilliant golden light particles and ink droplets that surge into a spiraling ink dragon roar. "
            "Epic martial arts choreography, photorealistic 8k, flawless sword combat."
        )
    },
    {
        "shot_num": 5,
        "name": "chain_shot_05_bullet_time_awakening",
        "prompt": (
            "Bullet-time freeze. The exploding golden particles, ink droplets, and falling snow crystals suddenly freeze suspended in mid-air. "
            "The camera performs a slow circular orbit around Li Bai. "
            "Beneath his feet, the frozen deep lake surface suddenly cracks with hundreds of glowing cyan-gold runic fractures spreading outward like plum blossoms. "
            "Li Bai's eyes open with profound spiritual enlightenment, sword heart awakening, pure white inner qi swirling gently around his body. "
            "Mystical wuxia, cinematic slow motion, 8k, magnificent lighting."
        )
    },
    {
        "shot_num": 6,
        "name": "chain_shot_06_cloud_cleaving_slash",
        "prompt": (
            "From the cracked ice surface, Li Bai suddenly leaps explosively into the dark stormy sky like an ascending dragon. "
            "At the peak of his leap, he performs a thunderous downward vertical two-handed sword slash. "
            "A titanic golden ink dragon erupts from his sword blade, cleaving the heavy dark cumulus clouds into two halves like split silk. "
            "Radiant golden sunlight cascades down through the colossal chasm in the clouds, illuminating the entire realm. "
            "Epic scale, cinematic god rays, photorealistic 8k, breathtaking fantasy."
        )
    },
    {
        "shot_num": 7,
        "name": "chain_shot_07_flatboat_farewell",
        "prompt": (
            "The camera cranes down smoothly through the golden morning mist from the sky down to a calm autumn river. "
            "Li Bai descends and lands gracefully on a wooden flatboat drifting downriver. "
            "He calmly sheathes his sword with a satisfying click, lies back leisurely on the boat, and raises a white jade wine gourd to drink wine. "
            "The flatboat drifts peacefully into the distance through emerald bamboo groves and soft morning mist, swallows flying across the golden sunrise. "
            "Poetic wuxia, peaceful ending, masterpiece 8k, serene atmosphere."
        )
    }
]

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as f:
        b64_str = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{b64_str}"

def submit_minimax_task(first_frame_path: str, prompt: str, duration: int = 5, resolution: str = "768P") -> str:
    print(f" -> 正在编码首帧: {os.path.basename(first_frame_path)} ...")
    first_b64 = encode_image_to_base64(first_frame_path)
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": first_b64}, "role": "first_frame"}
    ]
    payload = {
        "model": "MiniMax-H3-Max",
        "content": content,
        "resolution": resolution,
        "duration": duration,
        "ratio": "16:9"
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(SUBMIT_URL, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        task_id = data.get("task_id")
        if task_id:
            print(f" -> 任务提交成功! Task ID: {task_id}")
            return str(task_id)
        else:
            raise RuntimeError(f"提交失败，无 task_id: {data}")

def poll_and_download(task_id: str, output_path: str, max_wait_sec: int = 600):
    start_time = time.time()
    print(f" -> 开始轮询任务状态: {task_id} ...")
    while time.time() - start_time < max_wait_sec:
        query_req = urllib.request.Request(f"{QUERY_URL}?task_id={task_id}", headers={"Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(query_req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            status = data.get("status")
            if status == "Success":
                file_id = data.get("file_id")
                print(f" -> 渲染成功! File ID: {file_id}")
                file_req = urllib.request.Request(f"{FILE_URL}?file_id={file_id}", headers={"Authorization": f"Bearer {API_KEY}"})
                with urllib.request.urlopen(file_req) as f_resp:
                    f_data = json.loads(f_resp.read().decode("utf-8"))
                    dl_url = f_data.get("file", {}).get("download_url")
                    print(f" -> 下载视频中...")
                    dl_req = urllib.request.Request(dl_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    with urllib.request.urlopen(dl_req) as dl_resp, open(output_path, "wb") as out_f:
                        out_f.write(dl_resp.read())
                    print(f" -> 已保存: {output_path} ({os.path.getsize(output_path) / 1024 / 1024:.2f} MB)")
                    return
            elif status in ["Fail", "Error"]:
                raise RuntimeError(f"渲染失败: {data}")
            else:
                elapsed = int(time.time() - start_time)
                print(f"    ... 状态 [{status}] ({elapsed}s)")
                time.sleep(10)
    raise TimeoutError(f"超时未完成 ({max_wait_sec}s)")

def extract_last_frame(video_path: str, out_frame_path: str):
    print(f" -> 正在抽取尾帧: {os.path.basename(out_frame_path)} ...")
    cmd = ["ffmpeg", "-y", "-sseof", "-0.1", "-i", video_path, "-vframes", "1", "-q:v", "2", out_frame_path]
    subprocess.run(cmd, check=True, capture_output=True)
    if os.path.exists(out_frame_path) and os.path.getsize(out_frame_path) > 0:
        print(f" -> 尾帧已提取: {out_frame_path} ({os.path.getsize(out_frame_path)} bytes)")
    else:
        raise RuntimeError("尾帧提取失败")

def run_step(step_idx: int):
    step = CHAIN_STEPS[step_idx]
    shot_num = step["shot_num"]
    name = step["name"]
    out_video = os.path.join(OUTPUT_DIR, f"{name}.mp4")
    out_last_frame = os.path.join(OUTPUT_DIR, f"chain_shot_{shot_num:02d}_last.jpg")
    
    # Input frame is either defined or previous step's last frame
    if "input_frame" in step:
        inp_frame = step["input_frame"]
    else:
        prev_shot_num = shot_num - 1
        inp_frame = os.path.join(OUTPUT_DIR, f"chain_shot_{prev_shot_num:02d}_last.jpg")
    
    print(f"\n==========================================")
    print(f"=== 执行链式镜头 SC-{shot_num:02d}: {name} ===")
    print(f"==========================================")
    print(f"输入首帧 (严格继承上一镜尾帧): {inp_frame}")
    
    task_id = submit_minimax_task(inp_frame, step["prompt"])
    poll_and_download(task_id, out_video)
    extract_last_frame(out_video, out_last_frame)
    print(f"=== 镜头 SC-{shot_num:02d} 链式递推完成! ===\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        step_to_run = int(sys.argv[1])
        run_step(step_to_run)
    else:
        print("Usage: python run_frame_chain_pipeline.py <step_index 0..5>")
