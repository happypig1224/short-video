#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小呆呆「1KB大脑发呆」表情包生图脚本
使用 302.ai 的 Gemini 图像生成模型 (基于 scripts/generate_image.py)
"""

import os
import sys
from pathlib import Path

# 导入同目录下的 generate_image 模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from generate_image import generate_image

def main():
    root_dir = Path(__file__).resolve().parent.parent
    ref_image_path = root_dir / "IP视觉资产库" / "00_全局规范与角色库" / "小呆呆_角色母图" / "小呆呆三视图及表情参考.jpg"
    output_dir = root_dir / "IP视觉资产库" / "01_表情包" / "小呆呆" / "01_职场牛马篇" / "01_生图候选池"

    if not ref_image_path.exists():
        raise FileNotFoundError(f"未找到小呆呆参考母图: {ref_image_path}")

    print(f"[*] 找到小呆呆母图: {ref_image_path}")
    print(f"[*] 输出目录: {output_dir}")

    # 详细提示词设计
    prompt = (
        "3D Pixar animation movie style. Highly consistent with the character in the reference image: "
        "Xiao Dai Dai, the cute chubby pink pig with big ears, a round pig snout, bare chubby belly, "
        "wearing red suspender shorts and a tiny red bow tie.\n\n"
        "[Action & Expression]:\n"
        "Xiao Dai Dai is sitting at a busy office desk, completely zoning out with an iconic blank, derp '1KB brain memory' expression. "
        "His round eyes are wide open, staring completely blankly into space with empty, lifeless pupils. "
        "Mouth slightly agape in utter confusion and mental shutdown ('head empty, no thoughts'). "
        "Both little hands are resting limply on the desk or propping up his chubby cheeks.\n\n"
        "[Humorous Visual Elements]:\n"
        "Directly floating above his round head is a glowing retro pixelated loading progress bar saying '1% Loading...' with a tiny spinning buffer wheel. "
        "A faint, comedic wisp of white smoke is rising from his head, symbolizing an overheated, overloaded CPU brain.\n\n"
        "[Environment & Lighting]:\n"
        "Sitting in an office cubicle. In front of him is a computer monitor showing overwhelming complex spreadsheets and unanswered work chats. "
        "Messy desk scattered with sticky notes, documents, and an iced coffee cup. "
        "Soft cinematic studio lighting, shallow depth of field focusing sharply on Xiao Dai Dai's hilarious zoned-out face. "
        "High quality 3D CGI rendering, cute comedic meme poster aesthetic."
    )

    negative_prompt = (
        "realistic pig, grotesque, low resolution, blurry, distorted face, extra limbs, bad anatomy, "
        "dark gloomy horror lighting, deformed hands, ugly, watermark, text error"
    )

    print("=" * 60)
    print("🚀 正在调用 302.ai 生成小呆呆「1KB大脑发呆」表情包...")
    print("=" * 60)

    saved_images = generate_image(
        prompt=prompt,
        image_paths=[ref_image_path],
        negative_prompt=negative_prompt,
        aspect_ratio="3:4",
        output_dir=output_dir,
        filename_prefix="xdd_1kb_brain_daze",
        timeout=120
    )

    print("=" * 60)
    print("🎉 生图成功！生成文件如下：")
    for img in saved_images:
        print(f"  -> {img.resolve()}")
    print("=" * 60)

if __name__ == "__main__":
    main()
