"""
一键启动脚本: 若依风格 AI 生图工作台 (RuoYi AI Workbench)
同时启动 FastAPI 后端服务与 RuoYi-Vue 前端界面，并在浏览器中自动打开
"""

import os
import sys
import time
import webbrowser
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn


def open_browser():
    time.sleep(1.2)
    print("\n[Browser] 正在为您自动打开若依 AI 可灵生图工作台...")
    webbrowser.open("http://127.0.0.1:8000")


def main():
    print("""
========================================================================
   🎨 若依风格 AI 生图工作台 (RuoYi AI Image Workbench)
   核心引擎: 快手可灵图片 O3 (Kling Image O3) x 302.ai API
========================================================================
   - 前后端一体化访问地址: http://127.0.0.1:8000
   - 核心功能特性:
     * 1. 若依经典控制台 (经典深蓝侧边栏 + 顶部导航 + 面包屑)
     * 2. 多模态生图 (纯文生图 / 参考图生图，支持 1-10 张图片)
     * 3. 本地图片自动同步上传至 302.ai 云图床
     * 4. 画面尺寸自由定制 (1:1, 16:9, 9:16, 4:3, 3:4, 3:2, 2:3, auto)
     * 5. 画质分辨率选择 (1K / 2K / 4K) 与生成张数 (1-4)
     * 6. 异步实时状态轮询 + 呼吸动效进度反馈
     * 7. 成果大图预览、一键下载、链接复制、参数回填复用
     * 8. 本地轻量化任务持久化画廊 (data/tasks.json)
========================================================================
    """)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("server.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
