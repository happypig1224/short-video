-- 若依 AI 生图工作台 数据库初始化脚本
-- 包含用户表与生图资产表

-- 1. 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(64) DEFAULT '系统管理员',
    avatar VARCHAR(255) DEFAULT '',
    role VARCHAR(32) DEFAULT 'admin',
    status INTEGER DEFAULT 1,
    credits INTEGER DEFAULT 9999,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 创建生图资产表（与用户强关联）
CREATE TABLE IF NOT EXISTS image_assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id VARCHAR(64) NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    negative_prompt TEXT DEFAULT '',
    model_id VARCHAR(64) DEFAULT 'klingai',
    model_name VARCHAR(128) DEFAULT '快手可灵 O3',
    aspect_ratio VARCHAR(16) DEFAULT '1:1',
    img_resolution VARCHAR(16) DEFAULT '2k',
    image_count INTEGER DEFAULT 1,
    story_mode BOOLEAN DEFAULT 0,
    reference_images TEXT DEFAULT '[]',
    task_status VARCHAR(32) DEFAULT 'submitted',
    status_msg TEXT DEFAULT '',
    result_images TEXT DEFAULT '[]',
    cost_time INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_image_assets_user_id ON image_assets(user_id);
CREATE INDEX IF NOT EXISTS idx_image_assets_task_id ON image_assets(task_id);

-- 3. 仅插入一条初始管理员记录：用户名 admin，密码 admin123！@
INSERT OR IGNORE INTO users (id, username, password, nickname, avatar, role, status, credits)
VALUES (
    1,
    'admin',
    '$2b$12$FBoB4vX/Kx3ZrVHGci6ateXbMLfHw5.ajBNB/XdoEE1q0e27I6aC2',
    '系统管理员',
    'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
    'admin',
    1,
    9999
);

