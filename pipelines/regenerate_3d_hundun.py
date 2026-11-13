import os
import json
import shutil
import urllib.request

API_KEY = "sk-cnzllmkkxcadhnnihvdahaoaurhvnizhlyyjgqlkrubnsaxr"
OUTPUT_DIR = r"c:\Users\33046\Desktop\short video\four_beasts_3d_assets"
ARTIFACT_DIR = r"C:\Users\33046\.gemini\antigravity\brain\aab1cc86-842f-45bf-bfe8-713048b14715"

prompt = (
    "Hyper-realistic 3D CGI movie render, Shan Hai Jing ancient primordial beast Hundun (Dijiang). "
    "Black Myth cinematic aesthetic, Unreal Engine 5, Octane render, ray tracing, 8k resolution. "
    "Canonical creature design: a colossal beast-like primordial titan, body like a massive crimson and molten-gold chimera behemoth. "
    "Completely faceless smooth head with no eyes, no nose, no mouth, radiating dark matter gravitational waves. "
    "Six heavy reptilian beast legs with razor talons, four massive feathered wings spreading wide across the dark sky with realistic individual feathers and embers. "
    "Perched on a shattered floating mountain in an abyss void, volumetric dark clouds, gravitational lensing, "
    "subsurface scattering, photorealistic skin and feather grooming, IMAX cinematic lighting, masterpiece, no humanoid biped."
)

negative_prompt = (
    "human, biped, humanoid man, superhero, 2D, hand-drawn, cartoon, anime, illustration, flat color, sketch, low poly, blur"
)

url = "https://api.siliconflow.cn/v1/images/generations"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
payload = {
    "model": "Qwen/Qwen-Image",
    "prompt": prompt,
    "negative_prompt": negative_prompt,
    "image_size": "1024x1024",
    "batch_size": 1,
    "num_inference_steps": 30,
    "guidance_scale": 7.5
}

print("Submitting optimized 3D Hundun prompt...")
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
with urllib.request.urlopen(req, timeout=120) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    img_url = data['images'][0]['url']
    
img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(img_req, timeout=60) as img_resp:
    img_data = img_resp.read()
    
local_path = os.path.join(OUTPUT_DIR, "ref_3d_hundun.png")
with open(local_path, "wb") as f:
    f.write(img_data)
    
artifact_path = os.path.join(ARTIFACT_DIR, "ref_3d_hundun.png")
shutil.copyfile(local_path, artifact_path)
print("Optimized 3D Hundun successfully generated and replaced!")

