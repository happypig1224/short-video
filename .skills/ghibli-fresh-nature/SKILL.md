---
name: ghibli-fresh-nature
description: 【风格01 · 吉卜力日系清新风】细分场景指南：自然田园与夏日风光。专用于《龙猫》《岁月的童话》《幽灵公主》等夏日水稻田、里山乡村、巨型积雨云与男鹿和雄式深绿森林场景。
---

# 【风格01 · 吉卜力日系清新风】自然田园与夏日风光指南 (Ghibli Nature Skill)

本指南针对吉卜力动画中最经典的**盛夏田野、里山乡村（Satoyama）、幽深古树与森林秘境**（代表作：《龙猫》《岁月的童话》《侧耳倾听》《幽灵公主》的白日森林）。

核心优势：通过**男鹿和雄（Kazuo Oga）不透明水粉背景**与**山本二三（Nizo Yamamoto）积雨云**的艺术法则，还原最纯净的日系手绘自然美学。

---

## 核心美学特征与色彩法则

### 1. 专属自然色盘
* **植被与田野**：禁用荧光绿。采用**草绿（Sap Green）、翡翠绿（Viridian）、橄榄绿（Olive Green）**与嫩芽浅黄的渐变层叠。
* **盛夏天空**：**天青蓝（Cerulean Blue）、深钴蓝（Cobalt Blue）**配合奶白色巨型积雨云。
* **光影**：**暖金阳光与木漏れ日（Komorebi，树叶缝隙漏下的斑驳微光）**。

### 2. 空间与材质要点
* **风的实体化**：通过草浪倾斜、稻禾起伏、发丝与白衬衫后扬，将看不见的夏风具象化。
* **水粉厚涂肌理（Gouache Texture）**：保留手绘水粉的干笔触与冷压水彩纸纹理，彻底剥离 AI 的光滑塑料质感。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[少年/少女与自然互动]} + \text{[稻田/里山/森林环境]} + \text{[男鹿和雄水粉背景锚点]} + \text{[积雨云与木漏れ日光影]} + \text{[手绘赛璐璐质感]}$$

### 专用词库：
* **自然景致**：`endless vibrant green rice paddy fields, rural Japanese countryside path, mossy ancient camphor tree, winding clear stream, distant rolling mountains in summer haze`
* **天空与气候**：`towering fluffy white cumulus clouds (入道云), brilliant cerulean blue sky, warm radiant summer sunlight, gentle breeze rustling crops, dappled sunbeams (komorebi)`
* **角色动态**：`a young boy in a white short-sleeve shirt and straw hat walking along the irrigation canal, looking into the vast distance`
* **大师风格与材质**：`Studio Ghibli aesthetic, Kazuo Oga background art, hand-drawn traditional 2D animation, cel shading, rich gouache painting texture, rough paper grain`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> A breathtaking anime landscape in the authentic aesthetic of Studio Ghibli and Kazuo Oga background art. A young Japanese boy with untamed dark hair, wearing a loose white linen short-sleeve shirt and dark shorts with a straw hat hanging on his back, stands peacefully on a narrow earthen path between vast emerald-green rice paddies. The summer breeze creates rolling waves across the rice fields. In the background, colossal fluffy white cumulus clouds rise into an expansive cerulean blue sky. A tiny wooden irrigation sluice and wild yellow wildflowers line the path. Traditional 2D hand-drawn cel animation, rich gouache background texture, warm golden afternoon sunlight, evocative childhood nostalgia, no 3D CGI, no plastic rendering.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> A peaceful Japanese countryside landscape, lush green rice fields, Kazuo Oga background art style, Studio Ghibli aesthetic, towering cumulus clouds, boy in summer clothes by the dirt path, gouache painting texture, soft natural lighting, nostalgic warm glow --ar 16:9 --style raw --v 6.0

### 3. Stable Diffusion / FLUX
* **Positive**: `(masterpiece, best quality:1.2), studio ghibli aesthetic, kazuo oga background, 1boy, straw hat, white shirt, lush rice fields, wind rustling grass, towering clouds, deep blue sky, gouache texture, cel shading, hand-drawn, nostalgic warm lighting`
* **Negative**: `(worst quality:1.4), (low quality:1.4), 3d, cgi, photorealistic, greasy shiny skin, modern city buildings, extra limbs, blur`
