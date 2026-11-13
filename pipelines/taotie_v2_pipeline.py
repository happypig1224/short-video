import os
import sys
import time
import json
import base64
import urllib.request
import urllib.error
import re

API_KEY = "sk-2BO4CwzHo3Tv0Jx8gfUTCZaraSfisTjj1WT4pOVZ1DjBtg11"
BASE_URL = "https://api.302.ai"

OUTPUT_DIR = "taotie_v2"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REPORT_MD = os.path.join(OUTPUT_DIR, "taotie_v2_audit_report.md")
RESULT_JSON = os.path.join(OUTPUT_DIR, "taotie_v2_data.json")
VIDEO_FILE = os.path.join(OUTPUT_DIR, "taotie_v2_cinematic_5s.mp4")

AUDIT_FEEDBACK_GUIDELINES = """
【前一轮评审打回原因与整改要求】：
1. 头部严禁出现眼睛：上一轮部分帧中头部依然出现了兽眼或眼窝。必须严格遵循《山海经》“目在腋下”——面部为完全平滑、惨白无眼的类人人皮骨骼面孔（无眼眶、无眉弓眼目）；
2. 眼睛位置强制锁定：真正的血红/赤金色贪婪巨眼，必须明确生长在左右双前肢与躯干连接处的深邃腋窝（Axillary / under the armpits / beneath shoulder blades）深处；
3. 羊身毛皮质感强化：上一轮第4帧躯干过于光滑拟人，丢失了羊身属性。必须全帧统一为覆盖着浓密、纠结、粗砺的黑色/深灰太古长羊毛（Shaggy thick sheep wool/fleece），带有盘曲公羊巨角；
4. 虎齿人爪写实化：口裂至耳后，剑齿虎交错尖牙滴落涎水；四肢末端为骨节粗大的苍白五指人手，带有黑曜石利爪；
5. 场景质感统一：钩吾之山必须严格呈现“其上多玉，其下多铜”——山巅冷冽暗绿古玉矿脉，山下赤红铜矿与生锈商周青铜祭祀巨鼎，暴雨雷电与青铜绿雾。
"""

def call_gemini_4(messages, temperature=0.2, max_tokens=3500):
    url = f"{BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gemini-4-argon",
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"]

def generate_v2_prompts():
    print("[1/5] Calling Gemini 4 Argon to reverse-engineer revised, audit-compliant prompts...")
    system_prompt = (
        "You are an elite Hollywood Creature Concept Artist (specializing in Weta Workshop / Guillermo del Toro style dark fantasy) "
        "and Ancient Chinese Mythological Scholar.\n"
        "We are revising the previous rejected prompts of 饕餮 (Taotie) based on strict visual audit feedback.\n\n"
        "CRITICAL RULES TO PASS THE AUDIT:\n"
        "1. THE FACE MUST BE TOTALLY EYELESS: A smooth, creepy, pale porcelain-like human face mask, NO eyes on face, NO eye sockets, NO brows. Only a giant mouth splitting wide to ears.\n"
        "2. THE EYES MUST BE UNDER THE ARMPITS: Two glowing predatory crimson-gold slit eyes are placed strictly inside the armpits beneath the front limbs / behind the shoulder joints.\n"
        "3. THE BODY IS SHAGGY SHEEP WOOL: Massive quadrupedal ram body covered in dense, dark matted sheep wool/fleece with enormous spiral ram horns.\n"
        "4. TIGER FANGS & HUMAN TALONS: Interlocking saber fangs, five-fingered human hands with black claws.\n"
        "5. MOUNT GOUWU ENVIRONMENT: Upper peaks of dark green raw jade, lower cliffs of exposed raw red copper and verdigris bronze sacrificial cauldrons under dark lightning storm.\n\n"
        "Output ONLY valid JSON with this structure:\n"
        "{\n"
        "  \"revision_notes\": \"Summary of how the audit issues were fixed\",\n"
        "  \"frames\": [\n"
        "    {\n"
        "      \"frame_number\": 1,\n"
        "      \"title\": \"Establishing Shot - Eyeless Silhouette on Gouwu Cauldron\",\n"
        "      \"prompt_en\": \"...\",\n"
        "      \"prompt_zh\": \"...\"\n"
        "    },\n"
        "    {\n"
        "      \"frame_number\": 2,\n"
        "      \"title\": \"Profile Medium - The Shaggy Ram Body & Armpit Eye Reveal\",\n"
        "      \"prompt_en\": \"...\",\n"
        "      \"prompt_zh\": \"...\"\n"
        "    },\n"
        "    {\n"
        "      \"frame_number\": 3,\n"
        "      \"title\": \"Extreme Macro - The Axillary Eye Deep in the Fleece\",\n"
        "      \"prompt_en\": \"...\",\n"
        "      \"prompt_zh\": \"...\"\n"
        "    },\n"
        "    {\n"
        "      \"frame_number\": 4,\n"
        "      \"title\": \"Dynamic Roar - The Devouring Tiger Fangs & Twin Armpit Glares\",\n"
        "      \"prompt_en\": \"...\",\n"
        "      \"prompt_zh\": \"...\"\n"
        "    },\n"
        "    {\n"
        "      \"frame_number\": 5,\n"
        "      \"title\": \"Grand Finale - Exiled Sovereign on the Copper Throne\",\n"
        "      \"prompt_en\": \"...\",\n"
        "      \"prompt_zh\": \"...\"\n"
        "    }\n"
        "  ],\n"
        "  \"video_prompt_5s\": \"(Optimized 5-second cinematic prompt for Kling v2.6 showcasing the quadrupedal shaggy beast walking on Mount Gouwu, camera tracking low to reveal the glowing eyes in the armpits, then roaring toward the thunderstorm)\"\n"
        "}"
    )

    raw = call_gemini_4([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{AUDIT_FEEDBACK_GUIDELINES}\nPlease generate the updated JSON prompt suite now."}
    ])

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        data = json.loads(match.group(0), strict=False)
        return data
    else:
        raise RuntimeError(f"Failed to parse JSON: {raw[:300]}")

