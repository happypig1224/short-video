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

# Output directories and filenames
OUTPUT_DIR = "taotie_cinematic"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REPORT_MD = os.path.join(OUTPUT_DIR, "taotie_cinematic_report.md")
RESULT_JSON = os.path.join(OUTPUT_DIR, "taotie_cinematic_data.json")
VIDEO_FILE = os.path.join(OUTPUT_DIR, "taotie_cinematic_5s.mp4")

SHANHAIJING_LORE = """
【上古权威文献考据库】：
1. 《山海经·北山经》：“又北三百五十里，曰钩吾之山，其上多玉，其下多铜。有兽焉，其状如羊身人面，其目在腋下，虎齿人爪，其音如婴儿，名曰狍鸮，是食人。”
2. 郭璞注及《图赞》：“为物贪婪，食人未尽，还害其身，像在夏鼎，左传所谓饕餮是也。”“狍鸮贪惏，其目在腋。食人未尽，还自龈割。图形妙鼎，是谓不若。”
3. 《吕氏春秋·先识览》：“周鼎著饕餮，有首无身，食人未咽，害及其身，以言报更也。”
4. 《左传·文公十八年》与《史记》：“缙云氏有不才子，贪于饮食，冒于货贿……天下之民以比三凶，谓之饕餮。舜流四凶族，投诸四裔，以御魑魅。”
5. 《神异经·西南荒经》：“身多毛，头上戴豕。贪如狼恶，好自积财，而不食人谷，强者夺老弱者，名曰饕餮。”
【核心常驻场景】：
太古钩吾之山之巅与四裔荒蛮禁地。地质奇观——山体上覆风化古玉石矿（碧玉、血玉苍茫冷硬），山下暴露出巨大的赤铜与黄铜矿脉；远古青铜祭祀巨鼎与血迹斑驳的石台矗立在狂暴雷云与深渊断崖之畔；周身弥漫着青铜锈色与赤红煞气，上古蛮荒神魔战场的压迫感。
"""

def call_llm(messages, model="gemini-4-argon", temperature=0.3, max_tokens=4000):
    url = f"{BASE_URL}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"]

def generate_prompts_with_gemini4():
    print("[1/5] Calling Gemini 4 Argon to reverse-engineer ultra-detailed prompts for Taotie and its native scene...")
    system_prompt = (
        "You are an elite Hollywood Film Concept Director, Master Cinematographer, and Ancient Chinese Mythological Scholar.\n"
        "Based on the provided authoritative historical lore of 饕餮 (Taotie) and its native habitat 'Gouwu Mountain', "
        "synthesize an exhaustive, cinematic visual breakdown and generate 5 sequential movie frame prompts and 1 cohesive 5s video prompt.\n\n"
        "STRICT VISUAL ANATOMY OF TAOTIE:\n"
        "- Body: Gigantic, powerful muscular sheep-like body (羊身) covered with coarse matted dark fur and primordial scales;\n"
        "- Head & Mouth: Grotesque, humanoid skull face (人面) with zero eyes on the forehead/face, massive jaw split wide to ears packed with interlocking, savage saber-tiger fangs (虎齿), thick saliva, primordial bronze aura;\n"
        "- EYES UNDER ARMPITS (其目在腋下 - CRITICAL): True predatory, sinister, glowing crimson-amber eyes situated deep inside the armpits beneath the front limbs, glaring with insatiable greed;\n"
        "- Claws: Articulated human-like 5-finger talons with razor obsidian claws (人爪) capable of grasping and tearing;\n"
        "- Headless/Head-focused philosophy (有首无身): Overwhelming demonic skull dominance, devouring without bottom;\n"
        "- Scene (钩吾之山): Peak of Mount Gouwu, rugged raw jade veins above, exposed raw copper/bronze ore below, ancient colossal ritual cauldrons (周鼎/夏鼎), swirling ominous storm clouds, bronze-green miasma and red mist.\n\n"
        "Output ONLY a JSON object with this exact structure:\n"
        "{\n"
        "  \"scene_breakdown\": \"Deep textual description of the native environment (Mount Gouwu, bronze veins, jade rocks, weather, atmospheric lighting)\",\n"
        "  \"taotie_anatomy\": \"Exhaustive breakdown of Taotie's physical, textural, and terrifying features\",\n"
        "  \"frames\": [\n"
        "    {\n"
        "      \"frame_number\": 1,\n"
        "      \"title\": \"Establishing Shot - The Primordial Realm of Mount Gouwu\",\n"
        "      \"prompt_en\": \"(80-120 words cinematic prompt for GPT-Image-2.6 Sunburst)\",\n"
        "      \"prompt_zh\": \"(中文提示词)\"\n"
        "    },\n"
        "    {\n"
        "      \"frame_number\": 2,\n"
        "      \"title\": \"Medium Shot - The Beast on the Copper Altar\",\n"
        "      \"prompt_en\": \"...\",\n"
        "      \"prompt_zh\": \"...\"\n"
        "    },\n"
        "    {\n"
        "      \"frame_number\": 3,\n"
        "      \"title\": \"Macro Detail - The Sinister Eyes Beneath the Armpit\",\n"
        "      \"prompt_en\": \"...\",\n"
        "      \"prompt_zh\": \"...\"\n"
        "    },\n"
        "    {\n"
        "      \"frame_number\": 4,\n"
        "      \"title\": \"Action / Roar - The Devouring Maw and Human Claws\",\n"
        "      \"prompt_en\": \"...\",\n"
        "      \"prompt_zh\": \"...\"\n"
        "    },\n"
        "    {\n"
        "      \"frame_number\": 5,\n"
        "      \"title\": \"Climax - Lord of the Four Perils in Thunderstorm\",\n"
        "      \"prompt_en\": \"...\",\n"
        "      \"prompt_zh\": \"...\"\n"
        "    }\n"
        "  ],\n"
        "  \"video_prompt_5s\": \"(Highly dynamic 5-second cinematic camera prompt for Kling video generator capturing Taotie's crawl, eye glow in armpits, roar, and thunder over Mount Gouwu)\"\n"
        "}"
    )

    user_msg = f"{SHANHAIJING_LORE}\n\nPlease generate the complete prompt suite now."
    raw = call_llm([{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}], model="gemini-4-argon")
    
    # Parse JSON
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        data = json.loads(match.group(0), strict=False)
        return data
    else:
        raise RuntimeError(f"Failed to parse JSON from Gemini response: {raw[:300]}")

