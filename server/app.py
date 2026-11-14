"""
FastAPI 后端服务: 桥接 302.ai 可灵 O3 生图脚本 (generate_kling_image_o3.py)
整合 SQLite 用户认证鉴权体系、全接口强制拦截、用户资产隔离与持久化
"""

import os
import sys
import time
import json
import uuid
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.generate_kling_image_o3 import KlingImageO3Client, DEFAULT_API_KEY, DEFAULT_BASE_URLS
from server.db import (
    init_db,
    get_user_by_username,
    get_user_by_id,
    verify_password,
    create_access_token,
    decode_access_token,
    insert_task,
    get_task_by_id,
    update_task_record,
    list_user_tasks,
    delete_user_task,
    deduct_user_credits
)
from server.moderation import check_prompt_safety

# 初始化数据库与默认管理员
init_db()

# 数据存储目录
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
OUTPUT_DIR = DATA_DIR / "outputs"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 初始化生图核心客户端
kling_client = KlingImageO3Client()

app = FastAPI(
    title="RuoYi AI Image Workbench API",
    description="若依风格 AI 生图工作台企业级后端接口（集成 JWT 登录鉴权与用户数据隔离）",
    version="2.0.0"
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================= 鉴权依赖项与强制拦截 =================
security = HTTPBearer(auto_error=False)


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """
    核心用户鉴权依赖:
    强制拦截未携带有效 Bearer Token 的请求，校验用户有效性并返回用户信息
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或缺少身份令牌，请先登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录凭证已失效或无效，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_id(payload["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.get("status") != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该账号已被停用，请联系管理员",
        )
    return user


# 全局中间件：强制拦截所有 /api/* 请求（白名单除外）
PUBLIC_API_PATHS = {
    "/api/auth/login",
    "/api/health",
    "/docs",
    "/openapi.json",
    "/redoc"
}


@app.middleware("http")
async def auth_interceptor_middleware(request: Request, call_next):
    path = request.url.path

    # 非 /api 路径（如静态资源、HTML等）直接放行
    if not path.startswith("/api"):
        return await call_next(request)

    # 检查公开接口白名单
    if path in PUBLIC_API_PATHS:
        return await call_next(request)

    # 拦截 OPTIONS 预检请求（浏览器 CORS 预检放行）
    if request.method == "OPTIONS":
        return await call_next(request)

    # 针对受保护的 /api 请求执行 Token 强制校验
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "code": 401,
                "msg": "未登录或登录已失效，请重新登录",
                "detail": "Missing or invalid Authorization header"
            }
        )

    token = auth_header.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "code": 401,
                "msg": "登录令牌已过期或无效，请重新登录",
                "detail": "Invalid JWT token"
            }
        )

    # 注入当前用户ID到 request.state
    request.state.user_id = payload["user_id"]
    return await call_next(request)


# ================= 请求与响应模型 =================
class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


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


# ================= 动态模型缓存 =================
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
        filtered.sort(key=lambda x: (0 if x["id"] == "klingai" else (1 if x["is_kling"] else 2)))

    _CACHED_MODELS = filtered
    _LAST_MODELS_FETCH_TIME = now
    return filtered


# ================= 用户登录认证路由 =================

@app.post("/api/auth/login")
def login(req: LoginRequest):
    """
    用户登录认证接口
    校验用户名密码并签发 JWT Access Token
    """
    username = req.username.strip() if req.username else ""
    password = req.password.strip() if req.password else ""

    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")

    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.get("status") != 1:
        raise HTTPException(status_code=403, detail="账号已被停用，请联系管理员")

    token = create_access_token(user["id"], user["username"], user["role"])

    user_info = {
        "id": user["id"],
        "username": user["username"],
        "nickname": user["nickname"],
        "avatar": user["avatar"],
        "role": user["role"],
        "credits": user["credits"]
    }

    return {
        "code": 200,
        "msg": "登录成功",
        "data": {
            "token": token,
            "user": user_info
        }
    }


@app.get("/api/auth/me")
def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    """获取当前已登录用户信息及剩余算力"""
    fresh_user = get_user_by_id(user["id"]) or user
    return {
        "code": 200,
        "msg": "获取用户信息成功",
        "data": {
            "id": fresh_user["id"],
            "username": fresh_user["username"],
            "nickname": fresh_user["nickname"],
            "avatar": fresh_user["avatar"],
            "role": fresh_user["role"],
            "credits": fresh_user["credits"]
        }
    }


@app.post("/api/auth/logout")
def logout(user: Dict[str, Any] = Depends(get_current_user)):
    """退出登录"""
    return {"code": 200, "msg": "退出成功"}


@app.get("/api/health")
def health_check():
    """健康探测"""
    return {"code": 200, "status": "healthy"}


# ================= 业务 API 路由（强依赖用户认证与资产关联） =================

@app.get("/api/models")
def list_302_models(refresh: bool = False, user: Dict[str, Any] = Depends(get_current_user)):
    """
    动态拉取 302.ai 支持的所有生图模型列表（需要登录）
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
def get_system_info(user: Dict[str, Any] = Depends(get_current_user)):
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
def update_system_config(req: UpdateConfigRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """动态更新 API Key 或服务地址（仅管理员）"""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="仅系统管理员有权修改系统配置")

    if req.api_key and req.api_key.strip():
        kling_client.api_key = req.api_key.strip()
        kling_client.session.headers.update({"Authorization": f"Bearer {kling_client.api_key}"})
    if req.base_url and req.base_url.strip():
        url = req.base_url.strip().rstrip("/")
        kling_client.base_urls = [url]
        kling_client.current_base_url = url
    return {"code": 200, "msg": "配置已更新", "data": get_system_info(user=user)["data"]}


@app.post("/api/image/generate")
def generate_image(req: GenerateImageRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """
    提交 AI 生图任务到可灵 O3 并沉淀资产至数据库（与当前用户强关联）
    """
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="生图提示词不能为空")

    # 生产合规审查：敏感词与内容安全策略熔断
    is_safe, reason, hit_words = check_prompt_safety(req.prompt)
    if not is_safe:
        raise HTTPException(status_code=400, detail=reason)

    # 校验算力积分
    if user.get("credits", 0) <= 0:
        raise HTTPException(status_code=400, detail="您的算力余额不足，请联系管理员充值")

    # 扣除积分
    deduct_user_credits(user["id"], amount=1)

    # 提交给底层生图客户端
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

    # 存入数据库并与当前用户 user_id 关联
    task_record = {
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
        "cost_time": 0
    }

    inserted = insert_task(user_id=user["id"], task=task_record)

    return {
        "code": 200,
        "msg": "任务提交成功",
        "data": {
            "task_id": task_id,
            "task": inserted
        }
    }


@app.get("/api/image/task/{task_id}")
def get_task_status_endpoint(task_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """
    轮询/获取生图任务最新状态与结果图片（只允许查询属于当前用户的任务）
    """
    task = get_task_by_id(task_id, user_id=user["id"] if user.get("role") != "admin" else None)
    if not task:
        raise HTTPException(status_code=404, detail=f"未找到属于该用户的任务: {task_id}")

    # 如果任务在本地数据库已经是最终完成状态，直接返回
    if task.get("task_status") in ["succeed", "failed"]:
        return {"code": 200, "data": task}

    # 主动向 302.ai 轮询一次实时状态
    try:
        res = kling_client.fetch_task_result(task_id)
        status_val = res.get("status")
        status_msg = res.get("msg") or ""

        # 成功完成
        if status_val == "succeed":
            image_urls = res.get("images", [])
            updated = update_task_record(task_id, {
                "task_status": "succeed",
                "status_msg": "生成成功",
                "result_images": image_urls
            })
            return {"code": 200, "data": updated}

        # 任务失败
        elif status_val == "failed":
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


@app.get("/api/image/tasks")
def list_tasks_endpoint(
    page_num: int = Query(default=1, alias="pageNum"),
    page_size: int = Query(default=12, alias="pageSize"),
    prompt: Optional[str] = Query(default=None),
    user: Dict[str, Any] = Depends(get_current_user)
):
    """
    分页查询当前用户的生图资产列表（严格多租户数据隔离）
    """
    rows, total = list_user_tasks(
        user_id=user["id"],
        prompt=prompt,
        page_num=page_num,
        page_size=page_size
    )

    return {
        "code": 200,
        "total": total,
        "rows": rows,
        "data": rows
    }


@app.delete("/api/image/task/{task_id}")
def delete_task_endpoint(task_id: str, user: Dict[str, Any] = Depends(get_current_user)):
    """
    删除指定的任务资产记录（必须属于当前用户）
    """
    success = delete_user_task(task_id=task_id, user_id=user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在或无权删除")
    return {"code": 200, "msg": "删除成功"}


@app.post("/api/image/upload-reference")
async def upload_reference_image(file: UploadFile = File(...), user: Dict[str, Any] = Depends(get_current_user)):
    """
    上传本地参考图，暂存并同步上传至 302.ai 云图床，返回公网可用 URL
    """
    if not file:
        raise HTTPException(status_code=400, detail="未检测到上传文件")

    ext = Path(file.filename).suffix
    unique_name = f"ref_{user['id']}_{uuid.uuid4().hex[:10]}{ext}"
    local_path = UPLOAD_DIR / unique_name

    with open(local_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        remote_url = kling_client.upload_local_image(str(local_path))
        return {
            "code": 200,
            "msg": "参考图上传并同步成功",
            "url": remote_url,
            "file_url": remote_url,
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
