# ==========================================
# 生产级 Dockerfile: 若依 AI 生图工作台
# Multi-Stage Build: Python 3.11 Runtime
# ==========================================

FROM python:3.11-slim

# 设置工作目录与生产环境变量
WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai

# 安装系统级依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖配置并安装 Python 依赖
COPY .env.example .env.example
RUN pip install --no-cache-dir --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    fastapi \
    uvicorn[standard] \
    pydantic \
    python-multipart \
    requests \
    bcrypt \
    pyjwt \
    cryptography

# 复制项目核心代码
COPY scripts/ /app/scripts/
COPY server/ /app/server/
COPY init.sql /app/init.sql
COPY ruoyi-ai-workbench/dist/ /app/ruoyi-ai-workbench/dist/

# 创建持久化数据目录
RUN mkdir -p /app/data/uploads /app/data/outputs

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/api/health || exit 1

# 生产级启动指令 (4 进程工作池)
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