def generate_image_with_gpt_image(prompt, output_file):
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
            with open(output_file, "wb") as f:
                f.write(base64.b64decode(item["b64_json"]))
        elif "url" in item:
            urllib.request.urlretrieve(item["url"], output_file)
        else:
            raise RuntimeError(f"Unexpected image result: {res}")
    return output_file

def submit_kling_video(prompt):
    print("[*] Submitting 5s video task to Kling AI on 302.ai...")
    url = f"{BASE_URL}/klingai/v1/videos/text2video"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model_name": "kling-v1",
        "prompt": prompt,
        "duration": "5"
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        task_id = res["data"]["task_id"]
        print(f"[+] Kling video task submitted! Task ID: {task_id}")
        return task_id

def poll_and_download_kling_video(task_id, output_path, max_wait=300):
    print(f"[*] Waiting for Kling video {task_id} to render (timeout {max_wait}s)...")
    url = f"{BASE_URL}/klingai/v1/videos/text2video/{task_id}"
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            status = data.get("data", {}).get("task_status")
            print(f"    - Task {task_id} status: {status} ({int(time.time() - start_time)}s elapsed)")
            
            if status in ["succeed", "success"]:
                result = data["data"].get("task_result", {})
                videos = result.get("videos", [])
                video_url = None
                if videos and len(videos) > 0:
                    video_url = videos[0].get("url")
                elif "url" in result:
                    video_url = result["url"]
                
                if video_url:
                    print(f"[+] Video ready! Downloading from {video_url}...")
                    urllib.request.urlretrieve(video_url, output_path)
                    print(f"[+] Successfully saved video to: {output_path}")
                    return output_path
                else:
                    raise RuntimeError(f"Video marked succeed but no URL found: {result}")
            elif status in ["failed", "error"]:
                msg = data.get("data", {}).get("task_status_msg", "Unknown error")
                raise RuntimeError(f"Kling task failed: {msg}")
        time.sleep(10)
    raise TimeoutError(f"Kling task timed out after {max_wait}s")

