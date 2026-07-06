"""database.py — SQLite 数据库连接与初始化"""

import sqlite3
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


def get_connection() -> sqlite3.Connection:
    """获取数据库连接（自动启用外键和行工厂）。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """初始化数据库——建表（幂等，可重复调用）。"""
    conn = get_connection()
    try:
        conn.execute(CREATE_TABLE_SQL)
        conn.commit()
    finally:
        conn.close()
