"""
FastAPI 后端服务: 桥接 302.ai 可灵 O3 生图脚本 (generate_kling_image_o3.py)
为若依风格的生图工作台提供 RESTful API 与数据持久化
"""

import os
import sys
import time
import json
import uuid
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# 确保能引用 scripts 目录下的生图核心客户端
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_kling_image_o3 import KlingImageO3Client, DEFAULT_API_KEY, DEFAULT_BASE_URLS

# 数据存储目录
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"
TASKS_FILE = DATA_DIR / "tasks.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 初始化客户端
kling_client = KlingImageO3Client()

app = FastAPI(
    title="RuoYi AI Image Workbench API",
    description="若依风格 AI 生图工作台后端接口",
    version="1.0.0"
)

# 允许跨域联调
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= 数据持久化辅助函数 =================
def load_tasks() -> List[Dict[str, Any]]:
    if not TASKS_FILE.exists():
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_tasks(tasks: List[Dict[str, Any]]):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def get_task_by_id(task_id: str) -> Optional[Dict[str, Any]]:
    tasks = load_tasks()
    for t in tasks:
        if t["task_id"] == task_id:
            return t
    return None


def update_task_record(task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    tasks = load_tasks()
    for i, t in enumerate(tasks):
        if t["task_id"] == task_id:
            tasks[i].update(updates)
            save_tasks(tasks)
            return tasks[i]
    return None


# ================= 请求模型 =================
class GenerateImageRequest(BaseModel):
    prompt: str = Field(..., description="生图提示词")
    model_id: Optional[str] = Field(default="klingai", description="选择的生图模型 ID")
    reference_images: Optional[List[str]] = Field(default=[], description="参考图URL或本地路径列表")
    aspect_ratio: str = Field(default="1:1", description="宽高比")
    img_resolution: str = Field(default="1k", description="画质分辨率 1k/2k/4k")
    image_count: int = Field(default=1, ge=1, le=4, description="生成张数 1-4")
    story_mode: bool = Field(default=False, description="组图连贯模式")
    api_key: Optional[str] = Field(default=None, description="自定义 API Key")


class UpdateConfigRequest(BaseModel):
    api_key: Optional[str] = Field(default=None, description="自定义 API Key")
    base_url: Optional[str] = Field(default=None, description="自定义 302.ai Base URL")


# ================= 动态模型拉取与缓存 =================
import requests as sync_requests
_CACHED_MODELS: List[Dict[str, Any]] = []
_LAST_MODELS_FETCH_TIME: float = 0.0

def fetch_302_models(api_key: str, base_url: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
    global _CACHED_MODELS, _LAST_MODELS_FETCH_TIME
    now = time.time()
    if not force_refresh and _CACHED_MODELS and (now - _LAST_MODELS_FETCH_TIME < 600):
        return _CACHED_MODELS

    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Mozilla/5.0 302Studio/2.0"
    }

    raw_models = []
    for test_url in [base_url, "https://api.302.ai", "https://api.302ai.com"]:
        try:
            resp = sync_requests.get(f"{test_url}/v1/models", headers=headers, timeout=8)
            if resp.status_code == 200:
                raw_models = resp.json().get("data", [])
                break
        except Exception:
            continue

    keywords = ["kling", "flux", "midjourney", "image", "dall", "sd", "luma", "ideogram", "recraft", "cogview", "minimax"]
    exclude_keywords = ["voice", "audio", "text2voice", "tts", "asr", "whisper", "v2v", "video-to-video", "speech"]
    filtered = []

    for m in raw_models:
        mid = m.get("id", "")
        mid_lower = mid.lower()
        if any(ex in mid_lower for ex in exclude_keywords):
            continue
        if any(k in mid_lower for k in keywords):
            vendor = "其他生图模型"
            display_name = mid
            badge = ""
            desc = "通用高精度扩散生成模型"

            if "kling" in mid_lower:
                vendor = "快手可灵 (Kling AI)"
                if "o3" in mid_lower or mid_lower == "klingai":
                    display_name = "快手可灵 O3 (Kling Image O3)"
                    badge = "旗舰首选"
                    desc = "最新 O3 神经扩散，支持 4K 超清与 1~10 张参考图融合"
                elif "o1" in mid_lower:
                    display_name = "可灵 Image O1"
                    badge = "多模态"
                    desc = "全能型多模态图生图模型"
                elif "v3" in mid_lower:
                    display_name = "可灵 Omni v3"
                    badge = "全能版"
                    desc = "全场景影视级多模态输出"
                elif "v2" in mid_lower:
                    display_name = f"可灵 {mid}"
                    badge = "V2 经典"
                    desc = "经典构图与多画幅生成模型"
                else:
                    display_name = f"可灵 {mid}"
                    desc = "可灵系列图像生成"
            elif "flux" in mid_lower:
                vendor = "Black Forest (Flux)"
                display_name = f"Flux.1 {mid.replace('flux-', '').upper() if 'flux-' in mid else mid.upper()}"
                badge = "开源顶尖"
                desc = "120 亿参数扩散模型，极强文字排印与自然写实质感"
            elif "midjourney" in mid_lower:
                vendor = "Midjourney"
                display_name = "Midjourney v6.1"
                badge = "艺术美学"
                desc = "好莱坞电影与概念设计级艺术审美"
            elif "dall" in mid_lower:
                vendor = "OpenAI"
                display_name = "DALL-E 3"
                badge = "语义遵循"
                desc = "极佳复杂自然语言理解与构图还原"
            elif "ideogram" in mid_lower:
                vendor = "Ideogram"
                display_name = "Ideogram v2"
                badge = "排版设计"
                desc = "海报设计、标志与图文混合生成排版专家"
            elif "recraft" in mid_lower:
                vendor = "Recraft"
                display_name = "Recraft v3"
                badge = "商用矢量"
                desc = "专业设计级矢量图、3D Icon 与商用视觉"
            elif "minimax" in mid_lower:
                vendor = "MiniMax"
                display_name = "MiniMax Image-01"
                badge = "写实人像"
                desc = "高逼真东方人像与精细场景写实渲染"
            elif "cogview" in mid_lower:
                vendor = "智谱 AI (Zhipu)"
                display_name = "CogView-4"
                badge = "东方美学"
                desc = "中英文双语高精度概念美学生成"

            filtered.append({
                "id": mid,
                "name": display_name,
                "vendor": vendor,
                "badge": badge,
                "description": desc,
                "is_kling": "kling" in mid_lower,
                "is_default": mid_lower in ["klingai", "kling-image-o3"]
            })

    # 保底补全可灵 O3
    if not any(m["id"] == "klingai" for m in filtered):
        filtered.insert(0, {
            "id": "klingai",
            "name": "快手可灵 O3 (Kling Image O3)",
            "vendor": "快手可灵 (Kling AI)",
            "badge": "旗舰首选",
            "description": "最新 O3 神经扩散，支持 4K 超清与 1~10 张参考图融合",
            "is_kling": True,
            "is_default": True
        })
    else:
        # 置顶 klingai
        filtered.sort(key=lambda x: (0 if x["id"] == "klingai" else (1 if x["is_kling"] else 2)))

    _CACHED_MODELS = filtered
    _LAST_MODELS_FETCH_TIME = now
    return filtered


# ================= REST API 路由 =================

@app.get("/api/models")
def list_302_models(refresh: bool = False):
    """
    动态拉取 302.ai 支持的所有生图模型列表
    """
    models = fetch_302_models(kling_client.api_key, kling_client.current_base_url, force_refresh=refresh)
    vendors = list(dict.fromkeys([m["vendor"] for m in models]))
    return {
        "code": 200,
        "msg": "获取模型列表成功",
        "data": models,
        "total": len(models),
        "vendors": vendors,
        "current_active": "klingai"
    }

@app.get("/api/system/info")
def get_system_info():
    """获取系统与大模型链路状态"""
    masked_key = kling_client.api_key[:6] + "******" + kling_client.api_key[-4:] if len(kling_client.api_key) > 10 else "***"
    return {
        "code": 200,
        "msg": "系统正常",
        "data": {
            "model": "kling-image-o3",
            "model_name": "快手可灵图片 O3 (Kling Image O3)",
            "provider": "302.ai",
            "base_url": kling_client.current_base_url,
            "api_key_masked": masked_key,
            "status": "online"
        }
    }


@app.post("/api/system/config")
def update_system_config(req: UpdateConfigRequest):
    """动态更新 API Key 或服务地址"""
    if req.api_key and req.api_key.strip():
        kling_client.api_key = req.api_key.strip()
        kling_client.session.headers.update({"Authorization": f"Bearer {kling_client.api_key}"})
    if req.base_url and req.base_url.strip():
        url = req.base_url.strip().rstrip("/")
        kling_client.base_urls = [url]
        kling_client.current_base_url = url
    return {"code": 200, "msg": "配置已更新", "data": get_system_info()["data"]}


@app.post("/api/image/generate")
def generate_image(req: GenerateImageRequest):
    """
    提交 AI 生图任务到可灵 O3
    """
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="生图提示词不能为空")

    # 如果传入了自定义 key
    client = KlingImageO3Client(api_key=req.api_key) if req.api_key else kling_client

    try:
        task_id = client.submit_task(
            prompt=req.prompt,
            images=req.reference_images,
            aspect_ratio=req.aspect_ratio,
            img_resolution=req.img_resolution,
            image_count=req.image_count,
            story_mode=req.story_mode
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交可灵任务失败: {str(e)}")

    # 模型名称映射
    model_id = req.model_id or "klingai"
    all_models = fetch_302_models(client.api_key, client.current_base_url)
    model_info = next((m for m in all_models if m["id"] == model_id), None)
    model_name = model_info["name"] if model_info else model_id

    # 存入本地任务数据库
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    new_task = {
        "task_id": task_id,
        "prompt": req.prompt,
        "model_id": model_id,
        "model_name": model_name,
        "reference_images": req.reference_images or [],
        "aspect_ratio": req.aspect_ratio,
        "img_resolution": req.img_resolution,
        "image_count": req.image_count,
        "story_mode": req.story_mode,
        "task_status": "submitted",
        "status_msg": "任务已提交至计算集群，排队处理中...",
        "result_images": [],
        "cost_time": 0,
        "create_time": now,
        "start_timestamp": time.time()
    }

    tasks = load_tasks()
    tasks.insert(0, new_task)
    save_tasks(tasks)

    return {
        "code": 200,
        "msg": "任务提交成功",
        "data": {
            "task_id": task_id
        }
    }


@app.get("/api/image/task/{task_id}")
def get_task_status(task_id: str):
    """
    轮询/获取生图任务最新状态与结果图片
    """
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"未找到任务: {task_id}")

    # 如果任务在本地已经是完成状态，直接返回
    if task.get("task_status") in ["succeed", "failed"]:
        return {"code": 200, "data": task}

    # 主动向 302.ai 轮询一次实时状态
    try:
        res = kling_client.fetch_task_result(task_id)
        status = res.get("status")
        status_msg = res.get("msg") or ""

        # 成功完成
        if status == "succeed":
            image_urls = res.get("images", [])
            cost_time = int((time.time() - task.get("start_timestamp", time.time())) * 1000)

            updated = update_task_record(task_id, {
                "task_status": "succeed",
                "status_msg": "生成成功",
                "result_images": image_urls,
                "cost_time": cost_time
            })
            return {"code": 200, "data": updated}

        # 任务失败
        elif status == "failed":
            updated = update_task_record(task_id, {
                "task_status": "failed",
                "status_msg": status_msg or "模型渲染失败"
            })
            return {"code": 200, "data": updated}

        # 处理中
        else:
            updated = update_task_record(task_id, {
                "task_status": "processing",
                "status_msg": status_msg or "可灵 O3 神经扩散渲染中..."
            })
            return {"code": 200, "data": updated}

    except Exception as e:
        task["status_msg"] = f"正在轮询: {str(e)}"
        return {"code": 200, "data": task}

    return {"code": 200, "data": task}


