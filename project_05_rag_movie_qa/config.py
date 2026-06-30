"""
config.py — 全局配置常量
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"
SESSION_DIR = BASE_DIR / "sessions"
DATA_DIR = BASE_DIR.parent / "data"

COLLECTION_NAME = "tmdb_movies"
EMBEDDING_MODEL = "text-embedding-v4"
RETRIEVAL_K = 5
RANKING_K = 10  # 排序/极值类查询时的检索数量        # 检索召回

DEFAULT_NICK = "小新"
DEFAULT_CHARACTER = "人小鬼大"

LLM_MODEL = "deepseek-chat"
LLM_BASE_URL = "https://api.deepseek.com"
