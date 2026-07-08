"""database.py — SQLite 数据库连接与初始化（v2.1：WAL 模式 + 线程连接复用）"""

import sqlite3
import threading
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "student.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL UNIQUE,
    chinese  INTEGER NOT NULL CHECK(chinese  BETWEEN 0 AND 100),
    math     INTEGER NOT NULL CHECK(math     BETWEEN 0 AND 100),
    english  INTEGER NOT NULL CHECK(english  BETWEEN 0 AND 100)
);
"""

# 线程局部存储：每个线程复用同一个 SQLite 连接
_local = threading.local()


def get_connection() -> sqlite3.Connection:
    """获取当前线程的数据库连接（自动复用，启用 WAL + 外键）。

    WAL 模式优势：读写不互斥，适合 Web 服务多请求并发场景。
    """
    if not hasattr(_local, "conn") or _local.conn is None:
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        _local.conn = conn
    return _local.conn


def init_db() -> None:
    """初始化数据库——建表（幂等，可重复调用）。"""
    conn = get_connection()
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
