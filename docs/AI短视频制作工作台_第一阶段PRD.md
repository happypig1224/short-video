# 企业级AI短视频制作工作台（Phase 1 MVP）产品需求文档 (PRD)

## 1. 文档元数据与版本历史

- **产品名称**：企业级AI短视频制作工作台 (Enterprise AI Video Workbench)
- **版本阶段**：Phase 1 (MVP)
- **文档状态**：待评审 (Draft)
- **核心定位**：基于关键帧锁定与首尾帧插值架构，降低短视频生成废片率，实现单镜头成本可控的工业化生成工具。
- **关联方**：短视频编导、AI生图/生视频算法组、前端工程组、后端与FinOps计费组。

---

## 2. 核心痛点与量化指标

### 2.1 现状痛点
1. **文生视频废片率高**：直接依赖文生视频（T2V）生成动态镜头，肢体异化、场景漂移发生率超过 80%，大量消耗算力额度。
2. **试错成本不可控**：无事前计费预估，单镜头盲目尝试最高单价模型（如直接 4K 生成），单镜测试成本曾达到 2~5 美元。
3. **返工缺乏局部控制**：生成画面出现微小瑕疵（如手指畸变、道具穿模）时只能整张重绘，破坏已确认构图，造成算力二次浪费。
4. **前后镜头连续性差**：缺乏首尾帧空间和光影约束，镜头切换与镜头内部运镜缺乏物理逻辑。

### 2.2 Phase 1 验收指标
- **单镜头废片率**：从 >80% 降至 ≤5%（以进入首尾帧插值渲染且满足剧本要求的镜头比例核算）。
- **单镜头平均生成成本**：控制在 $0.35 以内（按 720P 插值渲染基线计算，不含二次 4K 超分）。
- **人工重试收敛次数**：单镜局部修正（Inpainting）平均交互次数 ≤2 次。
- **预算击穿拦截率**：100%（余额不足或超单任务预算上限时，在 API 请求发出前物理阻断）。

---

## 3. 系统工序架构与核心功能规格

Phase 1 工作台分为五大核心工序模块：

```
[输入剧本/创意] 
      │
      ▼
【F-01 智能分镜拆解】 ── (Gemini 3.8 Flash) ──> 结构化分镜列表 (Shot List)
      │
      ▼
【F-02 双关键帧候选池】 ── (起幅/落幅 双候选) ──> 候选帧 A/B
      │
      ▼
【F-03 人工评审与修正台】 ◄───┐ (打回重做/局部 Inpainting)
      │ (审核通过)            │
      ▼                       │
【F-05 事前算力预估熔断】      │ (未通过/需返工)
      │ (余额充足且授权)       │
      ▼                       │
【F-04 首尾帧视频插值】 ───────┘ (若运动断裂严重则降级回退)
      │
      ▼
[初版视频镜头库]
```

---

### F-01: 剧本与创意智能分镜拆解引擎

#### 1. 功能描述
系统接收用户输入的自然语言故事梗概、分集剧本或粗略创意，调用轻量语言模型自动输出严格结构化的多镜头分镜脚本。

#### 2. 模型选型与参数
- **推理模型**：`gemini-3.8-flash`（兼顾极低 Token 成本与高上下文解析能力）。
- **输出格式**：JSON 数组，严禁包含 Markdown 格式包裹符之外的散落文字。

#### 3. 分镜数据结构定义
每个分镜对象必须包含以下字段：
```json
{
  "shot_id": "shot_001",
  "sequence_index": 1,
  "scene_summary": "上古祭坛破晓，凶兽饕餮在浓雾中苏醒",
  "camera_motion": "缓缓推近并伴随低角度仰拍 (Push In & Low Angle Tilt Up)",
  "duration_seconds": 5,
  "start_frame_prompt": "Cinematic wide shot, ancient stone altar covered with moss, heavy morning mist, mythical beast Taotie silhouette awakening, glowing amber eyes, volumetric dawn light, 8k octane render, hyper-detailed textures",
  "end_frame_prompt": "Cinematic close-up shot, Taotie head emerging through the mist, razor-sharp fangs, intricate bone armor plates, piercing glowing eyes, dust particles floating in golden sunrise, photorealistic 8k",
  "dynamic_guidance": "从大远景浓雾剪影平滑推进到头部特写，雾气流向两侧散开，动作平缓无突变",
  "motion_strength": 5
}
```

