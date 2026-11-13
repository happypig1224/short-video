import os
import sys
import json
import time
import shutil
import urllib.request
import subprocess
import numpy as np
import wave

API_KEY = "sk-cnzllmkkxcadhnnihvdahaoaurhvnizhlyyjgqlkrubnsaxr"
WORK_DIR = r"c:\Users\33046\Desktop\short video\four_beasts_3d_output"
ARTIFACT_DIR = r"C:\Users\33046\.gemini\antigravity\brain\aab1cc86-842f-45bf-bfe8-713048b14715"
STATE_FILE = os.path.join(WORK_DIR, "four_beasts_3d_state.json")

os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

SHOTS = [
    {
        "id": 1,
        "name": "荒古开天·神碑封印崩解",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render, IMAX shot. Ancient prehistoric wilderness, towering basalt mountains. A massive ancient bronze stele carved with divine runes floating in midair begins cracking violently, glowing crimson lightning arcs explode as gigantic iron chains shatter into pieces. Camera tilts rapidly up as dark clouds and volcanic ash swirl violently, dark fantasy epic trailer.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 2,
        "name": "混沌初现·虚空无相之影",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Primordial beast Hundun, colossal crimson and molten-gold chimera behemoth. Completely faceless smooth head radiating heat shimmer and dark gravitational waves. Four massive feathered dragon wings spread wide across the dark sky, shedding fiery embers. Camera circles around the beast as it perches on a floating obsidian rock, dark void mist swirling.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 3,
        "name": "混沌震翼·空间重力倒悬",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Primordial beast Hundun violently beats its four giant fiery wings, sending shockwaves of golden heat and dark matter. Surrounding floating mountains and boulders reverse gravity and shatter into airborne fragments. Extreme dynamic camera pull-back with lens flare and heat distortion.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 4,
        "name": "穷奇振翼·血雷撕裂夜空",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Ancient ferocious beast Qiongqi, colossal white tiger with black stripes and massive curved obsidian horns. Two enormous black feathered and leathery bone wings spread across a turbulent sky illuminated by violent crimson blood lightning. Glowing red eyes lock onto the camera, snarling menacingly.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 5,
        "name": "穷奇俯冲·狂风裂地猎杀",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Ferocious winged tiger Qiongqi dives from the storm clouds at supersonic speed towards the cracked rocky terrain. Claws slash forward leaving blazing red plasma arcs in the air, wind pressure obliterating trees and rocks, intense motion blur, dramatic cinematic low angle.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 6,
        "name": "穷奇长啸·嗜杀狂暴风暴",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Close-up of demonic winged tiger Qiongqi letting out a ferocious bloodcurdling roar, razor-sharp fangs dripping saliva, stiff quill spines bristling along its neck and back. Crimson lightning explodes behind its head, camera shaking with sonic shockwave effect.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 7,
        "name": "梼杌破渊·玄岩蛮躯踏地",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Volcanic rift canyon meeting frozen glaciers. Colossal primordial beast Taowu steps heavily out of the molten abyss, massive tiger body with rough stone armor skin and long coarse dark fur, weathered demonic human-like face, gigantic wild boar tusks curving outward, camera panning up its towering frame.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 8,
        "name": "梼杌裂岳·碎链撼山断岳",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Titan beast Taowu slams its massive claws into the basalt ground with immense force, shattering the earth into volcanic fissures. Broken ancient bronze sealing shackles on its wrists clang violently. An eighteen-foot scaled python tail whips through the air, knocking over a towering stone pillar.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 9,
        "name": "梼杌傲骨·硬抗九天金雷",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Nine golden divine lightning bolts strike violently down from the storm clouds onto Taowu's armored back. Sparks and molten rock spray everywhere, but the beast stands unyielding, roaring defiantly at the heavens with unbending primal fury, slow-motion epic cinematic framing.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 10,
        "name": "饕餮觉醒·腋下血瞳睁视",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Deep dark abyss. Ancient gluttonous beast Taotie steps into dim volumetric light, sheep body with curled horns, tiger fangs. Camera pushes in as multiple eerie organic demonic eyes embedded under its armpits snap open, glowing with blinding crimson evil energy, terrifying horror atmosphere.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 11,
        "name": "饕餮吞天·黑洞万象归寂",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Beast Taotie's chest cavity violently splits wide open into an apocalyptic black hole gravitational abyss. Blazing accretion disk swirls as surrounding mountain crags, magma rivers, and fiery clouds are sucked violently into its dark void chest. Extreme gravitational lensing distortion, apocalyptic scale.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    },
    {
        "id": 12,
        "name": "四凶乱世·乾坤终焉碰撞",
        "prompt": "Cinematic 3D CGI movie scene, Unreal Engine 5, Octane render. Epic wide aerial view of the shattered primordial continent. In the four directions of the storm-ravaged sky, silhouettes of Hundun's fire, Qiongqi's blood lightning, Taowu's volcanic wrath, and Taotie's black hole collide in a cataclysmic cosmic shockwave, fading into cinematic darkness with burning gold embers.",
        "negative_prompt": "2D, cartoon, anime, illustration, flat color, sketch, low poly, toy-like, smooth plastic, bad anatomy, deformed, blurry"
    }
]

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tasks": {}}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def check_task_status(req_id):
    url = "https://api.siliconflow.cn/v1/video/status"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"requestId": req_id}
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data
    except Exception as e:
        print(f"[WARNING] Status check failed for {req_id}: {e}")
        return None

