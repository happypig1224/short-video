#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小呆呆「1KB大脑发呆」表情包生图 - 嘴部解剖矫正版
彻底解决嘴部问题：严格遵循三视图中标志性的【横向极宽、超长大嘴】，坚决杜绝圆圆小嘴
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

def get_key():
    return os.getenv("VIVIBON_302_IMAGE_API_KEY") or os.getenv("AI_302_API_KEY") or os.getenv("API_302_KEY") or ""

def generate_with_gemini_model(
    model_name: str,
    prompt: str,
    negative_prompt: str,
    ref_image_path: Path,
    output_dir: Path,
    aspect_ratio: str = "3:4",
    prefix: str = "xdd_wide_mouth"
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
    print(f"[*] 重点修正: 小呆呆三视图标志性【极宽长嘴/横贯大嘴】")
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

    # 重点修正小呆呆五官与标志性【横向超长嘴巴】的详细提示词
    prompt = (
        "3D Pixar stylized animation character portrait. Exact 100% facial and anatomical replica of Xiao Dai Dai from the provided turnaround reference sheet: "
        "A cute chubby pink pig with smooth rosy skin, gigantic drooping cheek flesh, large floppy pig ears, bare chubby tummy, red suspender shorts with thin straps, red tie around neck.\n\n"
        "[CRITICAL MOUTH ANATOMY - STRICTLY MATCH REFERENCE SHEET]:\n"
        "Xiao Dai Dai's mouth is naturally very WIDE and LONG, stretching horizontally across almost his entire lower face, reaching deep into both chubby cheek pouches. "
        "His mouth is significantly WIDER than his snout. "
        "It is a LONG, horizontal, gentle curved smile line spanning across the face, seamlessly merging into his chubby cheeks (exactly as shown in the top-left and bottom-left reference poses). "
        "NEVER a small mouth, NEVER a narrow mouth, absolutely NEVER a small circular dark O-shaped mouth hole.\n\n"
        "[EYE & EXPRESSION CONSISTENCY]:\n"
        "Large, glossy, pure black round cartoon eyes with bright white specular reflections. "
        "His classic zoned-out, clueless '1KB brain' expression: staring straight ahead in a lovable daze, head completely empty, eyebrows slightly raised in innocent confusion.\n\n"
        "[MEME SCENE & DETAILS]:\n"
        "Sitting at an office cubicle in front of a computer monitor. "
        "Directly floating above his head is a retro pixelated blue loading bar showing '1% Loading...' with an hourglass icon. "
        "A single thin trail of cartoon white steam rises from his head (CPU overloaded). "
        "Cluttered office desk with paper stacks, coffee cup, sticky notes. "
        "Warm studio lighting, high-end 3D CGI rendering, crisp details, funny workplace meme."
    )

    negative = (
        "small circular mouth, small O-shaped mouth hole, tiny narrow mouth, whistle mouth, hole on face, gaping cavity, "
        "realistic pig, human realistic eyes, iris texture, cataract, clouded eyes, wrinkles, realistic skin, deformed anatomy, blurry"
    )

    print("=" * 65)
    print("🚀 启动小呆呆【三视图长嘴修正版】生图任务...")
    print("=" * 65)

    saved = generate_with_gemini_model(
        model_name="gemini-2.5-flash-image",
        prompt=prompt,
        negative_prompt=negative,
        ref_image_path=ref_image,
        output_dir=out_dir,
        aspect_ratio="3:4",
        prefix="xdd_wide_mouth"
    )

    print("=" * 65)
    print(f"🎉 全部生成完成！生成文件数量: {len(saved)}")
    for s in saved:
        print(f"  -> {s.resolve()}")
    print("=" * 65)