def audit_generated_media_with_gemini(frame_files, video_file, design_data):
    print("[4/5] Calling Gemini 4 Argon to audit and review the generated frames and assets...")
    content = [
        {
            "type": "text",
            "text": (
                "You are an elite Visual Quality Assurance Director, Senior Art Supervisor, and Academic Mythological Scholar.\n"
                "Please perform an authoritative, rigorous AUDIT of the following generated cinematic frames representing 饕餮 (Taotie) on Mount Gouwu.\n\n"
                "Review and score the assets strictly against the classical canon:\n"
                "1. [Shan Hai Jing Anatomical Accuracy (1-100)]:\n"
                "   - 羊身 (Sheep-like muscular body)\n"
                "   - 人面 (Grotesque humanoid skull face)\n"
                "   - 其目在腋下 (Eyes positioned inside the armpits / beneath shoulders, NOT on forehead)\n"
                "   - 虎齿 (Savage protruding tiger fangs)\n"
                "   - 人爪 (Articulated humanoid predatory talons)\n"
                "2. [Mythological Scene & Atmosphere (1-100)]:\n"
                "   - 钩吾之山 (Mount Gouwu: Jade rock formations above, raw copper/bronze ore veins below)\n"
                "   - 周鼎/古鼎 (Primordial ritual cauldrons and bronze sacrificial atmosphere)\n"
                "   - 电影级光影 (Cinematic lightning, volumetric fog, rim light, depth of field)\n"
                "3. [Production Quality & Cinematic Grade (1-100)]:\n"
                "   - Detail fidelity, texture micro-displacement, photorealism, and epic scale.\n\n"
                "Provide a structured markdown review including:\n"
                "- Overview & Executive Summary\n"
                "- Frame-by-Frame Detailed Critique\n"
                "- Canon Compliance Analysis (山海经合规度判读)\n"
                "- Numerical Scores across the 3 dimensions\n"
                "- Final Audit Verdict: [PASSED - CINEMATIC EXCELLENCE] or [REVISE]\n"
            )
        }
    ]

    for i, path in enumerate(frame_files):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        content.append({
            "type": "text",
            "text": f"--- Cinematic Frame {i+1} ---"
        })
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{b64}"
            }
        })

    payload = {
        "model": "gemini-4-argon",
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
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
    print(">>> 饕餮 (TAOTIE) 影视级全流程反推、生成与专业审核系统 <<<")
    print("=" * 60)

    # Step 1: Prompt Generation via Gemini 4 Argon
    prompt_data = generate_prompts_with_gemini4()
    with open(RESULT_JSON, "w", encoding="utf-8") as f:
        json.dump(prompt_data, f, ensure_ascii=False, indent=2)
    print("[+] Prompt suite saved to:", RESULT_JSON)

    # Step 2: Submit Kling 5s video task (async in background)
    video_prompt = prompt_data.get("video_prompt_5s", "Mythical beast Taotie roaring on Mount Gouwu")
    kling_task_id = submit_kling_video(video_prompt)

    # Step 3: Generate 5 Frames with GPT-Image-2.6-Sunburst
    print("\n[2/5] Generating 5 Cinematic Film Frames via GPT-Image-2.6-Sunburst...")
    frame_files = []
    frames_meta = prompt_data.get("frames", [])
    for idx, fmeta in enumerate(frames_meta):
        out_name = os.path.join(OUTPUT_DIR, f"taotie_frame_{idx+1:02d}.png")
        print(f"[*] Rendering Frame {idx+1}/5: {fmeta.get('title')}...")
        p = fmeta.get("prompt_en")
        generate_image_with_gpt_image(p, out_name)
        frame_files.append(out_name)
        print(f"[+] Frame {idx+1} rendered and saved to {out_name}")

    # Step 4: Await and download Kling Video
    print("\n[3/5] Polling and fetching Kling 5s Cinematic Video...")
    try:
        poll_and_download_kling_video(kling_task_id, VIDEO_FILE, max_wait=360)
    except Exception as e:
        print(f"[!] Warning on Kling video download: {e}")

    # Step 5: Multi-frame Visual Audit via Gemini 4 Argon
    audit_review = audit_generated_media_with_gemini(frame_files, VIDEO_FILE, prompt_data)

    # Step 6: Compile Full Report
    print("\n[5/5] Compiling Comprehensive Film Production & Audit Dossier...")
    full_report = f"""# 上古凶兽《饕餮》影视级全案制作与质检审计报告

**制作平台**: 302.AI 统一前沿引擎  
**反推与编导模型**: `gemini-4-argon` (Google 最新前沿多模态推理模型)  
**电影级生图引擎**: `gpt-image-2.6-sunburst` (OpenAI 2026 最新高保真渲染模型)  
**视频生成引擎**: `kling-v1` (可灵 AI 电影级视频生成系统)  
**质检与学术审计**: `gemini-4-argon` (多模态视觉 QA 与古籍还原度审查)  

---

## 一、 权威考据与微观解构

### 1. 饕餮形貌微观解构 (Anatomy Breakdown)
{prompt_data.get('taotie_anatomy', 'N/A')}

### 2. 常驻场景解构 (钩吾之山 Mount Gouwu)
{prompt_data.get('scene_breakdown', 'N/A')}

---

## 二、 5 张影视级分镜帧图与生成提示词

"""
    for idx, fmeta in enumerate(frames_meta):
        frame_img_name = f"taotie_frame_{idx+1:02d}.png"
        abs_img_path = os.path.abspath(os.path.join(OUTPUT_DIR, frame_img_name)).replace("\\", "/")
        full_report += f"""### 分镜 {idx+1}：{fmeta.get('title')}
- **对应生成图**: [{frame_img_name}](file:///{abs_img_path})
- **英文工业级 Prompt**:
```text
{fmeta.get('prompt_en')}
```
- **中文导演指令**:
> {fmeta.get('prompt_zh')}

---
"""

    abs_video_path = os.path.abspath(VIDEO_FILE).replace("\\", "/")
    video_base = os.path.basename(VIDEO_FILE)
    full_report += f"""## 三、 5 秒电影级短视频制作

- **视频文件路径**: [{video_base}](file:///{abs_video_path})
- **Kling AI 5秒动态专用 Prompt**:
```text
{video_prompt}
```

---

## 四、 专家级多模态视觉审计报告 (Gemini 4 Argon Audit)

{audit_review}

---
*全案所有分镜、短视频及数据资产已保存在 `{OUTPUT_DIR}` 目录。*
"""

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(full_report)

    print(f"\n[OK] Complete Pipeline executed successfully! Dossier saved to: {REPORT_MD}")

if __name__ == "__main__":
    main()
