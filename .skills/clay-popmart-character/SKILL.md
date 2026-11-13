---
name: clay-popmart-character
description: 【风格02 · 3D黏土潮玩风】细分场景指南：角色档案与成套潮玩排版。专用于多角色成套盲盒手办企划、角色图鉴档案（Character Sheet）、海报包装视觉、多视角三视图与商业 IP 宣发排版设计。
---

# 【风格02 · 3D黏土潮玩风】角色档案与成套排版指南 (Clay Character Sheet Skill)

本指南针对商业级**潮玩 IP 成套盲盒发布、角色档案图鉴（Character Sheet）与商业海报排版**。

核心痛点：普通生图常常只生成单个人物，角色之间比例不一、风格割裂、缺乏世界观故事感与统一的视觉排版体系。本指南通过**统一视觉排版底座、角色序列对比、档案信息区划分**三大商业标准，实现高价值感的成套输出。

---

## 核心商业排版特征与视觉系统

### 1. 成套潮玩（Blind Box Series）的“秩序感”法则
* **统一地台与比例基准**：系列内每个 Q 版角色必须站在高度统一的**圆盘底座（Circular Display Base）**或**一体化黏土展示微景观**上，头身比恒定在 2.0-2.5 头身之间。
* **视线与动态呼应**：多角色同屏时，主次分明——中央角色正视前方充当 C 位锚点，两侧角色略微倾斜朝向中央或互动，形成叙事小剧场（Narrative Storytelling）。
* **标志性服饰色差（Color Coding）**：每个角色拥有专属的主题代表色（如墨绿侠客、朱红小仙、湖蓝文生、暖黄萌宠），保证同屏时视觉辨识度极高。

### 2. 角色档案海报（Character Sheet & Poster）的布局范式
* **上方/背景层**：通透干净的纯色渐变或微缩世界观浅景深虚化背景。
* **中层主体**：成套角色高精度 3D 手办模型，一字排开或错落站立于展示台。
* **下方/边框层**：留出工整的商业手办排版框（Product Info Cards），模拟官方盲盒角色名牌与图鉴档案。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[全套角色系列阵容]} + \text{[角色个性分工与外观]} + \text{[统一排版底座与海报构图]} + \text{[3D 黏土软陶材质]} + \text{[专业影棚产品级布光]}$$

### 专用词库：
* **排版与阵容构图**：`complete character sheet poster lineup, a full series set of 4 cute chibi blind box figures, standing side by side on matching circular display pedestals, unified visual typography layout, collectible designer art toy series`
* **角色区分设定**：`each character with unique outfits and props: one explorer with a compass, one guardian with a wooden staff, one scholar with a scroll, one companion pet`
* **材质与工艺**：`Pop Mart toy aesthetic, sculpted from matte polymer clay, subtle handmade clay indentations, glossy enamel eyes, clean solid seams, C4D Octane render`
* **灯光与摄影**：`professional studio product photography, dual softbox lighting, clean studio backdrop, crisp focal depth, 8k resolution commercial poster layout`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> A high-end commercial character sheet poster showcasing a full series set of 4 cute chibi collectible blind box figures, in the style of Pop Mart and 3D claymation. The 4 characters stand side by side on matching circular clay display pedestals against a clean, aesthetic studio backdrop. Each character has round chubby cheeks and big glossy eyes, sculpted from soft matte polymer clay with subtle handmade thumbprints. Each wears a distinct colorful outfit with charming unique accessories. The overall layout is clean, balanced, and professional, resembling an official collectible toy lineup poster and character profile archive. C4D Octane render, studio softbox lighting, crisp depth of field, premium designer toy collection.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> Complete blind box character lineup poster, 4 cute chibi figures standing on matching display bases, Pop Mart style, 3D polymer clay texture, subtle handmade marks, matte finish, soft studio lighting, clean background, unified visual design, commercial art toy catalog --ar 16:9 --v 6.0 --style raw

### 3. Stable Diffusion / FLUX
* **Positive**: `(masterpiece, best quality:1.2), pop mart character sheet, 4 chibi figures, line up, matching pedestals, 3d clay, polymer clay, matte texture, clean studio background, octane render, c4d, toy catalog poster`
* **Negative**: `(worst quality:1.4), (low quality:1.4), 2d flat, photorealistic human skin, messy random clutter, mismatched styles, distorted faces, blurry, extra limbs`

---

## 即拷即用实战预设

### 预设 1：探险小队全员档案海报（Expedition Team Profile Poster）
```text
A commercial art toy lineup poster featuring 4 cute chibi explorer figures in Pop Mart blind box style.
Layout: 4 figures arranged symmetrically on matching terracotta-colored circular display bases across a wide horizontal canvas.
Character 1: Brave leader holding a tiny brass compass and rolled map.
Character 2: Agile scout carrying a miniature wooden telescope.
Character 3: Gentle herbalist with a bamboo basket filled with clay herbs.
Character 4: Chubby mythical creature companion resting playfully on the ground.
Style: Soft matte polymer clay texture with delicate handmade touches, high-gloss eyes, Octane render, soft studio product lighting.
```

### 预设 2：盲盒隐藏款单体档案卡（Secret Chibi Figure Profile Card）
```text
A premium designer toy character profile showcase featuring a rare secret blind box figure.
The cute chibi figure stands proudly on an ornate translucent jade-like display base with gold foil accents.
Front view, slight 3/4 turn, soft studio rim lighting highlighting the velvety matte clay texture.
Commercial collectible toy packaging visual.
```
