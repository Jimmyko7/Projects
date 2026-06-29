"""
session_manager.py — 会话持久化管理

职责：聊天会话 JSON 文件的 CRUD 操作
"""

import os
import json
from datetime import datetime
from pathlib import Path


def generate_name() -> str:
    """生成时间戳会话名"""
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def list_all(session_dir: Path) -> list[str]:
    """列出所有会话名（按时间倒序）"""
    sessions = []
    if os.path.exists(str(session_dir)):
        for fn in os.listdir(str(session_dir)):
            if fn.endswith(".json"):
                sessions.append(fn[:-5])
    sessions.sort(reverse=True)
    return sessions


def save(data: dict, session_dir: Path) -> None:
    """保存会话到 JSON 文件"""
    name = data.get("current_session", generate_name())
    os.makedirs(str(session_dir), exist_ok=True)
    path = str(session_dir / f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load(name: str, session_dir: Path) -> dict | None:
    """加载指定会话"""
    path = str(session_dir / f"{name}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def delete(name: str, session_dir: Path) -> bool:
    """删除指定会话"""
    path = str(session_dir / f"{name}.json")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
