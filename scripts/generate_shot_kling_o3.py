import os
import sys
import json
import time
import base64
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()

# 302.ai Kling O3 Video Generator Script
# Model: kwaivgi/kling-video-o3-std/image-to-video (or kling-video-o3-pro)

API_KEY = os.getenv("VIVIBON_302_IMAGE_API_KEY") or os.getenv("API_302_KEY") or ""
BASE_API_URL = "https://api.302.ai/ws/api/v3/kwaivgi/kling-video-o3-std/image-to-video"

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

def submit_kling_o3_task(first_frame_path: str, last_frame_path: str, prompt: str, duration: int = 5):
    print(f"\n[1/3] 正在准备首尾关键帧资产...")
    print(f" - 起始帧: {first_frame_path} ({os.path.getsize(first_frame_path)/1024:.1f} KB)")
    first_b64 = encode_image_to_base64(first_frame_path)
    
    last_b64 = None
    if last_frame_path and os.path.exists(last_frame_path):
        print(f" - 结束帧: {last_frame_path} ({os.path.getsize(last_frame_path)/1024:.1f} KB)")
        last_b64 = encode_image_to_base64(last_frame_path)
    
    payload = {
        "image": first_b64,
        "prompt": prompt,
        "duration": duration
    }
    if last_b64:
        payload["image_tail"] = last_b64

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"\n[2/3] 正在向 302.ai 提交 Kling O3 图生视频任务...")
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
    print(f"\n[3/3] 正在等待视频渲染完成 (轮询间隔 10 秒，最长等待 {max_wait_sec} 秒)...")
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
                    print(f"\n🎉 视频渲染完成！")
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
    import argparse
    parser = argparse.ArgumentParser(description="302.ai Kling O3 Video Generator")
    parser.add_argument("--first", default=r"c:\Users\33046\Desktop\short video\generated_assets\shot_01_first_frame.jpg")
    parser.add_argument("--last", default=r"c:\Users\33046\Desktop\short video\generated_assets\shot_01_last_frame.jpg")
    parser.add_argument("--output", default=r"c:\Users\33046\Desktop\short video\rendered_clips\shot_01_cliff_storm_kling_o3.mp4")
    parser.add_argument("--prompt", default="")
    args = parser.parse_args()

    default_prompt = (
        "Honor of Kings 3D CGI cinematic motion. The camera begins behind the youthful poet-swordsman Li Bai "
        "on the stormy cliff, executing a smooth clockwise orbital tracking shot while pushing in closer, "
        "shifting smoothly to a 45-degree medium profile shot. Violent rainstorm and howling gale cause his "
        "moon-white robes and celadon high ponytail ribbon to flutter fiercely. Thunderstorms churn across distant mountains. "
        "Li Bai turns his head slightly with sharp resolute eyes, right hand resting on the hilt drawing the cyan sword by half an inch; "
        "a gleam of cold cyan sword qi flashes as raindrops shatter against the blade edge into misty ink droplets, "
        "seamlessly transitioning into the last frame. Fluid movement, 4K game CG aesthetic, volumetric storm lighting."
    )
    
    prompt = args.prompt if args.prompt else default_prompt
    
    print("=" * 65)
    print(" 302.ai Kling O3 视频生成执行器")
    print("=" * 65)
    
    task_id, poll_url = submit_kling_o3_task(args.first, args.last, prompt, duration=5)
    poll_and_download(task_id, poll_url, args.output)
