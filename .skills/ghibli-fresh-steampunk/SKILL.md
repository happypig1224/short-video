---
name: ghibli-fresh-steampunk
description: 【风格01 · 吉卜力日系清新风】细分场景指南：复古机械与蒸汽朋克。专用于《天空之城》《哈尔的移动城堡》《红猪》《风之谷》等空想航空器、飞艇机械、发条齿轮与云上浮岛场景，解决 AI 机械过于现代化或变冷酷机甲的问题。
---

# 【风格01 · 吉卜力日系清新风】复古机械与蒸汽朋克指南 (Ghibli Steampunk Skill)

本指南针对宫崎骏动画中标志性的**复古空想机械、蒸汽飞艇、工业采矿小镇与云海浮岛**（代表作：《天空之城》《哈尔的移动城堡》《红猪》《风之谷》《起风了》）。

核心痛点：AI 在遇到机械类词汇时，极易画出过于现代、光滑流线型的高科技机甲或赛博朋克金属。本指南通过锁定**19世纪末手绘工程图、黄铜铆钉与铸铁手作质感**，确保浓厚的吉卜力工业美学。

---

## 核心美学特征与材质法则

### 1. 机械构造的“手作感”与“笨重温度”
* **材质与工艺**：以**黄铜（Brass）、熟铁（Wrought Iron）、紫铜铆钉（Copper Rivets）、原木甲板（Wooden Deck）**为主，表面带有轻微的机油光泽和金属磨损痕迹。
* **动力展现**：必须有真实的物理逻辑表达——锅炉排出的白色膨胀蒸汽（Puffs of Boiler Steam）、旋转的木质双翼螺旋桨、外露的联动齿轮与传动皮带。
* **造型哲学**：圆润、憨厚、微胖的空想机械轮廓（如蜻蜓扑翼机、多铆钉飞艇、拼接式城堡），反对冷酷锐利的现代棱角。

### 2. 专属色盘系统
* **金属与工业**：黄铜浅金（Brushed Brass）、深古铜（Antique Bronze）、生铁灰褐、机油蓝黑。
* **自然与天空对比**：广袤的蔚蓝天空与纯白积雨云，与下方的金属机械形成鲜明的**冷暖反差**。
* **配景大地**：红陶砖瓦（Terracotta Tiles）、青石矿山、爬满常春藤的生锈废墟。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[空想机械/飞艇/城堡]} + \text{[黄铜与铆钉细节]} + \text{[云海/采矿镇工业环境]} + \text{[蒸汽与飞行动态]} + \text{[宫崎骏手绘概念设计]}$$

### 专用词库：
* **飞行器与机械**：`vintage steampunk airship, retro biplane with wooden propellers, whimsical flying machine with flapping insect wings, clumsy walking mechanical castle`
* **机械工艺词**：`exposed brass gears and bronze pipes, heavy iron rivets, worn metal plates, visible mechanical linkages, billowing puffs of white steam`
* **环境与空域**：`sailing above an endless sea of clouds, towering white cumulus clouds, rocky canyon mining town, ancient overgrown floating ruins`
* **人物呼应**：`a young adventurer boy wearing vintage aviator goggles and leather suspenders standing on the wooden observation deck, wind blowing his scarf`
* **风格与介质**：`Hayao Miyazaki concept art, Studio Ghibli mechanical aesthetic, traditional 2D hand-drawn cel animation, rich watercolor texture, warm nostalgic lighting`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> A breathtaking retro anime scene in the distinct mechanical aesthetic of Studio Ghibli and Hayao Miyazaki, inspired by Laputa: Castle in the Sky. A large, whimsical steampunk airship with wooden observation decks, spinning brass propellers, and visible copper rivets sails gracefully above a magnificent sea of clouds. Plumes of white steam billow from small copper exhaust pipes. A young adventurous boy wearing vintage pilot goggles and a brown vest stands at the bow, looking at a distant floating island surrounded by golden sunlight. Traditional 2D hand-drawn animation style, gouache background art, warm nostalgic color palette, no 3D CGI, no slick modern sci-fi materials.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> Vintage steampunk airship sailing through towering cumulus clouds, Laputa Castle in the Sky style, Studio Ghibli concept art, intricate brass gears, exposed copper pipes, billowing steam, warm sunset lighting, hand-painted anime background, watercolor texture --ar 16:9 --stylize 250 --niji 6 --style raw

### 3. Stable Diffusion / FLUX
* **Positive**: `(masterpiece, best quality:1.2), studio ghibli style, hayao miyazaki mecha, vintage steampunk airship, brass rivets, gears, wooden deck, billows of steam, sea of clouds, blue sky, hand-drawn, 2d cel shading, watercolor texture, warm sunlight`
* **Negative**: `(worst quality:1.4), (low quality:1.4), 3d render, cgi, modern sci-fi, sleek futuristic jet, cyberpunk, sharp angular armor, neon glow, blur`

---

## 即拷即用实战预设

### 预设 1：云海巡航的蒸汽飞艇（Airship Above Cloud Sea）
```text
A detailed vintage steampunk airship sailing through majestic golden sunset clouds, Hayao Miyazaki aesthetic.
The airship features a sturdy wooden hull, exposed copper pipes, spinning canvas propellers, and warm amber light glowing from portholes.
Wisps of white steam drift from its bronze chimney into the crisp mountain air.
Vast blue sky with dramatic golden hour sunbeams breaking through billowing clouds.
Hand-drawn cel animation, gouache painted clouds, nostalgic sense of grand adventure.
```

### 预设 2：被苔藓覆盖的古代机械巨神兵（Overgrown Steampunk Golem）
```text
An ancient colossal iron golem resting quietly in an overgrown sunny garden floating among the clouds, inspired by Laputa.
Its rusted iron armor is softened by green moss, climbing vines, and blooming yellow buttercups.
A small bird rests fearlessly on its outstretched mechanical finger.
Warm dappled sunlight, soft watercolor background by Kazuo Oga, peaceful and melancholic atmosphere.
```
