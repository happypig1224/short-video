"""
One-click Launcher for Enterprise AI Video Workbench & Human Review Studio.
Starts FastAPI backend server and launches browser automatically.
"""

import sys
import os
import time
import webbrowser
import threading
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import uvicorn


def open_browser():
    time.sleep(1.2)
    print("\n[Studio Ready] 正在自动为您打开编导人工审核可视化中台...")
    webbrowser.open("http://127.0.0.1:8000")


def main():
    print("""
========================================================================
   🎬 企业级 AI 短视频制作与编导人工审核可视化中台 (Phase 1 Studio)
========================================================================
   - 服务端口: http://127.0.0.1:8000
   - 核心功能:
     * F-01 智能分镜时序编排 (Gemini 3.8 Flash)
     * F-02 2x2 起止双关键帧对比决策 (GPT-Image 2.6)
     * F-03 透光台叠影 (Onion Skinning) 空间对齐检查
     * F-03 HTML5 Canvas 瑕疵画笔涂抹局部打回 (Inpainting)
     * F-04 首尾帧插值视频渲染 (Kling I2V)
     * F-05 302.AI 账户余额与 120% 事前算力熔断防线
========================================================================
    """)
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("workbench.web.server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
