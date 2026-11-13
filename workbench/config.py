"""
Configuration and pricing parameters for AI Video Workbench Phase 1.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 302.AI 接口配置
    API_KEY: str = os.getenv("API_KEY_302", "sk-live-default-placeholder")
    BASE_URL: str = os.getenv("API_BASE_URL_302", "https://api.302.ai")

    # 默认模型选型
    LLM_MODEL: str = "gemini-3.8-flash"
    IMAGE_MODEL: str = "gpt-image-2.6-sunburst"
    INPAINT_MODEL: str = "gpt-image-2.6-sunburst"
    VIDEO_MODEL: str = "kling-v1-6"

    # FinOps 单位经济基准价格 (USD)
    COST_LLM_PER_SHOT: float = 0.0003
    COST_IMAGE_PER_FRAME: float = 0.02228
    COST_INPAINT_PER_FRAME: float = 0.02228
    COST_VIDEO_PER_SHOT: float = 0.1890

    # 熔断安全边际 (120%)
    FINOPS_BUFFER_RATIO: float = 1.20

    # 重试与防沉迷限制
    MAX_INPAINT_RETRIES_PER_SHOT: int = 3
    MAX_SHOTS_PER_PROJECT: int = 30
    DEFAULT_DURATION_SECONDS: int = 5

    # 视频生成轮询参数
    POLL_INTERVAL_SECONDS: float = 2.0
    POLL_MAX_ATTEMPTS: int = 60

settings = Settings()
