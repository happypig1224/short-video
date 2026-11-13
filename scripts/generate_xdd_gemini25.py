#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小呆呆「1KB大脑发呆」表情包生图 - 进阶版 (使用 gemini-2.5-flash-image)
加强对小呆呆卡通眼睛、包子脸、五官一致性的极端锁定
"""

import os
import sys
import json
import base64
import http.client
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 获取 API Key
def get_key():
    return os.getenv("VIVIBON_302_IMAGE_API_KEY") or os.getenv("AI_302_API_KEY") or os.getenv("API_302_KEY") or ""

def generate_with_gemini_model(
    model_name: str,
    prompt: str,
    negative_prompt: str,
    ref_image_path: Path,
    output_dir: Path,
    aspect_ratio: str = "3:4",
    prefix: str = "xdd_gemini25"
):
    api_key = get_key()
    api_host = "api.302.ai"
    api_path = f"/google/v1/models/{model_name}?response_format=b64_json"

    # 读取参考图
    img_bytes = ref_image_path.read_bytes()
    b64_str = base64.b64encode(img_bytes).decode("utf-8")

    parts = [
        {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": b64_str
            }
        },
        {
            "text": f"{prompt.strip()}\n\n[Negative Elements / Strictly Avoid]:\n{negative_prompt.strip()}"
        }
    ]

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    print(f"[*] 正在调用模型: {model_name}")
    print(f"[*] 画面比例: {aspect_ratio}")
    print(f"[*] 参考母图: {ref_image_path.name}")

    conn = http.client.HTTPSConnection(api_host, timeout=120)
    try:
        conn.request("POST", api_path, json.dumps(payload), headers)
        res = conn.getresponse()
        raw_data = res.read().decode("utf-8")
    finally:
        conn.close()

    if res.status != 200:
        raise RuntimeError(f"请求失败 HTTP {res.status}: {raw_data[:200]}")

    resp_json = json.loads(raw_data)
    candidates = resp_json.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"无返回候选内容: {resp_json}")

    output_dir.mkdir(parents=True, exist_ok=True)
    saved_files = []

    for c in candidates:
        parts_list = c.get("content", {}).get("parts", [])
        for p in parts_list:
            inline = p.get("inlineData") or p.get("inline_data")
            if inline and "data" in inline:
                img_data = base64.b64decode(inline["data"])
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                out_path = output_dir / f"{prefix}_{model_name.replace('-', '_')}_{timestamp}.jpg"
                out_path.write_bytes(img_data)
                print(f"[+] 成功保存图像: {out_path} ({len(img_data)/1024:.1f} KB)")
                saved_files.append(out_path)

    return saved_files

if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parent.parent
    ref_image = root_dir / "IP视觉资产库" / "00_全局规范与角色库" / "小呆呆_角色母图" / "小呆呆三视图及表情参考.jpg"
    out_dir = root_dir / "IP视觉资产库" / "01_表情包" / "小呆呆" / "01_职场牛马篇" / "01_生图候选池"

    # 深度解构并锁定小呆呆面部、眼睛特征的 Prompt
    prompt = (
        "3D Pixar stylized animation character portrait. Exact 100% character replica and match of the cute cartoon character in the reference image: "
        "Xiao Dai Dai (GG Bond little pig). "
        "He is a smooth, stylized 3D chubby pink pig with smooth rosy skin, very chubby drooping lower cheeks, large floppy pig ears, "
        "and a big round pig snout with two round nostrils. Bare round belly, wearing his signature red suspender shorts with thin straps, "
        "and a small bright red necktie around his neck.\n\n"
        "[Critical Eye & Face Consistency Rule]: "
        "The eyes MUST strictly maintain the cartoon style of the reference sheet: "
        "Large, round, friendly black cartoon eyes with pure white glossy specular reflection dots. "
        "Pure black pupils with zero human iris texture. Simple smooth cartoon eye sockets, no realistic wrinkles, no realistic sclera, no cloudy cataract eyes. "
        "A cute, innocent, blank '1KB brain' zoning-out stare with wide open eyes, mouth slightly agape in utter cluelessness, head empty no thoughts.\n\n"
        "[Scene & Meme Humor]: "
        "Xiao Dai Dai is sitting at a busy office desk cubicle, completely spaced out and overwhelmed by work. "
        "Above his head floats a hilarious retro pixelated holographic loading bar showing '1% Loading...' with a tiny spinning sandglass icon. "
        "A subtle, comedic wisp of white cartoon smoke gently rises from his head (brain CPU overloaded). "
        "Messy desk with computer monitor displaying spreadsheets, colorful sticky notes, iced coffee cup. "
        "Bright studio key lighting, soft depth of field, high-end 3D CGI animation render, expressive workplace meme poster."
    )

    negative = (
        "realistic pig, human realistic eyes, visible iris texture, realistic sclera, cloudy dead eyes, "
        "cataract, zombie eyes, creepy uncanny valley, sunken eye sockets, wrinkles, angry face, "
        "wrong clothes, blue shorts, distorted body, extra ears, bad anatomy, deformed snout, blurry, low resolution, 2D flat"
    )

    print("=" * 65)
    print("🚀 启动进阶版 Gemini 模型生图 (gemini-2.5-flash-image)...")
    print("=" * 65)

    saved = generate_with_gemini_model(
        model_name="gemini-2.5-flash-image",
        prompt=prompt,
        negative_prompt=negative,
        ref_image_path=ref_image,
        output_dir=out_dir,
        aspect_ratio="3:4",
        prefix="xdd_1kb_v2"
    )

    print("=" * 65)
    print(f"🎉 全部生成完成！生成文件数量: {len(saved)}")
    for s in saved:
        print(f"  -> {s.resolve()}")
    print("=" * 65)