#### 4. 业务规则
- 系统限制单次剧本拆解生成的最大镜头数为 30 个。
- 拆解完成后，用户可在前端表格视图中直接编辑各镜头的提示词、运镜方式与预估时长。

---

### F-02: 双关键帧候选池生成系统

#### 1. 功能描述
根据分镜拆解给出的提示词，系统并行调度图像生成模型，为每个镜头分别生成「起幅（Frame 0）」与「落幅（Frame 1）」各 2 张候选图（Candidate A 与 Candidate B），供人工挑选组合。

#### 2. 生成规则与技术栈
- **起幅生成**：使用 `start_frame_prompt` 生成 2 张图片（Seed A, Seed B）。
- **落幅生成**：以起幅确认图作为图生图参考底图（Image-to-Image / ControlNet Reference），注入 `end_frame_prompt` 生成 2 张落幅候选。确保落幅的角色骨骼结构、色彩方案与起幅保持一致。
- **推荐图像模型**：`gpt-image-2.6-sunburst` 或中档 SDXL/FLUX 方案，单张成本约 $0.02~$0.04。

#### 3. 界面交互
- 镜头卡片展开后，呈现 2×2 网格：
  - 左侧两格：起幅 Candidate A / Candidate B。
  - 右侧两格：落幅 Candidate A / Candidate B。
- 用户点击任意一张即可高亮选中，并作为当前镜头的激活帧（Active Frame）。

---

### F-03: 人工审核评审台与定向打回重做引擎

#### 1. 功能描述
短视频制作人员在视频渲染前，对起幅和落幅执行一致性检查。支持画面对比、局部圈选涂抹打回，杜绝因细节缺陷全量重跑。

#### 2. 核心交互模式
- **透光台对比模式（Onion Skinning）**：
  - 用户可拖动滑块调节起幅与落幅的半透明叠加比例（0% ~ 100%）。
  - 用于检查角色比例漂移、地平线倾斜或主体位置突变。
- **画笔圈选与打回（Mask & Rejection Loop）**：
  - 若候选图主体合格但局部有瑕疵，用户点击「局部修正」进入画布模式。
  - 界面提供自由画笔（Brush Size: 5px~100px）与矩形选择框，支持撤销/重做。
  - 用户在缺陷区域（如手指畸变、背景乱码文字）完成涂抹，生成单通道二值 Mask（缺陷区域为纯白 255，保留区域为纯黑 0）。
  - 用户输入修改要求（如「将六指修正为自然握拳五指，保持青铜手甲质感」）。
  - 点击「提交局部重绘」，系统调用 Inpainting API 仅对 Mask 区域做去噪重绘，保持外围构图 100% 不变。
- **整镜重抽（Regenerate All）**：
  - 若两张候选构图均偏离剧本，用户可输入文字修改建议，调整提示词后重新生成 2 张候选，原候选存入历史版本归档。

#### 3. 审核状态判定
- 镜头只有在同时具备「已确认起幅」与「已确认落幅」后，其状态流转为 `KEYFRAMES_APPROVED`，解锁视频生成按钮。

---

### F-04: 首尾帧插值图生视频合成器

#### 1. 功能描述
将人工审核确认的起幅与落幅打包，连同运镜控制指令与动态描述，输入视频生成模型完成中间动作插值，生成平滑连续的动态镜头片段。

#### 2. 接口调用与参数规格
- **底层模型适配**：支持首尾帧输入模式（如 `kling-v1-6` / `kling-v2-6` 或 `hailuo` 首尾帧能力）。
- **请求负载定义 (Payload)**：
  ```json
  {
    "model": "kling-v1-6",
    "prompt": "从大远景浓雾剪影平滑推进到头部特写，雾气流向两侧散开，动作平缓无突变",
    "image": "https://oss-domain/shots/shot_001/frame_start_approved.png",
    "image_tail": "https://oss-domain/shots/shot_001/frame_end_approved.png",
    "duration": 5,
    "mode": "std",
    "cfg_scale": 0.5
  }
  ```