@app.get("/api/image/tasks")
def list_tasks(
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=12, alias="pageSize"),
    prompt: Optional[str] = Query(default=None)
):
    """
    分页查询历史生图任务列表
    """
    all_tasks = load_tasks()
    if prompt and prompt.strip():
        all_tasks = [t for t in all_tasks if prompt.strip().lower() in t.get("prompt", "").lower()]

    total = len(all_tasks)
    start = (page_num - 1) * page_size
    end = start + page_size
    rows = all_tasks[start:end]

    return {
        "code": 200,
        "total": total,
        "rows": rows,
        "data": rows
    }


@app.delete("/api/image/task/{task_id}")
def delete_task(task_id: str):
    """
    删除指定的任务记录
    """
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["task_id"] != task_id]
    if len(new_tasks) == len(tasks):
        raise HTTPException(status_code=404, detail="任务不存在")
    save_tasks(new_tasks)
    return {"code": 200, "msg": "删除成功"}


@app.post("/api/image/upload-reference")
async def upload_reference_image(file: UploadFile = File(...)):
    """
    上传本地参考图，暂存并同步上传至 302.ai 云图床，返回公网可用 URL
    """
    if not file:
        raise HTTPException(status_code=400, detail="未检测到上传文件")

    ext = Path(file.filename).suffix
    unique_name = f"ref_{uuid.uuid4().hex[:12]}{ext}"
    local_path = UPLOAD_DIR / unique_name

    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 同步上传到 302.ai 获取远程图床 URL
        remote_url = kling_client.upload_local_image(str(local_path))
        return {
            "code": 200,
            "msg": "参考图上传并同步成功",
            "url": remote_url,
            "local_path": str(local_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传参考图至302图床失败: {str(e)}")


# 挂载前端静态文件目录
FRONTEND_DIR = PROJECT_ROOT / "ruoyi-ai-workbench"
if (FRONTEND_DIR / "dist").exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR / "dist"), html=True), name="frontend")
elif (FRONTEND_DIR / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
