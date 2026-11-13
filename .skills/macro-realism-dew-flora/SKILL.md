---
name: macro-realism-dew-flora
description: 【风格06 · 微距微观写实】细分场景指南：露珠植物与晨光水滴。专用于清晨草叶晨露、叶脉微距、水滴倒映微观世界、起雾晨曦与极致浅景深水珠特写。
---

# 【风格06 · 微距微观写实】露珠植物与晨光水滴指南 (Macro Dew & Flora Skill)

本指南针对**清晨叶片上的晶莹露珠、水滴折射微观世界、晨雾氤氲与植物微观细胞肌理**。

核心命题：完美再现自然界极具治愈感的微观奇观——一颗凝结在翠绿草叶上的饱满水滴，如凸透镜般折射出清晨森林的倒影，晨雾在金色曙光中化为梦幻光斑。

---

## 核心美学特征与微观光学法则

### 1. 水滴的表面张力与微观折射
* **物理形态**：因表面张力（Surface tension）形成的完美饱满水珠，底部与叶面接触角自然过渡。
* **凸透镜倒影（Optical Inverted Refraction）**：水珠内部清晰倒映出**颠倒的微缩清晨森林、金黄朝阳或花朵倒影**，光线在水滴球体内产生焦散与彩虹色散微光。

### 2. 植物叶片的显微级结构
* **叶脉导管透光**：半透明的叶脉网络，逆光下呈现通透的翠碧色（Translucent emerald green）。
* **微绒毛（Trichomes）**：叶缘分布着极纤细的银色植物腺毛，绒毛尖端凝结着更细小的微型水雾珠，晶莹剔透。

### 3. 清晨起雾与光学景深
* **100mm 微距虚化**：背景是清晨森林升腾的白雾（Rising morning mist），在初升朝阳照射下化为柔滑的奶油状金绿色大光斑（Creamy golden-green circular bokeh）。

---

## 提示词模块化配方

### 核心结构：
$$\text{Prompt} = \text{[单颗晨露水滴主体与位置]} + \text{[水滴内部凸透镜倒影折射]} + \text{[叶片微脉络与腺毛显微细节]} + \text{[清晨起雾与金色逆光]} + \text{[100mm 微距专业镜头规范]}$$

### 专用词库：
* **水滴与折射**：`extreme macro photography of a single crystal-clear water droplet on a vibrant green leaf, perfect spherical dewdrop with high surface tension, clear inverted miniature landscape reflected inside the water drop, prismatic caustic light`
* **植物微结构**：`microscopic plant details, translucent leaf veins glowing in backlight, delicate tiny silver plant hairs (trichomes) holding tiny mist droplets, cellular leaf texture`
* **气候与光影**：`early morning sunrise, rising soft morning mist, gentle golden sunbeams, backlit rim light illuminating the droplet edge, ethereal dreamy atmosphere`
* **摄影光学**：`shot on 100mm f/2.8 macro lens, 1:1 reproduction ratio, razor-sharp focus on the droplet, extremely shallow depth of field, creamy circular bokeh background, National Geographic nature photography`
* **负向排除词**：`blurry droplet, artificial fake computer graphic, dry leaf, midday harsh light, plastic render, flat 2d, noisy artifacts`

---

## 主流生图模型适配

### 1. Gemini (302.ai / 谷歌原生接口)
> **Prompt:**  
> An award-winning extreme macro photograph capturing a single crystal-clear morning dew droplet resting perfectly on the tip of a vibrant green leaf at dawn. The spherical water droplet acts as a natural lens, sharply refracting an inverted miniature image of the misty sunrise and distant trees inside. Translucent cellular leaf veins glow with warm emerald light under the soft morning sun. Delicate microscopic hairs on the leaf catch the rising morning mist, creating tiny sparkling micro-droplets. In the background, heavy morning mist rises peacefully in the early dawn, dissolved into a stunning creamy golden-green bokeh. Shot on a 100mm f/2.8 macro lens, razor-sharp focus on the droplet, breathtaking optical clarity, National Geographic macro photography style, no 3D CGI plastic rendering.

### 2. Midjourney (v6 / Niji 6)
> **Prompt:**  
> Extreme macro photography, crystal-clear morning dew droplet on a green leaf, inverted sunrise reflection inside the water drop, rising morning mist, 100mm macro lens, razor-sharp focus, creamy soft golden bokeh, National Geographic style --ar 16:9 --style raw --v 6.0

### 3. Stable Diffusion / FLUX
* **Positive**: `(masterpiece, best quality:1.2), extreme macro, single water droplet on leaf, morning dew, inverted reflection in droplet, rising mist, 100mm macro lens, shallow depth of field, translucent leaf veins, creamy bokeh, national geographic`
* **Negative**: `(worst quality:1.4), (low quality:1.4), 3d cgi, fake plastic droplet, cartoon, blurry main subject, harsh noon light, flat colors`

