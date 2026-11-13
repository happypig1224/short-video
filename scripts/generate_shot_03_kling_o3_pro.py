import os
import sys
import json
import time
import base64
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

# 302.ai Kling O3 Pro Video Generator Script for Shot 03
# Model: kwaivgi/kling-video-o3-pro/image-to-video
# Scene: 残卷入水水墨爆散 (Torn scroll water impact & calligraphy ink burst)

API_KEY = os.getenv("VIVIBON_302_IMAGE_API_KEY") or os.getenv("API_302_KEY") or ""
BASE_API_URL = "https://api.302.ai/ws/api/v3/kwaivgi/kling-video-o3-pro/image-to-video"

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

def submit_shot_03_task(first_frame_path: str, last_frame_path: str, prompt: str, duration: int = 5):
    print(f"\n[1/3] 正在加载镜头 03 首尾关键帧资产...")
    print(f" - 起始帧: {first_frame_path} ({os.path.getsize(first_frame_path)/1024:.1f} KB)")
    print(f" - 结束帧: {last_frame_path} ({os.path.getsize(last_frame_path)/1024:.1f} KB)")
    
    first_b64 = encode_image_to_base64(first_frame_path)
    last_b64 = encode_image_to_base64(last_frame_path)
    
    payload = {
        "image": first_b64,
        "image_tail": last_b64,
        "prompt": prompt,
        "duration": duration
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"\n[2/3] 正在向 302.ai 提交 Kling O3 Pro 核心特效镜 (残卷入水化墨) 渲染任务...")
    req = urllib.request.Request(BASE_API_URL, data=json.dumps(payload).encode("utf-8"), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("code") == 200 and "data" in data:
                task_info = data["data"]
                task_id = task_info.get("id")
                poll_url = task_info.get("urls", {}).get("get", f"https://api.302.ai/ws/api/v3/predictions/{task_id}/result")
                print(f" -> 任务提交成功！")
                print(f" -> 任务 ID: {task_id}")
                print(f" -> 轮询接口: {poll_url}")
                return task_id, poll_url
            else:
                raise RuntimeError(f"提交返回异常: {data}")
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        raise RuntimeError(f"HTTP {e.code} 提交失败: {err_msg}")

def poll_and_download(task_id: str, poll_url: str, output_path: str, max_wait_sec: int = 600):
    print(f"\n[3/3] 正在等待 Kling O3 Pro 视频渲染完成 (轮询间隔 10 秒，最长等待 {max_wait_sec} 秒)...")
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    start_time = time.time()
    while time.time() - start_time < max_wait_sec:
        req = urllib.request.Request(poll_url, headers=headers)
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                data = result.get("data", {})
                status = data.get("status", "unknown")
                elapsed = int(time.time() - start_time)
                
                print(f" [{elapsed:3d}s] 当前状态: {status}")
                
                if status in ["succeeded", "completed"]:
                    outputs = data.get("outputs", [])
                    if not outputs:
                        raise RuntimeError(f"渲染成功但未发现输出视频链接: {data}")
                    video_url = outputs[0]
                    print(f"\n🎉 镜头 03 核心水墨特效视频渲染完成！")
                    print(f" -> 视频远程 URL: {video_url}")
                    print(f" -> 正在下载至本地: {output_path} ...")
                    
                    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
                    dl_req = urllib.request.Request(video_url, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                    })
                    with urllib.request.urlopen(dl_req) as dl_resp, open(output_path, "wb") as f:
                        f.write(dl_resp.read())
                    
                    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    print(f" -> 下载成功！文件大小: {file_size_mb:.2f} MB")
                    return output_path
                elif status == "failed":
                    error_msg = data.get("error", "未知错误")
                    raise RuntimeError(f"任务渲染失败: {error_msg}")
                    
        except urllib.error.HTTPError as e:
            print(f" [警告] 轮询异常 (HTTP {e.code})，10秒后重试...")
        
        time.sleep(10)

    raise TimeoutError(f"任务超时 ({max_wait_sec} 秒) 未完成，请稍后检查任务 ID: {task_id}")

if __name__ == "__main__":
    assets_dir = r"c:\Users\33046\Desktop\short video\generated_assets"
    output_dir = r"c:\Users\33046\Desktop\short video\rendered_clips"
    
    first_frame = os.path.join(assets_dir, "shot_03_first_frame.jpg")
    last_frame = os.path.join(assets_dir, "shot_03_last_frame.jpg")
    output_video = os.path.join(output_dir, "shot_03_scroll_ink_burst_kling_o3_pro.mp4")
    
    # Precise fluid dynamics & calligraphy particle transition prompt
    prompt = (
        "Honor of Kings 3D CGI poetic cinematic VFX motion. Transitioning seamlessly from first frame to last frame. "
        "A torn ancient parchment scroll slips gently from the fingers, fluttering and descending smoothly through the rainy air "
        "toward the dark, reflective mountain pond surface. The camera smoothly tracks the falling scroll down into an intimate macro angle. "
        "The instant the paper touches the water, a magnificent explosion of fluid dynamics erupts: "
        "the tranquil dark water shatters into swirling black ink liquid waves, blossoming Chinese cursive calligraphy characters "
        "glowing with radiant ethereal golden energy, and a high-speed crown splash of translucent water droplets. "
        "Black ink billows outward like blooming smoke in water, infused with divine cyan and gold light rays breaking through the dark lake depths. "
        "Cinematic slow-motion fluid simulation, ultra-detailed fluid splash, volumetric rim lighting, 4K game CG visual effects, "
        "zero jitter, flawless liquid physics, pristine particle render."
    )
    
    print("=" * 65)
    print(" 302.ai Kling O3 Pro 镜头 03 渲染 (残卷入水水面化墨·流体水墨特效)")
    print("=" * 65)
    
    task_id, poll_url = submit_shot_03_task(first_frame, last_frame, prompt, duration=5)
    poll_and_download(task_id, poll_url, output_video)
