import os
import sys
import json
import time
import base64
import urllib.request
import urllib.error

# 302.ai MiniMax-H3-Max Batch Generator for Shots 05, 06, 07
# Model: MiniMax-H3-Max ($0.054/s)
# Endpoints:
# - Submit: https://api.302.ai/minimaxi/v2/video_generation
# - Query:  https://api.302.ai/minimaxi/v1/query/video_generation?task_id={task_id}
# - File:   https://api.302.ai/minimaxi/v1/files/retrieve?file_id={file_id}

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("VIVIBON_302_IMAGE_API_KEY") or os.getenv("API_302_KEY") or ""
SUBMIT_URL = "https://api.302.ai/minimaxi/v2/video_generation"
QUERY_URL = "https://api.302.ai/minimaxi/v1/query/video_generation"
FILE_URL = "https://api.302.ai/minimaxi/v1/files/retrieve"

def encode_image_to_base64(image_path: str) -> str:
    """Read a local image and return a data URI string."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    with open(image_path, "rb") as f:
        b64_str = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{b64_str}"

def submit_minimax_task(first_frame_path: str, last_frame_path: str, prompt: str, duration: int = 5, resolution: str = "768P") -> str:
    print(f" -> 正在加载首尾帧 Base64 资产...")
    first_b64 = encode_image_to_base64(first_frame_path)
    last_b64 = encode_image_to_base64(last_frame_path)
    
    content = [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": first_b64}, "role": "first_frame"},
        {"type": "image_url", "image_url": {"url": last_b64}, "role": "last_frame"}
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
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            task_id = data.get("task_id")
            if task_id:
                print(f" -> 提交成功！MiniMax-H3-Max 任务 ID: {task_id}")
                return str(task_id)
            else:
                raise RuntimeError(f"提交失败，无 task_id: {data}")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code} 提交异常: {err_msg}")

def poll_and_download_minimax(task_id: str, output_path: str, max_wait_sec: int = 600):
    print(f" -> 正在轮询任务 {task_id} 状态...")
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    start_time = time.time()
    while time.time() - start_time < max_wait_sec:
        query_endpoint = f"{QUERY_URL}?task_id={task_id}"
        req = urllib.request.Request(query_endpoint, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                status = result.get("status", "unknown")
                elapsed = int(time.time() - start_time)
                print(f"    [{elapsed:3d}s] 状态: {status}")
                
                if status == "Success":
                    file_id = result.get("file_id")
                    if not file_id:
                        raise RuntimeError(f"任务成功但未返回 file_id: {result}")
                    print(f" -> 渲染成功！获取文件 ID: {file_id}")
                    
                    # Step 2: Retrieve download URL
                    file_req = urllib.request.Request(f"{FILE_URL}?file_id={file_id}", headers=headers)
                    with urllib.request.urlopen(file_req) as f_resp:
                        file_data = json.loads(f_resp.read().decode("utf-8"))
                        dl_url = file_data.get("file", {}).get("download_url")
                        if not dl_url:
                            raise RuntimeError(f"未获取到下载链接: {file_data}")
                    
                    print(f" -> 正在下载视频文件至: {output_path} ...")
                    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                    dl_req = urllib.request.Request(dl_url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    })
                    with urllib.request.urlopen(dl_req) as d_resp, open(output_path, "wb") as f_out:
                        f_out.write(d_resp.read())
                    
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    print(f" -> 下载完成！文件大小: {size_mb:.2f} MB\n")
                    return output_path
                elif status in ["Fail", "Failed", "Error"]:
                    base_resp = result.get("base_resp", {})
                    raise RuntimeError(f"渲染失败: {base_resp.get('status_msg', '未知错误')}")
        except urllib.error.HTTPError as e:
            print(f"    [警告] 轮询异常 (HTTP {e.code})，8秒后重试...")
            
        time.sleep(8)
        
    raise TimeoutError(f"任务超时 ({max_wait_sec}秒): {task_id}")

def run_shots(shot_list):
    assets_dir = r"c:\Users\33046\Desktop\short video\generated_assets"
    output_dir = r"c:\Users\33046\Desktop\short video\rendered_clips"
    
    shots_info = {
        5: {
            "name": "镜头 05 (太行玄冰风雪子弹时间·神光顿悟)",
            "first": os.path.join(assets_dir, "shot_05_first_frame.jpg"),
            "last": os.path.join(assets_dir, "shot_05_last_frame.jpg"),
            "output": os.path.join(output_dir, "shot_05_bullet_time_minimax_h3_max.mp4"),
            "prompt": (
                "Honor of Kings 3D CGI poetic martial arts cinematic motion. Connecting seamlessly from the ink dragon explosion into stillness. "
                "Youthful swordsman Li Bai stands in meditation on the pitch-black frozen ice of the winter gorge. "
                "Heavy snowfall slows down into ethereal bullet-time stillness, individual snowflakes suspended mid-air with soft rim light. "
                "The camera slowly pushes in towards his calm, youthful face. "
                "Deep spiritual enlightenment strikes: Li Bai suddenly opens his eyes, which blaze with divine cyan celestial light! "
                "The pitch-black river ice beneath his boots violently cracks with glowing cyan spiritual energy fissures. "
                "Flawless facial anatomy, bright resolute eyes, perfectly rendered snow and ice physics, 4K game CG aesthetic."
            )
        },
        6: {
            "name": "镜头 06 (破局金墨巨龙撕裂乌云·一剑狂歌)",
            "first": os.path.join(assets_dir, "shot_06_first_frame.jpg"),
            "last": os.path.join(assets_dir, "shot_06_last_frame.jpg"),
            "output": os.path.join(output_dir, "shot_06_dragon_slash_minimax_h3_max.mp4"),
            "prompt": (
                "Honor of Kings 3D CGI epic airborne combat climax motion. Connecting seamlessly from the cracking ice enlightenment. "
                "Li Bai leaps high into the stormy sky, sword raised overhead channeling swirling lightning, thunder, and glowing calligraphy runes. "
                "The camera sweeps dynamically in a low tracking arc as Li Bai executes a monumental downward slash. "
                "A thousand-foot colossal dragon made of swirling black ink and blazing golden calligraphy erupts from his blade, "
                "violently cleaving the dark thunderclouds in two. Radiant golden morning dawn sunbeams burst through the shattered clouds. "
                "Flawless anatomy, five distinct fingers, zero clipping, awe-inspiring dragon fluid dynamics, 4K game CG VFX."
            )
        },
        7: {
            "name": "镜头 07 (轻舟入画收剑归隐·诗意远行)",
            "first": os.path.join(assets_dir, "shot_07_first_frame.jpg"),
            "last": os.path.join(assets_dir, "shot_07_last_frame.jpg"),
            "output": os.path.join(output_dir, "shot_07_boat_farewell_minimax_h3_max.mp4"),
            "prompt": (
                "Honor of Kings 3D CGI poetic tranquil cinematic resolution. Connecting seamlessly from the dawn sunrise into morning mist. "
                "Li Bai lands gracefully on the bow of a wooden flatboat gliding smoothly across an emerald river bordered by misty bamboo mountains. "
                "He sheathes his cyan sword into the black plum blossom scabbard with a clean click. "
                "The camera slowly pans and pulls back into a grand, tranquil aerial landscape shot. "
                "Li Bai reclines leisurely at the boat bow, raising his white jade wine gourd to drink wine with a carefree, contented smile. "
                "The flatboat drifts peacefully into the golden morning mist and bamboo sea, leaving gentle ripples behind. "
                "Poetic Chinese landscape painting atmosphere, flawless cloth dynamics, serene 4K game CG aesthetic."
            )
        }
    }
    
    print("=" * 70)
    print(" 302.ai MiniMax-H3-Max 批量视频生成执行器 (镜头 05, 06, 07)")
    print("=" * 70)
    
    for s_num in shot_list:
        info = shots_info[s_num]
        print(f"\n>>> 开始处理: {info['name']} <<<")
        task_id = submit_minimax_task(info["first"], info["last"], info["prompt"], duration=5, resolution="768P")
        poll_and_download_minimax(task_id, info["output"])
        print(f">>> {info['name']} 渲染并下载完成！<<<\n")

if __name__ == "__main__":
    shots_to_run = [5, 6, 7]
    if len(sys.argv) > 1:
        shots_to_run = [int(x) for x in sys.argv[1:]]
    run_shots(shots_to_run)