def render_image(prompt, output_path):
    url = f"{BASE_URL}/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-image-2.6-sunburst",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        item = res["data"][0]
        if "b64_json" in item:
            with open(output_path, "wb") as f:
                f.write(base64.b64decode(item["b64_json"]))
        elif "url" in item:
            urllib.request.urlretrieve(item["url"], output_path)
    return output_path

def generate_kling_v26_video(prompt, output_file, max_wait=360):
    print(f"[*] Submitting video generation to Kling v2.6 (Flagship)...")
    url = f"{BASE_URL}/klingai/v1/videos/text2video"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model_name": "kling-v2-6",
        "prompt": prompt,
        "duration": "5"
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        task_id = res["data"]["task_id"]
        print(f"[+] Kling v2.6 task started: {task_id}")

    print(f"[*] Polling Kling v2.6 task {task_id} (timeout {max_wait}s)...")
    query_url = f"{BASE_URL}/klingai/v1/videos/text2video/{task_id}"
    query_headers = {"Authorization": f"Bearer {API_KEY}"}

    start_time = time.time()
    while time.time() - start_time < max_wait:
        q_req = urllib.request.Request(query_url, headers=query_headers)
        with urllib.request.urlopen(q_req) as q_resp:
            q_data = json.loads(q_resp.read().decode("utf-8"))
            status = q_data.get("data", {}).get("task_status")
            print(f"    - Kling v2.6 status: {status} ({int(time.time() - start_time)}s elapsed)")
            if status in ["succeed", "success"]:
                v_url = q_data["data"]["task_result"]["videos"][0]["url"]
                print(f"[+] Downloading Kling v2.6 video from {v_url}...")
                urllib.request.urlretrieve(v_url, output_file)
                print(f"[+] Successfully saved video to: {output_file}")
                return output_file
            elif status in ["failed", "error"]:
                raise RuntimeError(f"Kling v2.6 failed: {q_data}")
        time.sleep(12)
    raise TimeoutError("Kling v2.6 timed out")

def audit_v2_media(frame_files, video_file):
    print("[4/5] Calling Gemini 4 Argon to re-audit the revised assets against previous feedback...")
    content = [
        {
            "type": "text",
            "text": (
                "You are the Senior Visual Effects Supervisor and Mythological Authenticity Auditor.\n"
                "Review these 5 REVISED cinematic frames of 饕餮 (Taotie) generated after correcting the previous audit findings.\n\n"
                "STRICT AUDIT CRITERIA:\n"
                "1. Eyeless Human Face Compliance: Is the face completely free of eyes/eye sockets, displaying a smooth pale mask with giant tiger-fanged jaws?\n"
                "2. Eyes in Armpits ('其目在腋下'): Are the primary predatory eyes situated strictly beneath the shoulders / inside the armpits?\n"
                "3. Shaggy Sheep Body ('羊身'): Is the body clearly quadrupedal with thick matted sheep wool/fleece and ram horns?\n"
                "4. Humanoid Talons ('人爪'): Are the front paws articulated five-fingered human hands with black claws?\n"
                "5. Mount Gouwu Scene ('上多玉，下多铜'): Are the jade peaks, raw copper cliffs, and bronze cauldrons accurately integrated?\n\n"
                "Output a formal Audit Report in Markdown:\n"
                "- Comparative Progress (How it compares to V1)\n"
                "- Frame-by-Frame Verdict\n"
                "- Numerical Scores (1-100) for Canon Compliance, Scene Authenticity, and Cinematic Quality\n"
                "- Final Audit Status: [PASSED - CANONICAL MASTERPIECE] or [REVISE]\n"
            )
        }
    ]

    for i, path in enumerate(frame_files):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        content.append({
            "type": "text",
            "text": f"--- Revised Frame {i+1} ---"
        })
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64}"
            }
        })

    payload = {
        "model": "gemini-4-argon",
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.2,
        "max_tokens": 3000
    }
    url = f"{BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"]

