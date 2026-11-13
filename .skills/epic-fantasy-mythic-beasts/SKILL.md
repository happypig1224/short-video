---
name: epic-fantasy-mythic-beasts
description: 【风格05 · 史诗奇幻插画】细分场景指南：远古神兽与巨物奇观。专用于大鹏/鲲鹏展翅乘风、深海狂涛、九万里云霄、远古巨龙与神话巨兽等震撼视效呈现。
---

# 【风格05 · 史诗奇幻插画】远古神兽与巨物奇观指南 (Mythic Beasts Skill)

本指南针对**庄子《逍遥游》大鹏/鲲鹏化形、远古神话巨兽、遮天蔽日的翼兽与狂涛海啸奇观**。

核心命题：完美再现“**大鹏一日同风起，扶摇直上九万里**”的至高意境——水击三千里，其翼若垂天之云，绝云气，负青天。

---

## 核心美学特征与磅礴气势构建

### 1. 极致体量与构图张力（Monumental Scale）
* **大鹏翼展的“垂天之感”**：大鹏的双翼必须横跨整个画面视界（Wings spanning horizon to horizon），羽翼边缘翻滚着飓风与金色流光；羽毛肌理厚重如岩层，巨爪似钢钩，眼神凌厉威严。
* **动势方向（Dynamic Ascent）**：采用**仰角长焦或电影级超广角仰视镜头（Dramatic low-angle tracking shot）**，机位从波涛汹涌的幽暗海面斜刺向上，追随大鹏冲破雷暴、刺破九重云霄的螺旋上升动势。

### 2. 沧海、云海与风暴的立体气象
* **下方：北冥怒海**：幽深墨蓝的万丈狂涛、暴风巨浪（Roaring colossal ocean waves）、巨大的海水漩涡与飞溅的雪白浪花，展现“水击三千里”的力量感。
* **中层：狂风飓风（扶摇/Tornado Vortex）**：上升气流具象化为环绕大鹏身躯盘旋的螺旋风暴气柱，带起水汽与碎云。
* **上方：九万里天穹与破晓裂光**：大鹏头部已穿透厚重铅灰的暴雨雷云，刺入上方纯净耀眼的蔚蓝星穹；金色与天青色的**磅礴体积光（Colossal Volumetric Sunbeams）**如瀑布般从云层裂隙倾泻而下。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[神话大鹏巨兽形态与振翅动势]} + \text{[翻滚怒海与冲天飓风水汽]} + \text{[九重天霄裂云金光]} + \text{[尺度对比与气象透视]} + \text{[ArtStation 顶级奇幻概念画质]}$$

### 专用词库：
* **大鹏主体**：`colossal mythical Chinese giant bird Dapeng (Kunpeng), titanic majestic bird of legend, immense golden and obsidian feathered wings spanning across the entire sky, soaring straight up toward the heavens, piercing gaze, feathers like thunderclouds and dawn light`
* **海浪与风势**：`roaring dark abyssal ocean below, colossal turbulent tidal waves, towering waterspout vortex, sea spray and foam, ascending cyclone wind`
* **天空与云气**：`piercing through towering thunderheads into the upper stratosphere, breaking into the azure celestial sky, colossal volumetric god rays slicing through parting storm clouds, golden dawn light illuminating wingtips`
* **画风与质感**：`epic fantasy concept art, trending on ArtStation, cinematic matte painting, textured oil painting brushwork by Frank Frazetta and Greg Rutkowski, breathtaking monumental scale, IMAX composition`
* **负向排除词**：`small normal bird, peaceful flat lake, sunny cartoon, 2d anime flat color, blurry, deformed anatomy, modern airplanes`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> A breathtaking masterpiece of epic fantasy concept art capturing the ancient Chinese legend of the colossal mythical bird Dapeng (Kunpeng) ascending into the heavens: 'Soaring ninety thousand li straight up with the celestial wind'. The gargantuan beast, with majestic golden and dark sapphire feathered wings that span across the entire horizon, charges vertically straight up into the stratosphere. Below, a roaring, turbulent dark ocean churns with colossal storm waves and massive waterspouts. Above, the giant bird's head and wings shatter through dense, churning thunderclouds into brilliant golden celestial sunlight, casting monumental volumetric god rays across the sky. High contrast of abyssal sea blues, churning cloud shadows, and radiant golden light. Textured oil painting brushstrokes, breathtaking monumental scale, ArtStation trending quality, IMAX cinematic composition, no 3D cartoon CGI.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> Epic fantasy concept art of colossal mythical Chinese giant bird Kunpeng, soaring straight up through storm clouds into the heavens, immense wings spanning the sky, violent churning ocean below, golden volumetric god rays piercing the sky, dramatic low angle, ArtStation frontpage feature, Greg Rutkowski style, monumental scale --ar 16:9 --v 6.1 --stylize 400

### 3. Stable Diffusion / FLUX
* **Positive**: `(masterpiece, best quality:1.2), epic fantasy, colossal giant bird kunpeng, dapeng soaring into clouds, immense wings, stormy dark ocean waves, golden volumetric sunbeams, majestic scale, matte painting, artstation trending, dramatic lighting`
* **Negative**: `(worst quality:1.4), (low quality:1.4), small bird, cartoon, 2d flat, photorealistic human, modern city, blurry, deformed wings, bad anatomy`

