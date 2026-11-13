"""
Enterprise FastAPI Server for AI Short Video Production Workbench.
Serves full-featured, zero-external-dependency visual human-in-the-loop review studio.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException, Body, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Ensure workspace root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workbench.orchestrator import WorkbenchOrchestrator
from workbench.mock_gateway import Mock302AIGateway
from workbench.domain.entities import Project, Shot, ShotStatus, KeyframeCandidate, FrameType, CandidateSlot, SourceType
from workbench.domain.exceptions import InsufficientBalanceError, InpaintingExceededError

app = FastAPI(
    title="Enterprise AI Short Video Workbench API",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core orchestrator with gateway
mock_gateway = Mock302AIGateway(initial_balance=4.8213)
orchestrator = WorkbenchOrchestrator(api_client=mock_gateway, user_balance=4.8213)

PRESETS = {
    "taotie": {
        "title": "饕餮神话·破晓篇",
        "screenplay": "上古祭坛破晓，饕餮自浓雾中昂首苏醒，金色晨曦刺破苍穹，巨兽发出震天长啸。"
    },
    "libai": {
        "title": "李白·诗剑行 (国风水墨篇)",
        "screenplay": "深秋雨夜竹林，诗仙李白白袍胜雪，驻足凝视三尺青锋，剑气化作泼墨狂龙激荡四野，挥剑斩断万重愁。"
    },
    "four_beasts": {
        "title": "山海经·四凶兽启示录",
        "screenplay": "混沌无面撕裂虚空，穷奇振翅咆哮烈焰，梼杌傲立玄冰裂谷，饕餮吞噬万象极光，远古神话在大地苏醒。"
    }
}

# Current Active Project
CURRENT_PROJECT = orchestrator.create_project(
    title=PRESETS["taotie"]["title"],
    screenplay_raw=PRESETS["taotie"]["screenplay"]
)
orchestrator.step_decompose(CURRENT_PROJECT)
orchestrator.step_generate_keyframes_batch(CURRENT_PROJECT)

# Map keyframe candidate URLs to local visual endpoints for zero-failure visual rendering
def ensure_visual_candidate_urls(project: Project):
    for shot in project.shots:
        for c in shot.start_candidates:
            if not c.image_url.startswith("/api/media/preview"):
                c.image_url = f"/api/media/preview/{shot.sequence_index}/START/{c.candidate_slot.value}?v={c.revision_version}&id={c.id[:6]}"
        for c in shot.end_candidates:
            if not c.image_url.startswith("/api/media/preview"):
                c.image_url = f"/api/media/preview/{shot.sequence_index}/END/{c.candidate_slot.value}?v={c.revision_version}&id={c.id[:6]}"

ensure_visual_candidate_urls(CURRENT_PROJECT)

WEB_DIR = Path(__file__).parent.resolve()


@app.get("/", response_class=HTMLResponse)
def read_root():
    index_file = WEB_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return index_file.read_text(encoding="utf-8")


@app.get("/api/finops/balance")
def get_balance():
    return {
        "current_balance": orchestrator.user_balance,
        "is_safe": orchestrator.user_balance >= (0.3005 * 1.2),
        "required_safety_line": round(0.3005 * 1.2, 4)
    }


@app.get("/api/project")
def get_current_project():
    return CURRENT_PROJECT.model_dump()


@app.get("/api/presets")
def get_presets():
    return [
        {"id": k, "title": v["title"], "screenplay": v["screenplay"]}
        for k, v in PRESETS.items()
    ]


@app.post("/api/project/preset/{preset_id}")
def load_preset_project(preset_id: str):
    if preset_id not in PRESETS:
        raise HTTPException(status_code=404, detail="Preset not found")
    global CURRENT_PROJECT
    p_info = PRESETS[preset_id]
    CURRENT_PROJECT = orchestrator.create_project(
        title=p_info["title"],
        screenplay_raw=p_info["screenplay"]
    )
    orchestrator.step_decompose(CURRENT_PROJECT)
    orchestrator.step_generate_keyframes_batch(CURRENT_PROJECT)
    ensure_visual_candidate_urls(CURRENT_PROJECT)
    return CURRENT_PROJECT.model_dump()


@app.post("/api/decompose")
def decompose_screenplay(payload: Dict[str, Any] = Body(...)):
    raw_text = payload.get("screenplay", "")
    if not raw_text:
        raise HTTPException(status_code=400, detail="Screenplay text is required")
    CURRENT_PROJECT.screenplay_raw = raw_text
    orchestrator.step_decompose(CURRENT_PROJECT)
    orchestrator.step_generate_keyframes_batch(CURRENT_PROJECT)
    ensure_visual_candidate_urls(CURRENT_PROJECT)
    return CURRENT_PROJECT.model_dump()


@app.post("/api/shots/{shot_id}/select_candidate")
def select_candidate(shot_id: str, payload: Dict[str, Any] = Body(...)):
    shot = next((s for s in CURRENT_PROJECT.shots if s.id == shot_id), None)
    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")

    candidate_id = payload.get("candidate_id")
    frame_type = payload.get("frame_type")  # "START" or "END"

    if frame_type == "START":
        cand = next((c for c in shot.start_candidates if c.id == candidate_id), None)
        if cand:
            shot.selected_start_frame_id = cand.id
    elif frame_type == "END":
        cand = next((c for c in shot.end_candidates if c.id == candidate_id), None)
        if cand:
            shot.selected_end_frame_id = cand.id
    else:
        raise HTTPException(status_code=400, detail="Invalid frame_type")

    return shot.model_dump()


@app.post("/api/shots/{shot_id}/approve")
def approve_shot_keyframes(shot_id: str):
    shot = next((s for s in CURRENT_PROJECT.shots if s.id == shot_id), None)
    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")

    if not shot.selected_start_frame_id or not shot.selected_end_frame_id:
        raise HTTPException(status_code=400, detail="Both start and end keyframes must be selected")

    shot.status = ShotStatus.KEYFRAMES_APPROVED
    return shot.model_dump()


@app.post("/api/shots/{shot_id}/inpaint")
def submit_inpaint(shot_id: str, payload: Dict[str, Any] = Body(...)):
    shot = next((s for s in CURRENT_PROJECT.shots if s.id == shot_id), None)
    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")

    target_candidate_id = payload.get("candidate_id")
    mask_url = payload.get("mask_url", "https://mock-oss.302.ai/masks/temp_mask.png")
    prompt = payload.get("prompt", "修复画面局部瑕疵")

    try:
        updated_shot = orchestrator.step_inpaint_shot(
            shot=shot,
            candidate_id=target_candidate_id,
            mask_url=mask_url,
            feedback_prompt=prompt
        )
        # Update image url of the newly inprinted candidate to show visual badge
        ensure_visual_candidate_urls(CURRENT_PROJECT)
        return updated_shot.model_dump()
    except InpaintingExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/shots/{shot_id}/synthesize")
def synthesize_video(shot_id: str, payload: Dict[str, Any] = Body(...)):
    shot = next((s for s in CURRENT_PROJECT.shots if s.id == shot_id), None)
    if not shot:
        raise HTTPException(status_code=404, detail="Shot not found")

    start_id = payload.get("start_frame_id", shot.selected_start_frame_id)
    end_id = payload.get("end_frame_id", shot.selected_end_frame_id)

    try:
        ready_shot = orchestrator.step_approve_and_synthesize(
            shot=shot,
            selected_start_id=start_id,
            selected_end_id=end_id
        )
        return ready_shot.model_dump()
    except InsufficientBalanceError as e:
        raise HTTPException(status_code=402, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/finops/ledger")
def get_ledger():
    return {
        "ledger": [entry.model_dump() for entry in orchestrator.finops.ledger],
        "total_cost": orchestrator.finops.get_total_accumulated_cost()
    }


@app.get("/api/pipelines")
def list_pipelines():
    pipelines_dir = PROJECT_ROOT / "pipelines"
    results = []
    meta = {
        "libai_v2_anime_pipeline.py": "李白·诗剑行 国风水墨二次元动漫 15s 工业化视频生成管线",
        "libai_shijianxing_pipeline.py": "李白·诗剑行 3D CGI 写实电影级视频生成管线",
        "run_four_beasts_3d_pipeline.py": "山海经四大凶兽 60s 电影级 3D 渲染与全景音效大片管线",
        "taotie_pipeline.py": "饕餮苏醒电影感 5s 视频与多模态 VLM 质量门禁管线",
        "taotie_v2_pipeline.py": "饕餮 v2 进阶版端到端全时序视觉一致性视频生成管线",
        "siliconflow_video_pipeline.py": "硅基流动多模型生态混合调度短视频管线",
        "generate_3d_realistic_references.py": "3D 超写实神话生物影视级资产参考图生成工具",
        "generate_four_beasts_references.py": "2D 国风水墨动画四大凶兽参考图生成工具",
        "regenerate_3d_hundun.py": "凶兽混沌 3D 参考图局部重绘迭代工具",
        "regenerate_hundun.py": "凶兽混沌 2D 水墨参考图迭代工具",
        "create_cinematic_audio.py": "高保真国风武侠环境音效与立体声电影级配乐压制",
        "render_clean_promo.py": "无损 1080P/4K 视频压制与成片导出工具",
        "run_workbench_demo.py": "工作台端到端交互式 CLI 演示驱动"
    }

    if pipelines_dir.exists():
        for f in pipelines_dir.glob("*.py"):
            results.append({
                "filename": f.name,
                "title": meta.get(f.name, f.name),
                "path": str(f.relative_to(PROJECT_ROOT))
            })
    return results


@app.get("/api/media/preview/{shot_seq}/{frame_type}/{slot}")
def render_visual_preview(shot_seq: int, frame_type: str, slot: str, v: int = 1, id: str = ""):
    """
    Renders high-fidelity, cinema-dark widescreen vector SVG frame.
    Guarantees 100% offline self-contained visuals with zero broken images.
    """
    is_start = (frame_type == "START")
    bg_gradient = "linear-gradient(135deg, #0d1b2a 0%, #1b263b 50%, #0d1117 100%)" if is_start else "linear-gradient(135deg, #2b1704 0%, #4a280a 50%, #0f0a05 100%)"
    accent_color = "#38bdf8" if is_start else "#fbbf24"
    frame_title = "起幅 · START KEYFRAME" if is_start else "落幅 · END KEYFRAME"
    camera_desc = "远景景深 · 空间定位 (WIDE ESTABLISHING)" if is_start else "特写张力 · 动作终态 (CLOSE-UP CONVERGENCE)"
    
    # Visual seed variations
    is_slot_b = (slot == "B")
    has_inpaint = (v > 1)
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="100%" height="100%">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{ '#0b1329' if is_start else ('#311508' if not is_slot_b else '#251206') }"/>
      <stop offset="50%" stop-color="{ '#1e293b' if is_start else ('#582d0c' if not is_slot_b else '#451e06') }"/>
      <stop offset="100%" stop-color="#070a13"/>
    </linearGradient>
    <radialGradient id="lensGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.35"/>
      <stop offset="70%" stop-color="{accent_color}" stop-opacity="0.05"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
    </pattern>
  </defs>

  <!-- Cinema Backdrop -->
  <rect width="1280" height="720" fill="url(#bgGrad)"/>
  <rect width="1280" height="720" fill="url(#grid)"/>

  <!-- Dynamic Atmospheric Glow -->
  <circle cx="{ '420' if is_start else '860' }" cy="360" r="320" fill="url(#lensGlow)"/>

  <!-- Cinematic Beast / Subject Artistic Silhouette Vector -->
  <g transform="translate(640, 370) scale({ '1.0' if is_start else '1.4' })" opacity="0.85">
    <!-- Mountain/Altar Base -->
    <path d="M -480 200 L -200 40 L 0 100 L 220 20 L 480 200 Z" fill="#0d1117" opacity="0.9"/>
    <!-- Mythical Beast Silhouette Anatomy -->
    <path d="M -120 40 Q -80 -120 0 -130 Q 80 -120 120 40 Q 60 70 0 70 Q -60 70 -120 40 Z" fill="#111827"/>
    <!-- Horns / Spikes -->
    <path d="M -70 -100 Q -140 -200 -180 -160 Q -120 -110 -60 -80 Z" fill="{accent_color}" opacity="0.8"/>
    <path d="M 70 -100 Q 140 -200 180 -160 Q 120 -110 60 -80 Z" fill="{accent_color}" opacity="0.8"/>
    <!-- Glowing Eyes / Energy Core -->
    <circle cx="-35" cy="-70" r="{ '7' if is_start else '11' }" fill="#ffffff" filter="drop-shadow(0 0 8px {accent_color})"/>
    <circle cx="35" cy="-70" r="{ '7' if is_start else '11' }" fill="#ffffff" filter="drop-shadow(0 0 8px {accent_color})"/>
  </g>

  <!-- Inpainting Mask Patch (if version > 1) -->
  { f'''
  <g transform="translate(730, 240)">
    <circle cx="0" cy="0" r="65" fill="#10b981" fill-opacity="0.2" stroke="#10b981" stroke-width="2" stroke-dasharray="6,4"/>
    <rect x="-50" y="-12" width="100" height="24" rx="12" fill="#10b981"/>
    <text x="0" y="4" font-family="monospace" font-size="12" fill="#ffffff" font-weight="bold" text-anchor="middle">INPAINT REPAIRED (v{v})</text>
  </g>
  ''' if has_inpaint else '' }

  <!-- Cinematic HUD Overlays -->
  <rect x="24" y="24" width="1232" height="672" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
  <!-- Corner Crop Marks -->
  <path d="M 24 64 L 64 64 M 64 24 L 64 64" stroke="{accent_color}" stroke-width="3" fill="none"/>
  <path d="M 1256 64 L 1216 64 M 1216 24 L 1216 64" stroke="{accent_color}" stroke-width="3" fill="none"/>
  <path d="M 24 656 L 64 656 M 64 696 L 64 656" stroke="{accent_color}" stroke-width="3" fill="none"/>
  <path d="M 1256 656 L 1216 656 M 1216 696 L 1216 656" stroke="{accent_color}" stroke-width="3" fill="none"/>

  <!-- Info Badges Header -->
  <rect x="40" y="40" width="220" height="34" rx="6" fill="rgba(0,0,0,0.65)" stroke="rgba(255,255,255,0.15)"/>
  <text x="54" y="62" font-family="'Segoe UI', sans-serif" font-size="14" font-weight="bold" fill="{accent_color}">SHOT #{shot_seq:02d} · CANDIDATE {slot}</text>

  <rect x="270" y="40" width="180" height="34" rx="6" fill="rgba(0,0,0,0.65)" stroke="rgba(255,255,255,0.15)"/>
  <text x="284" y="62" font-family="monospace" font-size="13" fill="#94a3b8">MODEL: GPT-IMG-2.6</text>

  <!-- Bottom Widescreen Slate -->
  <rect x="40" y="630" width="1200" height="50" rx="8" fill="rgba(0,0,0,0.75)" stroke="rgba(255,255,255,0.1)"/>
  <text x="60" y="661" font-family="'Segoe UI', sans-serif" font-size="16" font-weight="bold" fill="#f8fafc">{frame_title}</text>
  <text x="320" y="660" font-family="'Segoe UI', sans-serif" font-size="13" fill="#cbd5e1">|   {camera_desc}   |   COST: $0.0223 USD   |   VER: v{v}</text>
  <text x="1220" y="661" font-family="monospace" font-size="13" fill="{accent_color}" text-anchor="end">● 24FPS 4K DCI</text>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")


def start_server(port: int = 8000):
    uvicorn.run("workbench.web.server:app", host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    start_server()
