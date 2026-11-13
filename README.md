# AI 短视频制作与影视级管线工作台 (AI Short Video Studio)

面向企业级 AI 短视频生产与影视级低成本工业化制作的完整工程仓库，包含核心工作台系统、自动化质量门禁测试套件、离线批量视频生成管线与完整系统规范设计文档。

---

## 📁 目录结构导览

```
short video/
├── ruoyi-ai-workbench/            # 极简高质感 Kling Studio 前端源码 (Vue 3 + Element Plus + Vite)
├── server/                        # 生图工作台 FastAPI 后端服务与 302.ai 模型代理
├── scripts/                       # 核心生图与视频生成脚本 (包含 Kling O3、MiniMax、Gemini 等)
├── IP视觉资产库/                  # 小呆呆 IP 角色母图、表情包、头像、壁纸规范与资产库
├── workbench/                     # 企业级短视频工作台系统核心源码 (Domain / Services / Web / Orchestrator)
├── tests/                         # 自动化测试套件 (包含 FinOps、Review、Synthesis 等 21 个单元与端到端用例)
├── pipelines/                     # 完整视频生成管线与驱动脚本 (13 个独立管线与工具)
├── docs/                          # 产品、架构、工业化制作指南与前端技术规范
├── start_ai_workbench.py          # 一键启动 Kling Studio 生图工作台 (FastAPI + Vue3)
├── .env.example                   # 环境变量示例文件 (302.ai API Key 配置)
├── .gitignore                     # Git 忽略规则配置文件
└── README.md                      # 项目快速入门与索引
```

---

## 🚀 核心模块说明

### 1. `workbench/` - 工作台系统核心
- **`domain/`**: 业务核心领域实体与异常定义（镜头 Shot、关键帧 Keyframe、FinOps 账本）。
- **`services/`**: 核心服务引擎
  - `script_engine.py`: 分镜智能拆解与提示词工程化
  - `keyframe_engine.py`: 起落双关键帧生成与一致性锁定
  - `review_engine.py`: 多模态质量门禁与局部缺陷 Inpainting 画布打回
  - `video_synthesis_engine.py`: 首尾帧插值视频渲染
  - `finops_guard.py`: 事前算力熔断与成本审计
- **`web/`**: 现代化交互 Web 服务与实时流水线控制台前端。

### 2. `pipelines/` - 视频生成管线与驱动脚本
统一管理所有针对特定主题的自动化视频生成管道：
- **`run_workbench_demo.py`**: 工作台全流程交互式 CLI 演示
- **`libai_v2_anime_pipeline.py` / `libai_shijianxing_pipeline.py`**: 李白·诗剑行国风动漫与写实短视频端到端生成管线
- **`run_four_beasts_3d_pipeline.py`**: 上古四凶兽 60秒 3D 电影级渲染合成管道
- **`taotie_pipeline.py` / `taotie_v2_pipeline.py`**: 饕餮电影感视频与多模态审计管道
- **`siliconflow_video_pipeline.py`**: 硅基流动视频模型适配生成管线
- **辅助生成工具**:
  - `generate_four_beasts_references.py` / `generate_3d_realistic_references.py`: 2D/3D 资产参考图生成
  - `regenerate_hundun.py` / `regenerate_3d_hundun.py`: 单镜头参考修正工具
  - `create_cinematic_audio.py` / `render_clean_promo.py`: 电影级音频合成与成片压制

### 3. `docs/` - 规范与技术文档
- **`AI短视频制作工作台_第一阶段PRD.md`**: 工作台第一阶段业务需求与验收标准
- **`AI短视频制作工作台_第一阶段架构设计.md`**: 工业级系统架构与流水线设计方案
- **`AI短视频影视级低成本工业化制作指南.md`**: 影视级低成本工业化实操方法论
- **`FRONTEND_SPECIFICATION.md`**: Web 前端与编导操作台交互规范
- **`TEST_PLAN_AND_ACCEPTANCE_CRITERIA.md`**: 质量保障计划与验收用例集

---

## ⚡ 快速开始

### 1. 运行系统自动化测试
```bash
python -m pytest tests/
```

### 2. 运行工作台演示 Demo
```bash
python pipelines/run_workbench_demo.py
```

### 3. 一键启动 Web 可视化中台（推荐）
```bash
python start_workbench.py
```
启动后将自动为您在默认浏览器中打开可视化的编导人工审核工作台（`http://127.0.0.1:8000`）。

也可以手动启动：
```bash
python workbench/web/server.py
```
