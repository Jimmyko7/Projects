"""config.py — AI 伴侣配置常量"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SESSION_DIR = BASE_DIR / "sessions"
DEFAULT_NICK = "小新"
DEFAULT_CHARACTER = "人小鬼大"
LLM_MODEL = "deepseek-chat"
LLM_BASE_URL = "https://api.deepseek.com"
