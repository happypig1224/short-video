"""
数据库与持久化模块 (SQLite + init.sql)
提供用户表与生图资产表的多租户隔离操作与安全鉴权辅助
"""

import os
import json
import sqlite3
import datetime
import bcrypt
import jwt
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "workbench.db"
INIT_SQL_PATH = PROJECT_ROOT / "init.sql"

JWT_SECRET = os.getenv("JWT_SECRET", "ruoyi_ai_workbench_secret_key_2026_super_secure")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7

DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_db_connection():
    """获取 SQLite 数据库连接并开启行模式"""
    conn = sqlite3.connect(str(DB_PATH), timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn


def init_db():
    """初始化数据库表结构与默认管理员记录"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if INIT_SQL_PATH.exists():
            with open(INIT_SQL_PATH, "r", encoding="utf-8") as f:
                sql_script = f.read()
            cursor.executescript(sql_script)
        else:
            # 基础建表兜底
            cursor.execute("""
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
            """)
            cursor.execute("""
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
            """)
            # 确保 admin 用户存在
            cursor.execute("SELECT id FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                admin_hash = hash_password("admin123！@")
                cursor.execute(
                    "INSERT INTO users (username, password, nickname, role, status, credits) VALUES (?, ?, ?, ?, ?, ?)",
                    ("admin", admin_hash, "系统管理员", "admin", 1, 9999)
                )
        conn.commit()
    finally:
        conn.close()


# ================= 密码与 Token 处理 =================

def hash_password(plain_password: str) -> str:
    """生成 bcrypt 密码哈希"""
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验密码是否匹配
    容错支持全角叹号 'admin123！@' 与半角叹号 'admin123!@'
    """
    if not plain_password or not hashed_password:
        return False

    candidates = [plain_password]
    if "！" in plain_password:
        candidates.append(plain_password.replace("！", "!"))
    if "!" in plain_password:
        candidates.append(plain_password.replace("!", "！"))

    for cand in candidates:
        try:
            if bcrypt.checkpw(cand.encode("utf-8"), hashed_password.encode("utf-8")):
                return True
        except Exception:
            pass
        if cand == hashed_password:
            return True

    return False


def create_access_token(user_id: int, username: str, role: str) -> str:
    """签发 JWT Access Token"""
    expire = datetime.datetime.utcnow() + datetime.timedelta(days=JWT_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """解码并验证 JWT Token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


# ================= 用户相关查询 =================

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def deduct_user_credits(user_id: int, amount: int = 1) -> bool:
    """扣减用户积分"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT credits FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not row or row["credits"] < amount:
            return False
        cursor.execute("UPDATE users SET credits = credits - ? WHERE id = ?", (amount, user_id))
        conn.commit()
        return True
    finally:
        conn.close()


# ================= 资产与生图任务操作（严格用户隔离） =================

def insert_task(user_id: int, task: Dict[str, Any]) -> Dict[str, Any]:
    """插入新任务记录并关联 user_id"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ref_images_json = json.dumps(task.get("reference_images", []), ensure_ascii=False)
        result_images_json = json.dumps(task.get("result_images", []), ensure_ascii=False)

        cursor.execute("""
        INSERT INTO image_assets (
            task_id, user_id, prompt, negative_prompt, model_id, model_name,
            aspect_ratio, img_resolution, image_count, story_mode,
            reference_images, task_status, status_msg, result_images,
            cost_time, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task["task_id"],
            user_id,
            task.get("prompt", ""),
            task.get("negative_prompt", ""),
            task.get("model_id", "klingai"),
            task.get("model_name", "快手可灵 O3"),
            task.get("aspect_ratio", "1:1"),
            task.get("img_resolution", "2k"),
            task.get("image_count", 1),
            1 if task.get("story_mode") else 0,
            ref_images_json,
            task.get("task_status", "submitted"),
            task.get("status_msg", "任务已提交"),
            result_images_json,
            task.get("cost_time", 0),
            now,
            now
        ))
        conn.commit()
        return get_task_by_id(task["task_id"], user_id=user_id)
    finally:
        conn.close()


def get_task_by_id(task_id: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """查询单条生图任务记录（如果传入 user_id 则做权限匹配）"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute("SELECT * FROM image_assets WHERE task_id = ? AND user_id = ?", (task_id, user_id))
        else:
            cursor.execute("SELECT * FROM image_assets WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return format_task_row(dict(row))
    finally:
        conn.close()


def update_task_record(task_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """更新任务状态及生成结果"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        fields = []
        values = []
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for k, v in updates.items():
            if k in ["task_status", "status_msg", "cost_time", "model_id", "model_name"]:
                fields.append(f"{k} = ?")
                values.append(v)
            elif k in ["result_images", "reference_images"]:
                fields.append(f"{k} = ?")
                values.append(json.dumps(v, ensure_ascii=False) if isinstance(v, list) else str(v))

        fields.append("updated_at = ?")
        values.append(now)
        values.append(task_id)

        sql = f"UPDATE image_assets SET {', '.join(fields)} WHERE task_id = ?"
        cursor.execute(sql, tuple(values))
        conn.commit()
        return get_task_by_id(task_id)
    finally:
        conn.close()


def list_user_tasks(
    user_id: int,
    prompt: Optional[str] = None,
    page_num: int = 1,
    page_size: int = 12
) -> Tuple[List[Dict[str, Any]], int]:
    """分页查询指定用户下的历史生图资产记录"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        where_clause = "WHERE user_id = ?"
        params: List[Any] = [user_id]

        if prompt and prompt.strip():
            where_clause += " AND prompt LIKE ?"
            params.append(f"%{prompt.strip()}%")

        cursor.execute(f"SELECT COUNT(*) FROM image_assets {where_clause}", tuple(params))
        total = cursor.fetchone()[0]

        offset = (page_num - 1) * page_size
        params.extend([page_size, offset])

        cursor.execute(f"""
        SELECT * FROM image_assets {where_clause}
        ORDER BY id DESC
        LIMIT ? OFFSET ?
        """, tuple(params))

        rows = cursor.fetchall()
        result = [format_task_row(dict(r)) for r in rows]
        return result, total
    finally:
        conn.close()


def delete_user_task(task_id: str, user_id: int) -> bool:
    """删除指定用户的生图资产记录"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM image_assets WHERE task_id = ? AND user_id = ?", (task_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def format_task_row(row: Dict[str, Any]) -> Dict[str, Any]:
    """将数据库行对象转换为 API 响应格式（还原 JSON 字段）"""
    res = dict(row)
    # 格式化 reference_images
    if isinstance(res.get("reference_images"), str):
        try:
            res["reference_images"] = json.loads(res["reference_images"])
        except Exception:
            res["reference_images"] = []
    # 格式化 result_images
    if isinstance(res.get("result_images"), str):
        try:
            res["result_images"] = json.loads(res["result_images"])
        except Exception:
            res["result_images"] = []
    
    # 兼容前端属性名称
    res["create_time"] = res.get("created_at", "")
    return res