def download_video(url, dest_path):
    print(f"[DOWNLOADING] {url} -> {dest_path}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        with open(dest_path, "wb") as f:
            f.write(resp.read())
    sz = os.path.getsize(dest_path)
    print(f"[DOWNLOADED] Saved to {dest_path} ({sz} bytes)")
    return sz > 0

def generate_60s_epic_soundtrack(output_wav_path):
    print(f"[AUDIO] Synthesizing 60.00s epic cinematic soundtrack -> {output_wav_path}...")
    sample_rate = 44100
    duration = 60.0
    num_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    
    audio = np.zeros(num_samples)
    
    # 1. 40Hz sub-bass dark rumble
    rumble = 0.25 * np.sin(2 * np.pi * 42 * t) * (1.0 + 0.3 * np.sin(2 * np.pi * 0.2 * t))
    audio += rumble
    
    # 2. Epic war drum beats (BPM accelerates: 80 BPM -> 100 BPM -> 120 BPM)
    drum_times = []
    # 00-15s: slow ominous hits every 1.5s
    for tm in np.arange(1.0, 15.0, 1.5):
        drum_times.append((tm, 0.8, 55.0))
    # 15-35s: medium battle tempo every 0.8s
    for tm in np.arange(15.0, 35.0, 0.8):
        drum_times.append((tm, 0.9, 65.0))
    # 35-55s: intense war drums every 0.5s with accent hits
    for tm in np.arange(35.0, 55.0, 0.5):
        accent = 1.0 if int(tm * 2) % 4 == 0 else 0.7
        drum_times.append((tm, accent, 75.0 if accent == 1.0 else 58.0))
    # 55-60s: final massive climax rolls + big impact at 58.2s
    for tm in np.arange(55.0, 58.0, 0.25):
        drum_times.append((tm, 0.85, 80.0))
    drum_times.append((58.2, 1.2, 45.0))
    
    for hit_time, amplitude, freq in drum_times:
        start_idx = int(hit_time * sample_rate)
        hit_len = int(0.7 * sample_rate)
        if start_idx + hit_len < num_samples:
            dt = np.linspace(0, 0.7, hit_len, endpoint=False)
            decay = np.exp(-dt * 7.0)
            pitch_drop = freq * np.exp(-dt * 8.0)
            drum_hit = amplitude * np.sin(2 * np.pi * pitch_drop * dt) * decay
            noise = 0.15 * amplitude * (np.random.rand(hit_len) * 2 - 1) * np.exp(-dt * 15.0)
            audio[start_idx:start_idx + hit_len] += (drum_hit + noise)
            
    # 3. Ancient bronze bell / chime resonances at key narrative transitions
    transition_times = [0.2, 15.0, 30.0, 45.0, 58.2]
    for tr in transition_times:
        start_idx = int(tr * sample_rate)
        chime_len = int(3.5 * sample_rate)
        if start_idx + chime_len < num_samples:
            dt = np.linspace(0, 3.5, chime_len, endpoint=False)
            decay = np.exp(-dt * 1.2)
            chime = 0.35 * (np.sin(2 * np.pi * 329.63 * dt) + 
                            0.5 * np.sin(2 * np.pi * 493.88 * dt) + 
                            0.25 * np.sin(2 * np.pi * 659.25 * dt)) * decay
            audio[start_idx:start_idx + chime_len] += chime
            
    # 4. Thunder and wind sweeps
    thunder_times = [4.5, 18.2, 27.0, 41.0, 52.0]
    for th in thunder_times:
        start_idx = int(th * sample_rate)
        th_len = int(2.5 * sample_rate)
        if start_idx + th_len < num_samples:
            dt = np.linspace(0, 2.5, th_len, endpoint=False)
            decay = np.exp(-dt * 1.5)
            th_sound = 0.4 * (np.random.rand(th_len) * 2 - 1) * decay * (1.0 + 0.5 * np.sin(2 * np.pi * 30 * dt))
            audio[start_idx:start_idx + th_len] += th_sound

    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = (audio / max_val) * 0.92
        
    int_audio = (audio * 32767).astype(np.int16)
    with wave.open(output_wav_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(int_audio.tobytes())
    print(f"[AUDIO DONE] Created {output_wav_path}")

def assemble_final_movie():
    print("[ASSEMBLY] Starting final 60s assembly with FFmpeg...")
    concat_list_path = os.path.join(WORK_DIR, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for s in SHOTS:
            video_name = f"shot_{s['id']:02d}.mp4"
            video_full_path = os.path.join(WORK_DIR, video_name).replace("\\", "/")
            if not os.path.exists(video_full_path):
                print(f"[ERROR] Missing video file: {video_full_path}")
                return None
            f.write(f"file '{video_full_path}'\n")
            
    # Generate soundtrack
    audio_wav_path = os.path.join(WORK_DIR, "four_beasts_epic_60s_bgm.wav")
    generate_60s_epic_soundtrack(audio_wav_path)
    
    final_mp4_path = os.path.join(WORK_DIR, "final_60s_four_beasts_3d.mp4")
    artifact_mp4_path = os.path.join(ARTIFACT_DIR, "final_60s_four_beasts_3d.mp4")
    artifact_wav_path = os.path.join(ARTIFACT_DIR, "four_beasts_epic_60s_bgm.wav")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list_path,
        "-i", audio_wav_path,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        final_mp4_path
    ]
    print(f"[EXEC] {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[SUCCESS] Final 60s 3D movie compiled: {final_mp4_path}")
        shutil.copyfile(final_mp4_path, artifact_mp4_path)
        shutil.copyfile(audio_wav_path, artifact_wav_path)
        print(f"[COPIED] Copied to artifact dir: {artifact_mp4_path}")
        return final_mp4_path
    else:
        print(f"[ERROR] FFmpeg failed:\n{res.stderr}")
        return None

def main():
    print("=" * 60)
    print(">>> 3D Photorealistic Short Video Pipeline: Monitoring & Assembly <<<")
    print("=" * 60)
    
    state = load_state()
    max_wait_seconds = 1800 # 30 mins
    start_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        all_completed = True
        summary_statuses = {}
        
        for shot in SHOTS:
            s_id = str(shot["id"])
            task_info = state["tasks"].get(s_id)
            if not task_info:
                print(f"[WARN] No task info for shot {s_id}")
                all_completed = False
                continue
                
            local_file = os.path.join(WORK_DIR, f"shot_{shot['id']:02d}.mp4")
            
            # If already downloaded and valid
            if os.path.exists(local_file) and os.path.getsize(local_file) > 100000:
                summary_statuses[s_id] = "Ready"
                task_info["status"] = "Succeed"
                task_info["local_file"] = local_file
                continue
                
            all_completed = False
            req_id = task_info.get("request_id")
            resp_data = check_task_status(req_id)
            
            if resp_data:
                cluster_status = resp_data.get("status")
                summary_statuses[s_id] = cluster_status
                
                if cluster_status == "Succeed":
                    results = resp_data.get("results") or {}
                    videos = results.get("videos") or []
                    if videos and len(videos) > 0 and videos[0].get("url"):
                        video_url = videos[0]["url"]
                        try:
                            ok = download_video(video_url, local_file)
                            if ok:
                                task_info["status"] = "Succeed"
                                task_info["video_url"] = video_url
                                task_info["local_file"] = local_file
                                save_state(state)
                                summary_statuses[s_id] = "Downloaded"
                        except Exception as dl_err:
                            print(f"[ERROR] Download failed for Shot {shot['id']:02d}: {dl_err}")
                    else:
                        print(f"[WARN] Succeed but no video url yet for Shot {shot['id']:02d}")
                elif cluster_status == "Failed":
                    print(f"[FAILED] Task failed for Shot {shot['id']:02d}: {resp_data}")
                    task_info["status"] = "Failed"
                    save_state(state)
            else:
                summary_statuses[s_id] = "NetErr"
                
        print(f"[STATUS CHECK @ {int(time.time() - start_time)}s] " + 
              ", ".join([f"S{k}:{v}" for k, v in summary_statuses.items()]))
        
        if all_completed:
            print("\n[ALL TASKS COMPLETE] All 12 shots successfully generated and downloaded!")
            break
            
        time.sleep(20)
        
    final_output = assemble_final_movie()
    if final_output:
        print("\n" + "=" * 60)
        print(f"[ALL DONE] 60-Second 3D Masterpiece Ready at: {final_output}")
        print("=" * 60)

if __name__ == "__main__":
    main()
