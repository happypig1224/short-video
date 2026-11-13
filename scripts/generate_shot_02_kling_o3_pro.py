import os
import sys
import json
import time
import base64
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

# 302.ai Kling O3 Pro Video Generator Script for Shot 02
# Model: kwaivgi/kling-video-o3-pro/image-to-video
# Strict constraints against mesh penetration, clipping, and anatomical deformation

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

def submit_shot_02_task(first_frame_path: str, last_frame_path: str, prompt: str, duration: int = 5):
    print(f"\n[1/3] 正在加载镜头 02 首尾关键帧资产...")
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

    print(f"\n[2/3] 正在向 302.ai 提交 Kling O3 Pro (专业版防穿模) 图生视频任务...")
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
                    print(f"\n🎉 镜头 02 视频渲染完成！")
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
    
    first_frame = os.path.join(assets_dir, "shot_02_first_frame.jpg")
    last_frame = os.path.join(assets_dir, "shot_02_last_frame.jpg")
    output_video = os.path.join(output_dir, "shot_02_sword_draw_kling_o3_pro.mp4")
    
    # Highly specific prompt with explicit anti-clipping spatial constraints
    prompt = (
        "Honor of Kings 3D CGI heroic cinematic motion. Transitioning seamlessly from first frame to last frame with zero mesh penetration or clipping. "
        "The youthful swordsman Li Bai smoothly pulls his left fingers away from the sword blade into a natural rest position. "
        "His right hand firmly and realistically grips the hilt, swinging the cyan jian sword smoothly outward and upward in front of his torso, "
        "maintaining strict physical distance and clearance from his chest, shoulders, and flowing white sleeves, strictly avoiding any clipping through body or clothing. "
        "He thrusts the sword diagonally upward toward the stormy sky in a heroic stance. "
        "The camera slightly tilts up into a dynamic low angle. Li Bai reveals a confident, dashing youthful smile with resolute bright eyes. "
        "A shockwave of cyan sword qi and faint golden calligraphic ripples erupts outward from the blade tip, "
        "blasting surrounding heavy falling raindrops into an expanding ring of fine water droplets and mist. "
        "Strictly zero mesh penetration, zero body intersection, five distinct fingers on both hands, flawless anatomy, "
        "natural wind-blown cloth physics, 4K game CG aesthetic, volumetric storm lightning."
    )
    
    print("=" * 65)
    print(" 302.ai Kling O3 Pro 镜头 02 渲染 (拔剑指天·严格防穿模)")
    print("=" * 65)
    
    task_id, poll_url = submit_shot_02_task(first_frame, last_frame, prompt, duration=5)
    poll_and_download(task_id, poll_url, output_video)

