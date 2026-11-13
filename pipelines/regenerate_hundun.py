import os
import json
import shutil
import urllib.request

API_KEY = "sk-cnzllmkkxcadhnnihvdahaoaurhvnizhlyyjgqlkrubnsaxr"
OUTPUT_DIR = r"c:\Users\33046\Desktop\short video\four_beasts_assets"
ARTIFACT_DIR = r"C:\Users\33046\.gemini\antigravity\brain\aab1cc86-842f-45bf-bfe8-713048b14715"

prompt = (
    "2D hand-drawn Chinese donghua aesthetic, traditional Chinese ink wash painting, "
    "Shan Hai Jing primordial beast Hundun (Dijiang). Pure 2D anime cel shading, bold calligraphic ink lines, "
    "flying white brushstrokes. Canonical beast design: massive plump mythological beast with crimson and fiery gold body, "
    "completely faceless without any eyes, ears, nose, or mouth, smooth skin with glowing red and gold ancient mystical runes, "
    "six powerful beast legs, four majestic feathered ink wings spreading wide. "
    "Suspended in a cosmic swirling ink vortex of black and white yin-yang void, levitating shattered rocks, "
    "dark prehistoric myth, epic, grand scale, masterpiece, absolutely no 3D render, no human clothing, no human face."
)

negative_prompt = (
    "human, person, human head, human face, mask, bag, clothes, clothing, purse, "
    "3D render, octane render, unreal engine, photorealistic, CGI, plastic, deformed, ugly"
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

print("Submitting optimized Hundun prompt...")
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
with urllib.request.urlopen(req, timeout=120) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    img_url = data['images'][0]['url']
    
img_req = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(img_req, timeout=60) as img_resp:
    img_data = img_resp.read()
    
local_path = os.path.join(OUTPUT_DIR, "ref_beast_hundun.png")
with open(local_path, "wb") as f:
    f.write(img_data)
    
artifact_path = os.path.join(ARTIFACT_DIR, "ref_beast_hundun.png")
shutil.copyfile(local_path, artifact_path)
print("Optimized Hundun successfully generated and replaced!")