- **质量基线**：Phase 1 统一采用 720P Standard 渲染模式，时长固定为 5 秒，单镜耗时 2~5 分钟。

#### 3. 产物管理
- 视频生成完成后自动回写工作台镜头列表，支持在轨循环播放预览。
- 提供帧率检查与丢帧标记，支持一键下载 MP4 原片。

---

### F-05: 事前算力与成本预估熔断器 (Pre-flight FinOps Gate)

#### 1. 功能描述
在任何耗费算力的 API 调用前，系统本地预估开销并检查用户账户可用余额。余额不足或预算超标时，立即中断请求并弹窗阻断。

#### 2. 算力计费公式
单次任务预估成本计算模型：
$$\text{Cost}_{\text{est}} = N_{\text{shots}} \times (P_{\text{llm}} + 4 \times P_{\text{image}} + P_{\text{video}})$$
- $N_{\text{shots}}$：当前选中提交的镜头总数。
- $P_{\text{llm}}$：分镜拆解预估 Token 开销（单次约 $0.0005）。
- $P_{\text{image}}$：单张关键帧生成单价（默认按 $0.025 计，每个镜头起落各 2 张即 4 张，约 $0.10）。
- $P_{\text{video}}$：单镜头 720P 5 秒视频插值单价（标准模式约 $0.189 ~ $0.27）。
- 典型单镜头基础预算基线：$0.0005 + $0.10 + $0.20 = $0.3005。

#### 3. 熔断与拦截规则
- **安全缓冲倍率**：系统要求账户可用余额 ≥ $\text{Cost}_{\text{est}} \times 120\%$。
- **阻断行为**：
  1. 若余额低于安全线，工作台全局禁用「开始批量生成」按钮。
  2. 弹出高优先级对话框，明确列出当前余额与预估开销，标出差额并提供充值链接。
  3. 严禁前端在未核准额度前直接向 302.AI 发送批处理请求。
- **单镜重做预算封顶**：
  - 单个镜头的局部重绘（Inpainting）次数达到 3 次时，系统触发防沉迷警告，提示编导检查起落幅语义是否存在根本冲突。

---

## 4. 镜头状态机模型

镜头从创建到就绪经历以下明确状态：

```
[DRAFT] (草稿/空镜头)
   │ 用户输入创意并执行拆解
   ▼
[SCRIPT_SPLIT] (分镜脚本生成完毕)
   │ 触发起落幅生成
   ▼
[KEYFRAME_GENERATING] (关键帧算力运行中)
   │ 生成返回 4 张候选图
   ▼
[REVIEW_PENDING] (等待人工评审)
   ├─► 用户圈选涂抹打回 ──► [INPAINTING_RUNNING] ──► 返回新图 ──► [REVIEW_PENDING]
   ├─► 用户全图调整提示词 ──► [KEYFRAME_GENERATING]
   └─► 用户确认起落幅选中
         ▼
[KEYFRAMES_APPROVED] (关键帧就绪)
   │ 用户点击渲染视频 (通过事前费用熔断检查)
   ▼
[VIDEO_SYNTHESIZING] (视频插值中)
   ├─► 生成成功 ──► [READY] (单镜头就绪)
   └─► 算力超时或接口报错 ──► [FAILED] (支持原参单键重试)
```

---

## 5. 数据实体与 Schema 规范

