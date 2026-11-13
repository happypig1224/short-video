import os
import json
import shutil
import urllib.request
import concurrent.futures

API_KEY = "sk-cnzllmkkxcadhnnihvdahaoaurhvnizhlyyjgqlkrubnsaxr"
OUTPUT_DIR = r"c:\Users\33046\Desktop\short video\four_beasts_3d_assets"
ARTIFACT_DIR = r"C:\Users\33046\.gemini\antigravity\brain\aab1cc86-842f-45bf-bfe8-713048b14715"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

PROMPTS_3D = {
    "ref_3d_hundun": {
        "name": "3D写实 混沌 (Hundun) - 虚无无相之尊",
        "prompt": (
            "Hyper-realistic 3D CGI movie render, Shan Hai Jing ancient primordial beast Hundun. "
            "Black Myth cinematic aesthetic, Unreal Engine 5, Octane render, 8k resolution. "
            "Canonical creature design: a colossal primordial behemoth with a massive, plump, muscular crimson and molten-gold body. "
            "Completely faceless with no eyes, ears, nose, or mouth, a smooth abyssal head radiating dark gravitational energy and heat shimmer. "
            "Six massive beast limbs with heavy razor claws, four gigantic feathered wings spreading wide with individual realistic feathers and glowing embers. "
            "Hovering above a floating shattered obsidian monolith, surrounded by realistic volumetric dark mist, gravitational lensing distortion, "
            "subsurface scattering, hyper-detailed skin texture, cinematic rim lighting, photorealistic dark fantasy."
        ),
        "negative_prompt": "2D, hand-drawn, cartoon, anime, illustration, flat color, sketch, low poly, human clothes, human face, bad anatomy, blur"
    },
    "ref_3d_qiongqi": {
        "name": "3D写实 穷奇 (Qiongqi) - 嗜杀裂天之翼",
        "prompt": (
            "Hyper-realistic 3D CGI movie render, Shan Hai Jing ancient ferocious beast Qiongqi. "
            "Black Myth cinematic aesthetic, Unreal Engine 5, Octane render, ray tracing, 8k resolution. "
            "Canonical creature design: colossal demonic saber-toothed tiger as huge as an ox, white and black realistic fur groom, "
            "two heavy obsidian curved horns on its head. On its back, two massive leathery feathered wings span across the sky, crackling with crimson red plasma lightning. "
            "Glowing blood-red predator eyes, sharp protruding ivory fangs dripping saliva, stiff hedgehog-like needle spines along its spine. "
            "Prowling menacingly on a shattered crag under a crimson thunderstorm, volumetric fog, photorealistic muscle anatomy, IMAX cinematic shot."
        ),
        "negative_prompt": "2D, hand-drawn, cartoon, anime, illustration, flat color, sketch, low poly, smooth plastic, bad anatomy, blur"
    },
    "ref_3d_taowu": {
        "name": "3D写实 梼杌 (Taowu) - 傲骨裂岳之蛮",
        "prompt": (
            "Hyper-realistic 3D CGI movie render, mythological primordial beast Taowu from ancient Chinese mythology. "
            "Black Myth cinematic aesthetic, Unreal Engine 5, Octane render, 8k resolution. "
            "Canonical creature design: massive behemoth like a volcanic titan, fierce weathered demonic human-like face with intense furious eyes, "
            "two gigantic curved wild boar tusks protruding from its jaws. Colossal tiger body with heavy muscular tiger claws, covered in two-meter long coarse dark fur like steel wire. "
            "An extremely long scaled reptilian python tail whipping through the air. Heavy broken ancient bronze sealing shackles around its wrists, "
            "standing on cracking magma rock and permafrost, golden heavenly lightning striking its back, hyper-detailed stone-like skin, volumetric smoke, photorealistic."
        ),
        "negative_prompt": "2D, hand-drawn, cartoon, anime, illustration, flat color, sketch, low poly, plastic, bad anatomy, blur"
    },
    "ref_3d_taotie": {
        "name": "3D写实 饕餮 (Taotie) - 终焉吞天之口",
        "prompt": (
            "Hyper-realistic 3D CGI movie render, Shan Hai Jing ancient gluttonous beast Taotie. "
            "Black Myth cinematic aesthetic, Unreal Engine 5, Octane render, 8k resolution. "
            "Canonical creature design: gigantic terrifying chimera with a muscular sheep-like body, curling ancient ram horns, fierce predator face with serrated tiger teeth. "
            "Canonical feature: sinister glowing red organic demonic eyes embedded underneath its armpits and shoulder joints. "
            "Torso clad in ancient weathered Zhou dynasty bronze armor plates fused with flesh and bone. Its entire chest cavity splits open into an abyss black hole vortex mouth, "
            "swallowing rocky debris, fire, and light with gravitational distortion. Razor-sharp humanoid hand-claws, hyper-detailed textures, cinematic volumetric lighting, photorealistic horror."
        ),
        "negative_prompt": "2D, hand-drawn, cartoon, anime, illustration, flat color, sketch, low poly, plastic, bad anatomy, blur"
    },
    "ref_3d_primordial_wilderness": {
        "name": "3D写实 荒古世界观场景 (Primordial Wilderness)",
        "prompt": (
            "Hyper-realistic 3D CGI environment cinematic still, ancient desolate prehistoric Shan Hai Jing mythological landscape. "
            "Unreal Engine 5 Nanite and Lumen, Octane render, 8k resolution, IMAX cinematic wide angle. "
            "Towering jagged shattered basalt mountain peaks, collapsed primordial mountain range Buzhou Mountain. "
            "A colossal fissure canyon split with glowing molten orange-red magma colliding with frozen glaciers. "
            "Sky filled with swirling ominous dark storm clouds pierced by crimson blood lightning, gigantic shattered ancient bronze steles and broken sealing chains floating in mid-air. "
            "Volumetric atmospheric fog, photorealistic rock erosion, hyper-detailed textures, dark fantasy epic scale."
        ),
        "negative_prompt": "2D, hand-drawn, cartoon, anime, illustration, flat color, sketch, modern buildings, low poly, blur"
    }
}

def generate_image_3d(key, info):
    print(f"[START 3D] Generating {info['name']} ({key})...")
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
            
            img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(img_req, timeout=60) as img_resp:
                img_data = img_resp.read()
                
            local_path = os.path.join(OUTPUT_DIR, f"{key}.png")
            with open(local_path, "wb") as f:
                f.write(img_data)
                
            artifact_path = os.path.join(ARTIFACT_DIR, f"{key}.png")
            shutil.copyfile(local_path, artifact_path)
            
            print(f"[SUCCESS 3D] {key} saved to {local_path} and {artifact_path}")
            return key, local_path, artifact_path, None
    except Exception as e:
        print(f"[ERROR 3D] Failed to generate {key}: {e}")
        return key, None, None, str(e)

if __name__ == "__main__":
    print(f"Submitting 5 3D realistic reference tasks in parallel...")
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_key = {executor.submit(generate_image_3d, k, v): k for k, v in PROMPTS_3D.items()}
        for future in concurrent.futures.as_completed(future_to_key):
            k, l_path, a_path, err = future.result()
            results[k] = {"local": l_path, "artifact": a_path, "error": err}
            
    print("\n3D Generation summary:")
    print(json.dumps(results, indent=2))

