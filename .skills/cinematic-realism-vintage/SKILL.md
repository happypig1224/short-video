---
name: cinematic-realism-vintage
description: 【风格03 · 电影感超写实人像】细分场景指南：年代纪实与历史群像。专用于 70-80 年代中国农村/城镇家庭合影、老照片胶片感、历史人物纪实与集体时代肖像，解决年代感失真与假面塑料皮问题。
---

# 【风格03 · 电影感超写实人像】年代纪实与历史群像指南 (Vintage Realism Skill)

本指南针对 **1970-1980 年代真实生活纪实、乡土农村家庭全家福合影与历史时代群像**。

核心痛点：AI 容易把 70 年代的人画得像穿现代古装的偶像明星（过度白皙、现代发型、妆容假面），或者将老照片粗暴添加生硬的黄色杂色。本指南通过**时代服饰细节、自然风霜面容与复古 35mm 胶片感**三大支柱实现真正震撼的历史真实感。

---

## 核心美学特征与年代真实度法则

### 1. 时代服饰与道具的严谨复原（1970s 中国农村范本）
* **衣物面料与剪裁**：
  * 拒绝光滑丝绸与现代紧身剪裁。采用**纯棉老粗布（Coarse cotton fabric）、藏青与灰蓝色土布棉袄、耐磨斜纹布中山装、碎花土布小衫**。
  * 衣物必须带有真实的**穿着折痕、手肘与袖口磨损起毛痕迹、布纽扣与针脚细节**。
* **发型与饰品**：
  * 男士：平头或质朴短分头，戴蓝绿军便帽或羊肚白毛巾。
  * 女士：齐耳短发两边别黑色小发夹，或双麻花辫，无染烫痕迹。
* **环境道具**：泥砖夯土墙（Mud-brick wall）、红柳木长条凳、门梁上晾晒的金黄玉米棒、粗陶水缸、搪瓷茶缸。

### 2. 生理特征的“岁月与风霜感”
* **皮肤质感**：长期农耕劳作形成的**健康小麦色/红铜色晒伤（Sun-kissed tanned skin）**、眼角清晰深刻的笑纹与风霜鱼尾纹（Crow's feet）、粗糙有茧的骨节分明双手。
* **神态还原**：质朴、腼腆而真挚的笑容，面向老式相机的微微拘谨与一家人依偎在一起的血脉温情。

### 3. 35mm 胶片光学质感
* **胶片色彩**：柯达（Kodak Portra / Kodachrome）或海鸥/公元老胶片色调，微微褪色的红蓝纯度，暗部泛冷灰，高光柔和泛乳黄。
* **颗粒与缺陷**：微细银盐胶片颗粒（Fine analog film grain）、轻微的暗角（Subtle vignetting）与轻微镜头眩光，杜绝数码高锐度死白。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[年代背景与家庭群像构成]} + \text{[服饰风霜与肢体互动]} + \text{[泥砖土房与乡土环境]} + \text{[35mm 胶片机与胶卷规格]} + \text{[自然漫射日光与真实肤质]}$$

### 专用词库：
* **年代与人物设定**：`authentic vintage 1970s Chinese rural family portrait, a family of six: elderly grandparents, loving parents, and two young children posing together`
* **服饰与神态**：`wearing modest vintage 1970s navy and dark blue quilted cotton padded jackets, simple cloth shoes, genuine warm candid smiles, shy looking at the camera, authentic weathered skin texture, sun-tanned faces with natural crow's feet and wrinkles`
* **环境与道具**：`standing in front of a rustic mud-brick farmhouse courtyard, wooden door, dried corn cobs hanging from eaves, clay ground, nostalgic rural village setting`
* **光学与胶卷**：`shot on 35mm lens, vintage analog film photography, Kodak Portra 400 color grading, fine film grain, soft natural overcast daylight, desaturated earth tones, archival historical documentary photography, candid documentary style`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> An authentic, deeply moving vintage 1970s family portrait of a Chinese rural family of six, standing proudly outside their rustic mud-brick courtyard home. The family spans three generations: wrinkled, sun-weathered grandparents with kind laughing eyes; hardworking parents with tanned, honest faces; and two curious young children wrapped in warm quilted cotton jackets with patched knees. They wear authentic period-accurate modest 1970s blue and grey Mao suits and coarse cotton clothing. In the background, golden dried corn cobs hang under the thatched eaves of the clay farmhouse. Shot on vintage 35mm film, Kodak Portra 400 aesthetic, organic film grain, natural overcast ambient daylight, authentic skin micro-textures with visible pores and wrinkles, warm nostalgic color tones, historical documentary archive quality, no smooth plastic skin, no CGI rendering.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> Authentic 1970s Chinese rural family portrait of six, mud-brick farmhouse courtyard, vintage padded cotton jackets, genuine candid expressions, shot on 35mm film, Kodak Portra 400, fine analog film grain, natural skin imperfections, weathered textures, overcast daylight, historical documentary style --ar 16:9 --style raw --v 6.0

### 3. Stable Diffusion / FLUX
* **Positive**: `(masterpiece, best quality:1.2), vintage 1970s photo, chinese rural family of six, mud brick house, cotton padded jackets, genuine smiles, wrinkled skin, weathered hands, shot on 35mm film, kodak portra, fine grain, documentary photography`
* **Negative**: `(worst quality:1.4), (low quality:1.4), 3d render, cgi, modern clothes, makeup, plastic smooth skin, airbrushed, oversaturated colors, blur, cartoon`

---

## 即拷即用实战预设

### 预设 1：七十年代北方农家全家福（1970s Northern Countryside Family）
```text
A documentary vintage 1970s black-and-white family portrait of a rural Chinese peasant family of six.
Posed on wooden benches in a sandy courtyard against a rammed-earth mud wall.
Grandmother wearing a simple headscarf, grandfather smoking a long wooden pipe, parents with sturdy posture, two children holding wooden toys.
Heavy silver gelatin film grain, high dynamic range, authentic candid historical photography.
```

### 预设 2：丰收时节的老院暖阳（Harvest Season Nostalgia）
```text
A warm color vintage 1970s photograph of a rural family resting after harvest.
Soft afternoon sunlight filtering through courtyard trees, illuminating dusty air and golden straw stacks.
Authentic coarse cloth clothing, genuine weathered smiles, visible laugh lines and honest eyes.
Shot on 35mm analog film, vintage warmth, soft vignette.
```

