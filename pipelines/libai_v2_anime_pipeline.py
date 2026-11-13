#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《王者荣耀·李白·诗剑行》15秒高燃国漫风宣传片自动化生成流水线 V2
严格按照用户提供的原画截图与真实皮肤视觉设计：
1. 人物设定：俊美青年剑仙，黑发高马尾、碎刘海、白袍广袖、天青色腰带、朱红发带，持长剑流淌天青与水墨剑芒（国漫动漫画风）
2. 场景设定：东方水墨泼墨仙境，白练飞瀑倾泻、苍翠古松、漫天巨幅草书墨宝字帖流转、朱砂红印章、倒影深潭
3. 分镜对齐：
   - 镜头1（0-5s）：【黑白水墨微表情特写】青年闭目凝神，银光侧打，出鞘眼眸迸发青芒 「但承青莲有侠志，莫道红尘无剑仙！」
   - 镜头2（5-10s）：【中景飞瀑水墨剑舞】飞身纵跃，天青腰带翻飞，泼墨水浪与剑龙撕裂飞瀑 「剑至高危如蜀道，生逢穷途行路难！」
   - 镜头3（10-15s）：【全景诗成笑傲登顶】独立千山飞瀑绝壁，一剑指天，朱印草书与墨龙漫卷天际 「日月青冥，尽付剑锋！」
