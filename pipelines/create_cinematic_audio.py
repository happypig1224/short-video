import numpy as np
import wave
import subprocess
from pathlib import Path

def generate_wuxia_cinematic_audio(output_wav: Path, duration=15.0, sr=44100):
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    left = np.zeros_like(t)
    right = np.zeros_like(t)

    # 1. 基础深邃低频与风声氛围 (Atmospheric Sub-bass & Wind)
    wind_noise = np.random.normal(0, 0.05, len(t))
    # 模拟山谷微风
    wind_env = (np.sin(2 * np.pi * 0.2 * t) * 0.5 + 0.5) ** 2
    left += wind_noise * wind_env * 0.3
    right += wind_noise * (1 - wind_env) * 0.3

    # 2. 战鼓打击点 (Cinematic War Drums)
    drum_times = [0.2, 2.5, 5.0, 6.2, 7.5, 8.8, 10.0, 11.2, 12.5, 13.5]
    for dt in drum_times:
        idx = int(dt * sr)
        drum_len = int(0.8 * sr)
        if idx + drum_len > len(t):
            drum_len = len(t) - idx
        dt_arr = np.linspace(0, 0.8, drum_len, endpoint=False)
        # 45Hz -> 25Hz 频坠
        pitch = 45 * np.exp(-4 * dt_arr)
        drum_wave = np.sin(2 * np.pi * pitch * dt_arr) * np.exp(-5 * dt_arr)
        left[idx:idx+drum_len] += drum_wave * 0.7
        right[idx:idx+drum_len] += drum_wave * 0.7

    # 3. 刀光剑影清脆剑鸣 (Metallic Sword Ring / Unsheathing)
    sword_times = [0.8, 5.2, 7.8, 10.3]
    for st in sword_times:
        idx = int(st * sr)
        ring_len = int(2.0 * sr)
        if idx + ring_len > len(t):
            ring_len = len(t) - idx
        st_arr = np.linspace(0, 2.0, ring_len, endpoint=False)
        # 金属基频 2400Hz + 泛音 4800Hz + 7200Hz
        metal_ring = (
            np.sin(2 * np.pi * 2420 * st_arr) * 0.6 +
            np.sin(2 * np.pi * 4840 * st_arr) * 0.3 +
            np.sin(2 * np.pi * 7260 * st_arr) * 0.15
        ) * np.exp(-3.5 * st_arr)
        # 破风啸叫 (Whoosh)
        whoosh = np.random.normal(0, 0.2, ring_len) * np.exp(-15 * st_arr)
        left[idx:idx+ring_len] += (metal_ring * 0.5 + whoosh * 0.4)
        right[idx:idx+ring_len] += (metal_ring * 0.5 + whoosh * 0.4)

    # 4. 国风五音古筝/琵琶意境 (Pentatonic Guzheng Plucks: D-F-G-A-C)
    notes = [
        (0.5, 293.66),   # D4
        (1.2, 349.23),   # F4
        (2.0, 392.00),   # G4
        (3.0, 440.00),   # A4
        (4.0, 523.25),   # C5
        (5.5, 587.33),   # D5 (高潮开始)
        (6.0, 698.46),   # F5
        (7.0, 783.99),   # G5
        (8.2, 880.00),   # A5
        (9.5, 1046.50),  # C6 (剑气冲霄)
        (10.5, 587.33),  # D5
        (11.5, 440.00),  # A4
        (12.5, 392.00),  # G4
        (13.8, 293.66),  # D4 (余韵悠长)
    ]
    for nt, freq in notes:
        idx = int(nt * sr)
        pluck_len = int(1.8 * sr)
        if idx + pluck_len > len(t):
            pluck_len = len(t) - idx
        p_arr = np.linspace(0, 1.8, pluck_len, endpoint=False)
        # 古筝泛音
        pluck = (
            np.sin(2 * np.pi * freq * p_arr) * 0.5 +
            np.sin(2 * np.pi * freq * 2 * p_arr) * 0.25 +
            np.sin(2 * np.pi * freq * 3 * p_arr) * 0.12
        ) * np.exp(-2.2 * p_arr)
        left[idx:idx+pluck_len] += pluck * 0.45
        right[idx:idx+pluck_len] += pluck * 0.45

    # 5. 音量淡入淡出与限幅归一化
    fade_in = np.minimum(1.0, np.linspace(0, 1, int(sr * 0.3)))
    fade_out = np.minimum(1.0, np.linspace(1, 0, int(sr * 1.0)))
    left[:len(fade_in)] *= fade_in
    right[:len(fade_in)] *= fade_in
    left[-len(fade_out):] *= fade_out
    right[-len(fade_out):] *= fade_out

    # 归一化到 [-0.9, 0.9]
    max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-6)
    left = (left / max_val * 0.88 * 32767).astype(np.int16)
    right = (right / max_val * 0.88 * 32767).astype(np.int16)

    # 写入立体声 WAV
    stereo = np.empty((len(t) * 2,), dtype=np.int16)
    stereo[0::2] = left
    stereo[1::2] = right

    with wave.open(str(output_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(stereo.tobytes())

    print("Generated Wuxia Cinematic Audio:", output_wav)

output_wav = Path("c:/Users/33046/Desktop/short video/libai_v2_output/wuxia_cinematic_bgm.wav")
generate_wuxia_cinematic_audio(output_wav)

