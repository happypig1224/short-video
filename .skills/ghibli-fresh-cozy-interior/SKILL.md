---
name: ghibli-fresh-cozy-interior
description: 【风格01 · 吉卜力日系清新风】细分场景指南：温馨室内与治愈美食。专用于《魔女宅急便》面包房、《哈尔的移动城堡》杂乱厨房与厚切培根蛋、《借物少女艾莉缇》微缩木屋与日常静物，解决室内变冷淡现代样板间或食物发塑料感的问题。
---

# 【风格01 · 吉卜力日系清新风】温馨室内与治愈美食指南 (Ghibli Cozy Interior & Food Skill)

本指南针对吉卜力动画中最具烟火气与治愈感的**温馨杂乱木屋、手作生活杂货与“吉卜力美食”**（代表作：《魔女宅急便》的面包房、《哈尔的移动城堡》的厨房与煎培根蛋、《借物少女艾莉缇》的花草房间、《千与千寻》吃饭团落泪）。

核心痛点：AI 容易把室内画成冷冰冰的现代简约样板间，或者把食物渲染成油腻无生气的塑料模型。本指南通过**暖光生活杂物、木质温度与食物动态热汽**三大法则进行精准控制。

---

## 核心美学特征与细节法则

### 1. 吉卜力美食（Ghibli Food）的“欲望感”秘诀
* **动态热度表现**：必须带上**升腾的白色半透明热汽（Rising Wisps of Warm Steam）**、铁锅边缘滋滋作响的气泡油花（Sizzling Oil Bubbles）。
* **色彩诱人度**：金黄微焦的太阳蛋边缘（Crispy Golden Edges）、流心蛋黄的柔和高光、厚切培根的油润粉红、刚出炉面包的粗糙麦香外壳。
* **餐具器皿**：黑铁铸铁锅（Cast-Iron Skillet）、厚胎白瓷碗、深色原木餐桌、手捏陶罐。

### 2. 室内空间的“杂乱生活感”（Cluttered Warmth）
* **禁止空旷与极简**：吉卜力的房间充满生活痕迹——垂挂在天花板的风干香草、架子上整齐摆放的彩色玻璃果酱罐、随意搭在椅背的毛线开衫、泛黄的书本与手写配方单。
* **专属色盘与布光**：
  * **主色调**：蜜蜡暖黄（Warm Amber）、胡桃木色（Walnut Wood）、米白亚麻、墨绿天鹅绒。
  * **光源**：温暖的钨丝吊灯、透过方格木窗洒下的斜阳，光柱中漂浮着细小的微尘光斑（Dancing Dust Motes）。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[美食特写/室内场景]} + \text{[原木器皿与杂乱杂物]} + \text{[暖阳斜射与升腾热汽]} + \text{[宫崎骏生活手绘动画风]} + \text{[质朴温馨氛围]}$$

### 专用词库：
* **吉卜力美食词**：`delicious Ghibli anime feast on a wooden table, thick-cut sizzling bacon and golden sunny-side-up eggs in a black cast-iron pan, steaming bowl of vegetable stew, crusty rustic bread loaf, melting butter`
* **室内器皿与杂物**：`cozy cluttered rustic wooden cottage kitchen, copper pots hanging from exposed beams, glass spice jars with colorful herbs, vintage ceramic tea kettle, lace curtains`
* **光影与空气**：`warm golden sunlight streaming through a small wooden mullioned window, visible dancing dust motes in sunbeams, gentle translucent steam rising, cozy domestic atmosphere`
* **材质与画风**：`Studio Ghibli aesthetic, hand-drawn traditional 2D animation, soft watercolor painting textures, warm pastel palette, slice-of-life charm`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> A mouth-watering, heartwarming anime scene in the authentic aesthetic of Studio Ghibli, inspired by the cozy kitchen in Howl's Moving Castle. On a heavy, warm rustic wooden dining table sits a hearty breakfast: a sizzling black cast-iron skillet filled with thick slices of sizzling bacon and two perfect sunny-side-up eggs with glossy golden yolks. A loaf of warm crusty country bread and a steaming ceramic mug of hot tea sit nearby. Delicate plumes of warm steam curl into the air. In the background, copper saucepans hang from dark wooden ceiling beams, and glass jars of herbs line the shelves. Warm golden morning sunlight streams through a small window, casting a cozy glow across the room. Hand-drawn 2D animation, watercolor and gouache textures, comforting and nostalgic, no 3D CGI, no plastic sheen.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> Cozy rustic anime kitchen interior, Studio Ghibli food style, wooden table laden with a steaming skillet of sizzling bacon and sunny-side-up eggs, rustic crusty bread, hanging copper cookware, warm golden hour light pouring through window panes, soft dust motes, hand-painted anime background, watercolor textures --ar 16:9 --niji 6 --style raw

### 3. Stable Diffusion / FLUX
* **Positive**: `(masterpiece, best quality:1.2), studio ghibli food, anime interior, cozy wooden kitchen, sizzling bacon and eggs in cast iron skillet, steaming hot food, rustic bread, hanging pots, warm amber lighting, sunbeam through window, hand-drawn cel style, soft gouache textures`
* **Negative**: `(worst quality:1.4), (low quality:1.4), 3d render, photorealistic, modern minimal apartment, cold lighting, plastic food, neon colors, messy distortion`

---

## 即拷即用实战预设

### 预设 1：哈尔式治愈早餐（Howl's Hearty Breakfast）
```text
A close-up of a delicious, steaming breakfast in a cozy cottage, authentic Studio Ghibli aesthetic.
In the center: a seasoned cast-iron pan holding thick sizzling bacon strips and two sunny-side-up eggs with glowing yellow yolks.
Beside it: freshly sliced rustic artisan bread with melting butter, and a steaming mug of hot milk tea.
Warm, gentle sunlight illuminating the rising vapor, soft wooden textures, cozy domestic slice-of-life mood.
Hand-drawn 2D cel animation, painterly gouache details, rich warm colors.
```

### 预设 2：琪琪的暖阳面包房（Kiki's Warm Sunlit Bakery）
```text
Inside a charming vintage European anime bakery, inspired by Kiki's Delivery Service.
Wooden counter filled with golden-brown braided breads, round baguettes, croissants, and fruit tarts on wicker trays.
Sunlight pouring through a large shop window onto tiled floors, a vase of fresh daisies on the counter.
Warm, inviting, nostalgic atmosphere filled with the scent of baked goods.
Studio Ghibli background art, soft watercolor wash, delicate line art.
```