def main():
    print("=" * 60)
    print(">>> 饕餮 (TAOTIE) V2 纠偏反推、高精重塑与二次审核系统 <<<")
    print("=" * 60)

    # 1. Reverse-engineer V2 prompts
    v2_data = generate_v2_prompts()
    clean_v2 = {}
    for k, v in v2_data.items():
        clean_v2[k.strip()] = v
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(clean_v2, f, ensure_ascii=False, indent=2)

    # 2. Render 5 V2 frames
    print("\n[2/5] Rendering 5 Corrected Film Frames with GPT-Image-2.6-Sunburst...")
    frame_files = []
    for idx, fmeta in enumerate(clean_v2.get("frames", [])):
        out_path = os.path.join(OUTPUT_DIR, f"taotie_v2_frame_{idx+1:02d}.png")
        print(f"[*] Rendering V2 Frame {idx+1}/5: {fmeta.get('title')}...")
        render_image(fmeta.get("prompt_en"), out_path)
        frame_files.append(out_path)
        print(f"[+] Saved V2 Frame {idx+1} to {out_path}")

    # 3. Generate Kling v2.6 5s Video
    print("\n[3/5] Generating 5s Video with Kling v2.6 Flagship Engine...")
    v_prompt = clean_v2.get("video_prompt_5s", "Cinematic mythological beast Taotie on Mount Gouwu")
    try:
        generate_kling_v26_video(v_prompt, VIDEO_FILE, max_wait=360)
    except Exception as e:
        print(f"[!] Warning on Kling v2.6 video: {e}")

    # 4. Multi-modal Audit
    audit_report = audit_v2_media(frame_files, VIDEO_FILE)

    # 5. Compile dossier
    print("\n[5/5] Compiling V2 Audit Report Dossier...")
    abs_video_path = os.path.abspath(VIDEO_FILE).replace("\\", "/")
    video_base = os.path.basename(VIDEO_FILE)

    full_md = f"""# 上古凶兽《饕餮》V2 纠偏重塑与终审验收报告

**反推与编导模型**: `gemini-4-argon` (基于审核打回意见与成熟原画二次反推)  
**高保真渲染引擎**: `gpt-image-2.6-sunburst` (OpenAI 2026 最新高保真图像模型)  
**旗舰视频生成引擎**: `kling-v2-6` (可灵 AI 2026 旗舰级电影视频大模型)  
**终审审计验收**: `gemini-4-argon` (多模态视觉 QA 与古籍还原度审查)  

---

## 一、 V2 审核纠偏对比与优化策略

{clean_v2.get('revision_notes', 'N/A')}

---

## 二、 V2 纠偏后的 5 张影视级分镜帧图与提示词

"""
    for idx, fmeta in enumerate(clean_v2.get("frames", [])):
        frame_name = f"taotie_v2_frame_{idx+1:02d}.png"
        abs_img_path = os.path.abspath(os.path.join(OUTPUT_DIR, frame_name)).replace("\\", "/")
        full_md += f"""### 分镜 {idx+1}：{fmeta.get('title')}
- **对应生成图**: [{frame_name}](file:///{abs_img_path})
- **纠偏英文 Prompt**:
```text
{fmeta.get('prompt_en')}
```
- **中文导演指令**:
> {fmeta.get('prompt_zh')}

---
"""

    full_md += f"""## 三、 Kling v2.6 旗舰级 5 秒短视频成果

- **视频文件路径**: [{video_base}](file:///{abs_video_path})
- **Kling v2.6 动态提示词**:
```text
{v_prompt}
```

---

## 四、 Gemini 4 Argon 终审验收审计报告

{audit_report}

---
*全案所有 V2 资产保存在 `{OUTPUT_DIR}` 目录。*
"""
    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(full_md)

    print(f"\n[OK] V2 Pipeline completed successfully! Report saved to {REPORT_MD}")

if __name__ == "__main__":
    main()

