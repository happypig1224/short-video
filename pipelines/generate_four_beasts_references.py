import os
import json
import shutil
import urllib.request
import concurrent.futures

API_KEY = "sk-cnzllmkkxcadhnnihvdahaoaurhvnizhlyyjgqlkrubnsaxr"
OUTPUT_DIR = r"c:\Users\33046\Desktop\short video\four_beasts_assets"
ARTIFACT_DIR = r"C:\Users\33046\.gemini\antigravity\brain\aab1cc86-842f-45bf-bfe8-713048b14715"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

PROMPTS = {
    "ref_beast_hundun": {
        "name": "混沌 (Hundun) - 虚无无相之尊",
        "prompt": "2D hand-drawn Chinese donghua aesthetic, traditional Chinese ink wash painting, Shan Hai Jing mythological beast Hundun. Pure 2D anime cel shading, bold calligraphic brush lineart, flying white ink splatter. Canonical lore: body like a red-gold sack, six legs, four feathered wings, completely faceless with no eyes, nose, or mouth, face is a swirling vortex of black and white void ink mist and golden divine runes. Surrounded by inverted floating rocks torn by void spacetime, yin-yang gravity reversal, primordial chaos aura, dark fantasy Oriental mythology, masterpiece, 8k resolution, absolutely no 3D render.",
        "negative_prompt": "3D render, octane render, unreal engine, photorealistic, CGI, plastic, smooth 3d model, western dragon, western fantasy, bad anatomy, deformed limbs"
    },
    "ref_beast_qiongqi": {
        "name": "穷奇 (Qiongqi) - 嗜杀裂天之翼",
        "prompt": "2D hand-drawn Chinese donghua aesthetic, traditional Chinese ink wash painting, Shan Hai Jing mythological beast Qiongqi. Pure 2D anime cel shading, bold calligraphic brush lineart, splash ink splatter. Canonical lore: massive tiger body as huge as an ox with black-and-white stripes, huge feathered wings spanning the sky on its back with crimson blood glow and lightning arcs. Blood-red glowing eyes, razor-sharp protruding tusks, stiff hedgehog-like needle fur. Standing in a crimson blood lightning storm, tearing the sky with ink wind blades, roaring ferociously, slaughter and malice aura, dynamic epic composition, masterpiece, absolutely no 3D render.",
        "negative_prompt": "3D render, octane render, unreal engine, photorealistic, CGI, plastic, smooth 3d model, western dragon, western fantasy, bad anatomy, deformed limbs"
    },
    "ref_beast_taowu": {
        "name": "梼杌 (Taowu) - 傲骨裂岳之蛮",
        "prompt": "2D hand-drawn Chinese donghua aesthetic, traditional Chinese ink wash painting, mythological ferocious beast Taowu from Shen Yi Jing. Pure 2D anime cel shading, bold calligraphic brush lineart, flying white splash ink. Canonical lore: massive body like a volcanic rock mountain, fierce human face with protruding wild boar tusks, tiger paws and claws, long steel-needle fur covering the body, an eighteen-foot iron python tail. Broken ancient bronze sealing chains around its massive wrists, stomping cracked lava ground and permafrost, roaring proudly against golden divine heavenly lightning strikes, unyielding primordial beast titan, masterpiece, absolutely no 3D render.",
        "negative_prompt": "3D render, octane render, unreal engine, photorealistic, CGI, plastic, smooth 3d model, western dragon, western fantasy, bad anatomy, deformed limbs"
    },
    "ref_beast_taotie": {
        "name": "饕餮 (Taotie) - 终焉吞天之口",
        "prompt": "2D hand-drawn Chinese donghua aesthetic, traditional Chinese ink wash painting, Shan Hai Jing mythological beast Taotie. Pure 2D anime cel shading, bold calligraphic brush lineart, flying white splash ink. Canonical lore: sheep body with a human-like eerie face, canonical eyes located uniquely under its armpits glowing with blood-red evil light, tiger teeth and human claws. Covered in ancient Zhou dynasty bronze Taotie vessel patterns, chest and torso splitting open into a massive black hole void abyss mouth that swallows mountains, stars, and celestial fire, endless greed, apocalyptic consumption, masterpiece, absolutely no 3D render.",
        "negative_prompt": "3D render, octane render, unreal engine, photorealistic, CGI, plastic, smooth 3d model, western dragon, western fantasy, bad anatomy, deformed limbs"
    },
    "ref_scene_primordial_wilderness": {
        "name": "荒古大荒世界观场景 (Primordial Wilderness)",
        "prompt": "2D hand-drawn Chinese donghua aesthetic, traditional Chinese splash ink wash painting, ancient primordial wilderness of Shan Hai Jing mythology. Aged parchment paper texture background, bold ink brushwork depicting broken thousand-mile mountain peaks and collapsed Buzhou Mountain. Sky torn into crimson and black storm clouds with blood lightning, inverted ancient bronze stele and shattered divine chains floating in midair, glowing red magma fissures meeting deep abyss frost. Ethereal ink mist, grand desolate prehistoric epic scale, dark Oriental fantasy landscape, masterpiece, absolutely no 3D render.",
        "negative_prompt": "3D render, octane render, unreal engine, photorealistic, CGI, modern buildings, western fantasy"
    }
}

def generate_image(key, info):
    print(f"[START] Generating {info['name']} ({key})...")
    url = "https://api.siliconflow.cn/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen-Image",
        "prompt": info["prompt"],
        "negative_prompt": info["negative_prompt"],
        "image_size": "1024x1024",
        "batch_size": 1,
        "num_inference_steps": 30,
        "guidance_scale": 7.5
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            img_url = data['images'][0]['url']
            
            # Download image
            img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(img_req, timeout=60) as img_resp:
                img_data = img_resp.read()
                
            local_path = os.path.join(OUTPUT_DIR, f"{key}.png")
            with open(local_path, "wb") as f:
                f.write(img_data)
                
            artifact_path = os.path.join(ARTIFACT_DIR, f"{key}.png")
            shutil.copyfile(local_path, artifact_path)
            
            print(f"[SUCCESS] {key} generated and saved to {local_path} and {artifact_path}")
            return key, local_path, artifact_path, None
    except Exception as e:
        print(f"[ERROR] Failed to generate {key}: {e}")
        return key, None, None, str(e)

if __name__ == "__main__":
    print(f"Submitting {len(PROMPTS)} reference generation tasks in parallel...")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_key = {executor.submit(generate_image, k, v): k for k, v in PROMPTS.items()}
        for future in concurrent.futures.as_completed(future_to_key):
            k, l_path, a_path, err = future.result()
            results[k] = {"local": l_path, "artifact": a_path, "error": err}
            
    print("\nGeneration summary:")
    print(json.dumps(results, indent=2))
