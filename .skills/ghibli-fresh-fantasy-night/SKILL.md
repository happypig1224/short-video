---
name: ghibli-fresh-fantasy-night
description: 【风格01 · 吉卜力日系清新风】细分场景指南：奇幻夜景与神怪祭典。专用于《千与千寻》式水上油屋、红灯笼暮色、水上列车、幽灵神怪与魔法湖畔场景，解决夜景发黑或误变赛博朋克的问题。
---

# 【风格01 · 吉卜力日系清新风】奇幻暮夜与神怪祭典指南 (Ghibli Fantasy Night Skill)

本指南针对吉卜力日系清新美学中的**奇幻夜景、神明祭典与神秘水上世界**（代表作：《千与千寻》《哈尔的移动城堡》星空湖畔、《幽灵公主》荧光山神）。

针对普遍痛点：AI 画夜景容易把画面画得死黑一片，或者受霓虹词干扰跑成赛博朋克风。本指南提炼出专门的**深靛蓝暮色与纸灯笼暖光对撞法则**。

---

## 核心美学特征与色彩法则

### 1. 专属色盘系统
* **暗部与夜空**：禁止使用压抑的纯黑（#000000）。采用**深靛蓝（Indigo）、钴蓝（Cobalt Blue）与夜幕青紫（Midnight Violet）**。
* **暖光源与反光**：**琥珀黄（Amber Gold）、朱砂红（Cinnabar Red）、蜜糖暖橙**，模拟古旧纸灯笼内部透出的烛光。
* **奇幻发光体**：薄荷微青（Mint Glow）、幽灵白蓝（Ghostly Pale Blue）、水面碎金反光。

### 2. 空间与材质要点
* **水面反射**：吉卜力夜景几乎离不开水——水上铁轨、水漫神龛、温泉水汽。水面承担了二次折射暖光的作用，有效提亮画面下半部分。
* **多层木构建筑**：层叠的飞檐、朱红色的回廊、木制桥梁，在暗处保留深褐色木纹肌理，而非涂抹一团黑。
* **烟气与水雾**：温热的温泉白雾在空气中翻滚，让夜景产生深邃的空气透视（Atmospheric Depth）。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[主体/神怪/人物]} + \text{[传统木构水景环境]} + \text{[红灯笼与水雾光源]} + \text{[吉卜力手绘水彩/水粉质感]} + \text{[深靛蓝夜空与水面反光]}$$

### 专用词库：
* **环境与建筑**：`grand multi-tiered traditional wooden bathhouse over water, red wooden bridge, Japanese torii gate submerged in a calm sea, narrow old marketplace street`
* **光源控制**：`hundreds of glowing red paper lanterns, warm amber lantern glow, gentle steam rising from hot springs, golden light reflections on rippling dark water`
* **氛围与天空**：`mystical twilight, deep indigo night sky, starry celestial sky, hazy misty atmosphere, enchanting and nostalgic mood`
* **角色与神怪**：`shadowy spirit creatures, friendly masked yokai, a solitary girl looking back on the wooden bridge, mysterious wandering shadows`
* **材质与媒介**：`Studio Ghibli style, hand-drawn 2D anime aesthetic, rich gouache background painting, watercolor textures, soft painterly brushstrokes`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> A magical nighttime anime scene in the authentic aesthetic of Studio Ghibli, inspired by Spirited Away. A majestic multi-tiered traditional Japanese bathhouse standing above a calm, glassy lake under a deep indigo twilight sky. Hundreds of warm red and golden paper lanterns illuminate the wooden balconies, casting vibrant amber reflections across the rippling water. Gentle white steam rises into the night air. On a red wooden bridge leading to the entrance, a few mysterious, friendly spirit silhouettes wander peacefully. Traditional 2D hand-drawn cel animation, rich gouache painting texture, nostalgic and enchanting atmosphere, no harsh digital glare, no 3D CGI.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> A traditional Japanese bathhouse at night, Spirited Away aesthetic, Studio Ghibli style, multi-story wooden architecture over a dark glassy river, glowing red and golden paper lanterns, rising hot spring steam, indigo twilight sky, jewel-toned color palette, hand-drawn anime background, rich watercolor texture --ar 16:9 --niji 6 --style raw

### 3. Stable Diffusion / FLUX
* **Positive**: `(masterpiece, best quality:1.2), studio ghibli style, spirited away aesthetic, traditional wooden bathhouse at night, hundreds of glowing red paper lanterns, warm amber light reflection on water, deep indigo sky, steam, watercolor texture, cel shading, hand-drawn`
* **Negative**: `(worst quality:1.4), (low quality:1.4), 3d, cgi, photorealistic, modern neon lights, cyberpunk, harsh contrast, pitch black darkness, oversaturated purple`

---

## 即拷即用实战预设

### 预设 1：水上列车与暮色星海（Water Train at Twilight）
```text
A nostalgic retro red train traveling on train tracks submerged in a shallow, calm ocean, inspired by Studio Ghibli's Spirited Away.
Twilight sky gradient from golden sunset orange to deep indigo blue, filled with early evening stars.
Inside the train, soft warm interior lighting reveals shadows of quiet passengers.
Water gently ripples against the rails with glowing reflections, peaceful, melancholic and dreamy atmosphere.
Hand-drawn 2D cel animation, gouache background texture, watercolor wash.
```

### 预设 2：灯火通明的神隐夜市（Night Market of the Spirits）
```text
A bustling old wooden food stall street at dusk, warm steam billowing from steaming bamboo steamers and hot broth pots.
Strings of red and yellow lanterns illuminate old wooden storefronts and hand-painted signs.
Friendly, mysterious masked spirit patrons walking down cobblestone steps.
Studio Ghibli aesthetic, Hayao Miyazaki concept art, rich warm color grading, painterly background details.
```