"""

import os
import sys
import time
import json
import urllib.request
import subprocess
from pathlib import Path

API_KEY = os.getenv("SILICONFLOW_API_KEY", "sk-cnzllmkkxcadhnnihvdahaoaurhvnizhlyyjgqlkrubnsaxr")
BASE_URL = "https://api.siliconflow.cn/v1"
OUTPUT_DIR = Path("c:/Users/33046/Desktop/short video/libai_v2_output")
STATE_FILE = OUTPUT_DIR / "pipeline_v2_state.json"

MODEL_IMAGE = "Qwen/Qwen-Image"
MODEL_TTS = "FunAudioLLM/CosyVoice2-0.5B"
VOICE_NAME = "FunAudioLLM/CosyVoice2-0.5B:alex"
MODEL_VIDEO = "Wan-AI/Wan2.2-T2V-A14B"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def log(step: str, msg: str):
    timestamp = time.strftime("%H:%M:%S")
    clean_msg = msg.encode("ascii", "replace").decode("ascii") if sys.platform == "win32" and not sys.stdout.encoding.lower().startswith("utf") else msg
    print(f"[{timestamp}] [{step}] {clean_msg}", flush=True)

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_state(state: dict):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def download_file(url: str, dest_path: Path):
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
        f.write(resp.read())

STORYBOARD = {
    "title": "王者荣耀·李白·诗剑行 15秒国漫水墨宣传片",
    "theme": "诗剑相融，墨韵破空。白衣黑发青年剑仙参悟大道，以笔化剑，臻至化境。",
    "character": {
        "name": "李白·诗剑行 (青年剑仙)",
        "description": "俊美冷冽的青年国漫剑仙，黑发高马尾带微卷碎刘海，身穿月白长袍与飘逸大袖，腰系标志性天青色宽锦带与红丝绦，手握流淌青光与水墨的长剑",
        "visual_prompt": (
            "Chinese donghua anime style, official art of Li Bai Poetry and Sword skin from Honor of Kings. "
            "Handsome young anime swordsman with dark black messy layered hair tied in a high ponytail, bangs framing face, "
            "wearing an elegant flowing white scholar-warrior robe with wide sleeves, vibrant cyan and sky-blue silk sash tied at waist with red tassel, "
            "holding a slender Chinese silver sword glowing with cyan Qi and black ink smoke, "
            "standing majestically, Chinese ink-wash painting background with waterfall and pine trees, floating calligraphy characters, "
            "4k masterpiece anime illustration, clean cel shading, high quality"
        )
    },
    "scene": {
        "location": "水墨飞瀑深潭与草书天际 (诗境)",
        "description": "传统水墨山水画风，巨幅白练瀑布飞泻，墨色奇峰陡峭，苍松挺拔，天空中漂浮漫卷巨大的狂草毛笔书法字帖，右上角盖有朱砂红印章，水面泛起墨色涟漪",
        "visual_prompt": (
            "Chinese donghua anime landscape, traditional Chinese ink wash painting, "
            "massive majestic waterfalls cascading down misty jagged mountains, ancient pine trees on cliffs, "
            "huge cursive Chinese calligraphy characters written with black ink floating across the cloudy sky, "
            "a large traditional red cinnabar artist seal stamp in the upper right corner, "
            "calm reflective lake at bottom with water ripples, ethereal ink-wash aesthetic, masterpiece 4k"
        )
    },
    "shots": [
        {
            "shot_id": 1,
            "duration": 5,
            "camera_movement": "水墨特写推进 (Dolly In Close-up)",
            "visual_prompt": (
                "Chinese anime donghua style, dramatic cinematic close-up shot of young swordsman Li Bai, "
                "striking handsome anime face, layered black hair blowing in the wind across his eyes, "
                "eyes slowly opening with piercing cyan glow, intense high-contrast monochrome ink wash lighting, "
                "brilliant silver highlight on shoulder and face, subtle red ribbon in hair, "
                "holding glowing sword blade in front of face reflecting floating golden calligraphy, "
                "black ink splatters floating in slow motion, masterpiece 4k anime"
            ),
            "narration": "但承青莲有侠志，莫道红尘无剑仙！"
        },
        {
            "shot_id": 2,
            "duration": 5,
            "camera_movement": "飞瀑平移跟拍 (Tracking Shot)",
            "visual_prompt": (
                "Chinese anime donghua style, dynamic medium tracking shot of young anime swordsman Li Bai "
                "gracefully leaping in mid-air in front of a giant cascading ink waterfall, "
                "flowing white robes and bright cyan sky-blue waist sash fluttering wildly, "
                "swinging sword creating enormous swirling arcs of black calligraphy ink and glowing cyan water dragon, "
                "giant Chinese calligraphy characters floating in background, dynamic wuxia anime action, fluid animation"
            ),
            "narration": "剑至高危如蜀道，生逢穷途行路难！"
        },
        {
            "shot_id": 3,
            "duration": 5,
            "camera_movement": "全景拉升仰拍 (Crane Up Reveal)",
            "visual_prompt": (
                "Chinese anime donghua style, breathtaking wide shot, young swordsman Li Bai standing proudly "
                "on calm reflective water, brandishing glowing sword pointing diagonally down, "
                "colossal waterfalls and misty ink mountains filling the background, "
                "swirling black ink dragon soaring into the sky, giant cursive calligraphy poems flying in the air, "
                "red cinnabar seal stamp in top corner, dazzling cyan and golden sword aura illuminating the ink clouds, "
                "epic donghua climax, masterpiece"
            ),
            "narration": "日月青冥，尽付剑锋！"
        }
    ]
}

# ==============================================================================
# 阶段 1：生成严格国漫水墨风原画素材 (Qwen/Qwen-Image)
# ==============================================================================
def step1_generate_images(state: dict) -> dict:
    log("STAGE 1", "启动 Qwen/Qwen-Image 生成【国漫动漫画风 + 水墨青年剑仙】原画...")
    images_state = state.get("images", {})

    tasks = [
        ("character_reference", STORYBOARD["character"]["visual_prompt"], "李白·诗剑行 青年剑仙角色参考图"),
        ("scene_reference", STORYBOARD["scene"]["visual_prompt"], "水墨飞瀑草书 场景概念图")
    ]
    for shot in STORYBOARD["shots"]:
        tasks.append((f"shot_{shot['shot_id']}_keyframe", shot["visual_prompt"], f"镜头 {shot['shot_id']} 关键帧图"))

    url = f"{BASE_URL}/images/generations"

    for key, prompt, desc in tasks:
        file_path = OUTPUT_DIR / f"{key}.png"
        if key in images_state and file_path.exists() and file_path.stat().st_size > 50000:
            log("STAGE 1", f"{desc} 已存在，跳过: {file_path.name}")
            continue

        log("STAGE 1", f"正在生成 {desc}...")
        payload = {
            "model": MODEL_IMAGE,
            "prompt": prompt,
            "image_size": "1024x1024"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=HEADERS)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            img_url = data["images"][0]["url"]

        log("STAGE 1", f"{desc} 生成成功，正在下载本地...")
        download_file(img_url, file_path)
        images_state[key] = {
            "local_path": str(file_path),
            "remote_url": img_url,
            "description": desc
        }
        state["images"] = images_state
        save_state(state)

    return images_state

# ==============================================================================
# 阶段 2：合成 3 句李白经典台词语音 (CosyVoice2-0.5B)
# ==============================================================================
def step2_generate_audio(state: dict) -> dict:
    log("STAGE 2", "启动 CosyVoice2-0.5B 合成李白高品质台词语音...")
    audio_state = state.get("audio", {})
    url = f"{BASE_URL}/audio/speech"

    for shot in STORYBOARD["shots"]:
        shot_id = shot["shot_id"]
        key = f"shot_{shot_id}_audio"
        file_path = OUTPUT_DIR / f"{key}.mp3"
        narration = shot["narration"]

        if key in audio_state and file_path.exists() and file_path.stat().st_size > 5000:
            log("STAGE 2", f"镜头 {shot_id} 台词录音已存在，跳过: {file_path.name}")
            continue

        log("STAGE 2", f"正在录制镜头 {shot_id} 李白台词: 「{narration}」...")
        payload = {
            "model": MODEL_TTS,
            "input": narration,
            "voice": VOICE_NAME,
            "response_format": "mp3"
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=HEADERS)
        with urllib.request.urlopen(req) as resp:
            audio_bytes = resp.read()
            with open(file_path, "wb") as f:
                f.write(audio_bytes)

        log("STAGE 2", f"镜头 {shot_id} 台词录音生成成功 ({len(audio_bytes)} 字节)")
        audio_state[key] = {
            "local_path": str(file_path),
            "narration": narration
        }
        state["audio"] = audio_state
        save_state(state)

    return audio_state

# ==============================================================================
# 阶段 3：Wan2.2-T2V-A14B 并发渲染 3 个 5 秒国漫水墨视频
# ==============================================================================
def step3_generate_videos(state: dict) -> dict:
    log("STAGE 3", "启动 Wan2.2-T2V-A14B 并发渲染国漫水墨视频分镜...")
    video_state = state.get("video", {})
    submit_url = f"{BASE_URL}/video/submit"
    status_url = f"{BASE_URL}/video/status"

    for shot in STORYBOARD["shots"]:
        shot_id = shot["shot_id"]
        key = f"shot_{shot_id}_video"
        file_path = OUTPUT_DIR / f"{key}.mp4"

        if key in video_state and file_path.exists() and file_path.stat().st_size > 50000:
            log("STAGE 3", f"镜头 {shot_id} 视频已存在，跳过: {file_path.name}")
            continue

        if key not in video_state or not video_state[key].get("requestId"):
            log("STAGE 3", f"提交镜头 {shot_id} 渲染任务: {shot['camera_movement']}...")
            prompt = shot["visual_prompt"]
            payload = {
                "model": MODEL_VIDEO,
                "prompt": prompt
            }
            req = urllib.request.Request(submit_url, data=json.dumps(payload).encode("utf-8"), headers=HEADERS)
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                req_id = res["requestId"]
                log("STAGE 3", f"镜头 {shot_id} 任务提交成功，RequestId: {req_id}")
                video_state[key] = {
                    "requestId": req_id,
                    "status": "InQueue",
                    "local_path": str(file_path)
                }
                state["video"] = video_state
                save_state(state)

    log("STAGE 3", "开始监控视频渲染状态...")
    pending_keys = [
        f"shot_{shot['shot_id']}_video"
        for shot in STORYBOARD["shots"]
        if not (OUTPUT_DIR / f"shot_{shot['shot_id']}_video.mp4").exists() or (OUTPUT_DIR / f"shot_{shot['shot_id']}_video.mp4").stat().st_size < 50000
    ]

    poll_count = 0
    while pending_keys:
        poll_count += 1
        time.sleep(10)
        still_pending = []
        for key in pending_keys:
            req_id = video_state[key]["requestId"]
            payload = {"requestId": req_id}
            req = urllib.request.Request(status_url, data=json.dumps(payload).encode("utf-8"), headers=HEADERS)
            try:
                with urllib.request.urlopen(req) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                    curr_status = res.get("status")
                    log("STAGE 3", f"轮询 #{poll_count} | {key} ({req_id}) 状态: {curr_status}")
                    video_state[key]["status"] = curr_status

                    if curr_status == "Succeed":
                        video_url = res["results"]["videos"][0]["url"]
                        dest_path = Path(video_state[key]["local_path"])
                        log("STAGE 3", f"{key} 渲染成功！正在下载视频...")
                        download_file(video_url, dest_path)
                        video_state[key]["remote_url"] = video_url
                        state["video"] = video_state
                        save_state(state)
                    elif curr_status == "Failed":
                        log("STAGE 3", f"ERROR: {key} 视频生成失败: {res}")
                        raise RuntimeError(f"{key} 视频生成失败")
                    else:
                        still_pending.append(key)
            except Exception as e:
                log("STAGE 3", f"轮询异常重试中: {e}")
                still_pending.append(key)

        pending_keys = still_pending

    log("STAGE 3", "所有国漫水墨视频镜头渲染完成！")
    return video_state

# ==============================================================================
# 阶段 4：FFmpeg 自动化拼接 15 秒短片与音画对齐
# ==============================================================================
def step4_render_final_video(state: dict) -> Path:
    final_output = OUTPUT_DIR / "final_15s_libai_shijianxing_anime.mp4"
    if final_output.exists() and final_output.stat().st_size > 500000:
        log("STAGE 4", f"[EXISTS] 15秒最终成片已存在: {final_output}")
        return final_output

    log("STAGE 4", "启动 FFmpeg 自动化后期系统，拼接 15 秒【李白·诗剑行】国漫宣传片...")

    concat_list = OUTPUT_DIR / "concat_list.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for i in (1, 2, 3):
            f.write(f"file 'shot_{i}_video.mp4'\n")

    concatenated_video = OUTPUT_DIR / "temp_concat_video.mp4"
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(concatenated_video)
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    a1 = OUTPUT_DIR / "shot_1_audio.mp3"
    a2 = OUTPUT_DIR / "shot_2_audio.mp3"
    a3 = OUTPUT_DIR / "shot_3_audio.mp3"

    filter_complex = (
        "[1:a]adelay=500|500[aud1];"
        "[2:a]adelay=5500|5500[aud2];"
        "[3:a]adelay=10500|10500[aud3];"
        "[aud1][aud2][aud3]amix=inputs=3:dropout_transition=2[aout]"
    )

    cmd_mix = [
        "ffmpeg", "-y",
        "-i", str(concatenated_video),
        "-i", str(a1),
        "-i", str(a2),
        "-i", str(a3),
        "-filter_complex", filter_complex,
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", "15.0",
        str(final_output)
    ]
    subprocess.run(cmd_mix, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if concatenated_video.exists():
        concatenated_video.unlink()
    if concat_list.exists():
        concat_list.unlink()

    log("STAGE 4", f"[SUCCESS] 15秒李白·诗剑行国漫风宣传片合成完毕: {final_output}")
    return final_output

def main():
    print("=" * 70)
    print("  王者荣耀·李白·诗剑行 15秒国漫水墨宣传片生成流水线 V2")
    print("=" * 70)

    state = load_state()

    # 1. 生图
    images_state = step1_generate_images(state)

    # 2. 配音
    audio_state = step2_generate_audio(state)

    # 3. 视频渲染
    video_state = step3_generate_videos(state)

    # 4. FFmpeg 合成
    final_video = step4_render_final_video(state)

    print("\n" + "=" * 70)
    print(f"[DONE] V2 宣传片制作完成！保存目录: {OUTPUT_DIR.resolve()}")
    print(f"1. 角色参考图: {OUTPUT_DIR / 'character_reference.png'}")
    print(f"2. 场景参考图: {OUTPUT_DIR / 'scene_reference.png'}")
    print(f"3. 最终15秒视频: {final_video}")
    print("=" * 70)

if __name__ == "__main__":
    main()