### 5.1 镜头实体 (Shot Entity)
```typescript
interface ShotEntity {
  id: string;                      // 镜头唯一 UUID
  projectId: string;               // 所属项目 ID
  sequenceIndex: number;           // 剧本镜头时序编号
  sceneDescription: string;        // 场记描述
  cameraMotion: string;            // 运镜代码 (Pan/Tilt/Zoom/Truck)
  durationSeconds: number;         // 镜头计划时长 (Phase 1 默认为 5)
  
  // 提示词与引导
  startPrompt: string;             // 起幅提示词
  endPrompt: string;               // 落幅提示词
  motionPrompt: string;            // 动态运镜引导词
  
  // 关键帧候选资源
  startCandidates: KeyframeCandidate[]; // 起幅 2 张候选
  endCandidates: KeyframeCandidate[];   // 落幅 2 张候选
  selectedStartFrameId?: string;        // 选中的起幅 ID
  selectedEndFrameId?: string;          // 选中的落幅 ID
  
  // 视频合成产物
  videoTaskId?: string;            // 外部 API 任务编号
  videoUrl?: string;               // 视频回传存储 URL
  videoStatus: ShotStatus;         // 当前流转状态
  
  // 成本审计
  accumulatedCostUsd: number;      // 本镜头已耗费成本 (美元累计值)
  createdAt: string;
  updatedAt: string;
}

interface KeyframeCandidate {
  id: string;
  imageUrl: string;
  sourceType: 'ORIGINAL' | 'INPAINTED';
  maskUrl?: string;                // 若为局部涂抹，关联对应二值 Mask
  feedbackNote?: string;           // 打回时的人工批注
  costUsd: number;
}

type ShotStatus = 
  | 'DRAFT'
  | 'SCRIPT_SPLIT'
  | 'KEYFRAME_GENERATING'
  | 'REVIEW_PENDING'
  | 'INPAINTING_RUNNING'
  | 'KEYFRAMES_APPROVED'
  | 'VIDEO_SYNTHESIZING'
  | 'READY'
  | 'FAILED';
```

---

## 6. 异常处理与边界场景定义

| 场景编号 | 异常场景 | 触发机制 | 表现与处置策略 |
| :--- | :--- | :--- | :--- |
| **EX-01** | 首尾帧空间透视冲突 | 起幅为人物正脸特写，落幅为全景背影，且人物朝向完全反转。 | 视频插值模型极易产生肢体扭曲。前端在用户同时选定两张图时，调用轻量视觉模型对两图进行空间一致性快检；若判定动作跨度过大，弹出「运动幅度过大风险警告」，建议用户拆分为两个连续镜头。 |
| **EX-02** | 302.AI 算力接口返回 403 / 余额不足 | 账户余额扣减至 0，接口返回 `err_code: -10004`。 | 捕获该错误码，不执行盲目重试；挂起该镜头的生成任务，状态置为 `FAILED`，前端显示全局红色横幅通知并提供充值跳转按钮。 |
| **EX-03** | 视频合成长时间排队阻塞 | 视频生成任务轮询时间超过 10 分钟未返回结果。 | 终止前端轮询，将任务标记为 `TIMEOUT`；后台保留 Webhook 回调监听，恢复后自动更新视频地址，并向用户发送就绪提示。 |
| **EX-04** | 画布 Mask 区域过大误操作 | 用户使用画笔涂抹面积超过原画的 70%。 | 弹窗提示「涂抹区域超过 70%，局部重绘效果已接近全图重抽，建议直接修改提示词执行全图重新生成」，降低无效算力消耗。 |

---

## 7. 实施计划与里程碑

1. **第 1 周：数据流与分镜原型跑通**
   - 完成 LLM 结构化拆解 Prompt 固化。
   - 跑通前端分镜列表与 302.AI 图生图接口联调。
2. **第 2 周：关键帧评审台与 Inpainting 画布**
   - 交付起落幅 A/B 候选双卡片交互。
   - 交付 HTML5 Canvas 涂抹掩码生成与局部重绘联调。
3. **第 3 周：首尾帧视频合成与 FinOps 熔断网关**
   - 接入 Kling / Hailuo 首尾帧 I2V 任务调度与状态轮询。
   - 上线事前余额检查与费用明细阻断器。
4. **第 4 周：联调测试与首批 sample 制作**
   - 验证单镜废片率低于 5% 指标。
   - 输出完整的端到端制作案例及操作手册。
