"""session_manager.py — 聊天会话 JSON 持久化"""

import os, json
from datetime import datetime
from pathlib import Path


def generate_name() -> str:
    return datetime.now().strftime("%Y-%m-%d %H-%M-%S")


def list_all(d: Path) -> list[str]:
    if not os.path.exists(str(d)): return []
    s = [f[:-5] for f in os.listdir(str(d)) if f.endswith(".json")]
    s.sort(reverse=True); return s


def save(data: dict, d: Path) -> None:
    os.makedirs(str(d), exist_ok=True)
    with open(str(d / f"{data.get('current_session', generate_name())}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load(name: str, d: Path) -> dict | None:
    p = str(d / f"{name}.json")
    if not os.path.exists(p): return None
    try:
        with open(p, "r", encoding="utf-8") as f: return json.load(f)
    except Exception: return None


def remove(name: str, d: Path) -> bool:
    p = str(d / f"{name}.json")
    if os.path.exists(p): os.remove(p); return True
    return False
