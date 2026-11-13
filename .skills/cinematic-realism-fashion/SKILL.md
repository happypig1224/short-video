---
name: cinematic-realism-fashion
description: 【风格03 · 电影感超写实人像】细分场景指南：时尚肖像与商业大片。专用于高端商业写真、时装杂志封面、85mm 浅景深面部特写与无瑕疵感裸妆质感，杜绝磨皮假人塑料感。
---

# 【风格03 · 电影感超写实人像】时尚肖像与商业大片指南 (Fashion Realism Skill)

本指南针对**高端时尚摄影、85mm 浅景深面部特写、杂志大片与品牌商业写真**。

核心痛点：商业肖像常常容易被 AI 算法“美颜过度”，变成毫无生气的塑料芭比娃娃。本指南通过**哈苏中画幅光学模拟、微毛孔保留与次表面散射（SSS）**，在保持美感的同时呈现极致的生物级细节。

---

## 核心美学特征与布光法则

### 1. 皮肤光学的“呼吸感”
* **裸妆质感与微毛孔**：面部保留细腻真实的天然毛孔（Visible pores）、鼻翼与脸颊边缘极细微的绒毛（Peach fuzz），仅在唇部与眼角保留水润高光。
* **次表面散射（SSS）**：强调用光穿透皮肤表层的半透明肉感，耳廓与指尖透出微红暖光。

### 2. 商业影棚专业布光系统
* **伦勃朗光（Rembrandt Lighting）**：阴影侧眼下形成经典的倒三角微光，赋予面部立体雕塑感。
* **大尺寸羽化柔光箱**：主光柔和均匀，避免刺眼反光；背景用 85mm f/1.4 浅景深柔化为奶油般的虚化光斑（Creamy bokeh）。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[模特气质与神态]} + \text{[时装设计与材质]} + \text{[影棚布光与次表面散射]} + \text{[哈苏中画幅/85mm f/1.4 镜头]} + \text{[自然皮肤细节微孔]}$$

### 专用词库：
* **摄影设备**：`shot on Hasselblad H6D-100c, 85mm f/1.4 lens, shallow depth of field, creamy background bokeh`
* **质感词汇**：`natural skin texture, visible skin pores, subtle peach fuzz, subsurface scattering, authentic skin details, minimal retouching`
* **光影控制**：`Rembrandt lighting, large softbox diffuse light, soft rim lighting, natural daylight fill`
* **商业质感**：`Vogue editorial portrait, high fashion commercial photography, elegant composition, muted sophisticated color grading`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> A high-fashion editorial portrait of an elegant woman, shot on Hasselblad H6D-100c with an 85mm f/1.4 portrait lens. The lighting is classic soft Rembrandt studio lighting, casting gentle shadows that sculpt her facial features. Authentic, unretouched skin texture with visible micro-pores, natural peach fuzz, and realistic subsurface scattering on her cheeks and ears. Shallow depth of field with a creamy, blurred studio background. Sophisticated neutral color palette, Vogue magazine cover quality, sharp focus on the eyes, no airbrushed plastic skin, no CGI rendering.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> High-fashion editorial portrait, 85mm f/1.4, shot on Hasselblad, natural skin texture, visible pores, softbox Rembrandt lighting, minimal retouching, creamy bokeh, cinematic color grading --ar 4:5 --style raw --v 6.0

