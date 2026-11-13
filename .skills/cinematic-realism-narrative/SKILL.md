---
name: cinematic-realism-narrative
description: 【风格03 · 电影感超写实人像】细分场景指南：影视剧照与故事分镜。专用于 2.39:1 变形宽银幕电影画面、强悬念叙事分镜、戏剧性冷暖打光与情绪大片，解决画面缺乏电影故事感与张力的问题。
---

# 【风格03 · 电影感超写实人像】影视剧照与故事分镜指南 (Cinematic Narrative Skill)

本指南针对**2.39:1 变形宽银幕（Anamorphic）电影剧照、强戏剧张力的人物特写与影视概念分镜**。

不同于普通的单张肖像，电影剧照必须具备**“故事正在发生的前一秒或后一秒”的悬念感**。本指南通过**变形宽银幕横向眩光、冷暖光冲突与情绪化空间构图**三大支柱实现强烈的电影感。

---

## 核心美学特征与电影工业法则

### 1. 宽银幕变形镜头的光学特征
* **2.39:1 宽画幅**：利用极宽的画幅比例（Aspect Ratio 2.39:1 或 16:9），营造强烈的影视院线感。
* **椭圆焦外光斑与横向水平眩光（Anamorphic Flare）**：背景虚化光斑呈椭圆形拉伸，强光源处带有优雅的横向冷蓝或暖金细拉丝光晕。

### 2. 情绪化冲突打光
* **冷暖对冲（Color Temperature Contrast）**：人物面部一侧受窗外冰冷月光/霓虹青光照射，另一侧受室内温暖台灯/烛光映照，在明暗交界线上呈现丰富的色彩过渡。
* **环境烟气与体积光（Atmospheric Haze）**：空间中弥漫着淡淡的微烟或薄雾，让光束（God rays）显现出实体轨迹，烘托悬疑或深情氛围。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[电影剧照镜头类型]} + \text{[角色悬念神态与动作]} + \text{[变形宽银幕冷暖布光]} + \text{[阿莱 ARRI 电影机与调色]} + \text{[深邃电影故事感]}$$

### 专用词库：
* **电影设备**：`cinematic movie still, shot on ARRI Alexa Mini LF, Panavision Anamorphic lenses, 2.39:1 aspect ratio`
* **光学特征**：`subtle horizontal blue anamorphic lens flare, oval bokeh, shallow depth of field, atmospheric haze`
* **布光与调色**：`dramatic dual-tone cinematic lighting, warm amber practical light clashing with cool cyan moonlight, rich cinematic color grading`
* **情绪与叙事**：`intense dramatic moment, subtle emotional tension, cinematic composition, authentic facial micro-expressions`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> A gripping cinematic movie still shot on ARRI Alexa Mini LF with Panavision Anamorphic lenses. A determined detective stands near a rain-streaked window in a dimly lit room, holding a vintage telephone receiver. The lighting is dramatically split: one side of his face is bathed in cool cyan light from a distant city neon sign through the wet glass, while the other side is warmed by an amber desk lamp. Atmospheric dust motes and cigarette smoke hang in the air. Authentic skin texture with natural sweat beads and stubble. 2.39:1 cinematic composition, psychological thriller film aesthetic, no CGI rendering, no plastic smooth skin.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> Cinematic movie still, shot on ARRI Alexa, Panavision anamorphic lens, dramatic moody dual lighting, intense emotional tension, natural skin texture, atmospheric haze, movie screenshot --ar 2.39:1 --style raw --v 6.0

