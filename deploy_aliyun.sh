#!/usr/bin/env bash
# ==============================================================================
# 阿里云轻量应用服务器 (Ubuntu 24.04 / 1GB RAM) 生产环境一键极速部署脚本
# 适用服务: 若依 AI 生图工作台 (RuoYi AI Workbench)
# ==============================================================================

set -e

echo "=========================================================================="
echo "🚀 开始在阿里云轻量服务器部署 若依 AI 生图工作台 (RuoYi AI Workbench)..."
echo "=========================================================================="

# 1. 针对 1GB 内存服务器优化：配置 2GB Swap 虚拟内存 (防止 OOM 内存溢出)
if [ ! -f /swapfile ]; then
    echo "[1/6] 正在为 1GB 内存服务器创建 2GB Swap 交换分区..."
    fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "Swap 创建成功，当前内存状态："
    free -h
else
    echo "[1/6] Swap 交换分区已存在，跳过创建。"
fi

# 2. 安装基础运行依赖
echo "[2/6] 正在更新系统软件源并安装基础环境 (Python 3.12/Git/SQLite3)..."
apt-get update -y
apt-get install -y python3 python3-pip python3-venv git curl sqlite3

# 3. 拉取最新生产代码
INSTALL_DIR="/opt/short-video"
echo "[3/6] 正在部署项目代码至 $INSTALL_DIR ..."

if [ -d "$INSTALL_DIR" ]; then
    echo "检测到已有代码库，执行 git pull 拉取最新提交..."
    cd "$INSTALL_DIR"
    git reset --hard HEAD
    git pull origin main
else
    git clone https://github.com/happypig1224/short-video.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 4. 创建隔离虚拟环境并安装核心依赖
echo "[4/6] 正在创建 Python 生产虚拟环境并安装依赖..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn pydantic python-multipart requests bcrypt pyjwt cryptography

# 5. 初始化配置与数据库
echo "[5/6] 正在初始化生产环境变量与数据库..."
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# 运行数据库初始化
python3 -c "from server.db import init_db; init_db(); print('数据库 (workbench.db) 初始化成功！')"

# 6. 配置 Systemd 守护进程 (开机自启、奔溃自动重启)
echo "[6/6] 正在配置 Systemd 系统守护进程..."
cat << 'EOF' > /etc/systemd/system/ruoyi-workbench.service
[Unit]
Description=RuoYi AI Workbench Production Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/short-video
Environment="PYTHONUNBUFFERED=1"
Environment="PATH=/opt/short-video/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/short-video/venv/bin/uvicorn server.app:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ruoyi-workbench
systemctl restart ruoyi-workbench

echo "=========================================================================="
echo "🎉 部署完成！正在检查服务健康状态..."
sleep 3

if curl -s http://127.0.0.1:8000/api/health | grep -q "healthy"; then
    echo "✅ 服务已成功运行！健康检查探测通过！"
else
    echo "⚠️ 正在启动中，请使用 systemctl status ruoyi-workbench 查看状态。"
fi

echo "=========================================================================="
echo "🌐 访问地址: http://$(curl -s ifconfig.me):8000"
echo "📌 重要提醒: 请务必在阿里云控制台【防火墙】标签页中添加开放 TCP 8000 端口！"
echo "🔑 初始账号: admin  /  初始密码: admin123！@"
echo "=========================================================================="
