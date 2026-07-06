"""repository.py — StudentRepository 数据访问层（Repository 模式）"""

import sys
import sqlite3
from pathlib import Path

# 确保从任意目录运行都能找到同目录模块
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from database import get_connection
from models import StuGrade


class StudentRepository:
    """学生成绩数据访问对象——封装全部 SQLite CRUD 操作。"""

    def add(self, name: str, chinese: int, math: int, english: int) -> StuGrade:
        """添加学生成绩。重名时抛出 ValueError。"""
        conn = get_connection()
        try:
            conn.execute(
                "INSERT INTO students (name, chinese, math, english) VALUES (?, ?, ?, ?)",
                (name, chinese, math, english),
            )
            conn.commit()
            return StuGrade(name, chinese, math, english)
        except sqlite3.IntegrityError:
            raise ValueError(f"学生 '{name}' 已存在！")
        finally:
            conn.close()

    def update(self, name: str, chinese: int, math: int, english: int) -> StuGrade | None:
        """按姓名更新成绩。返回更新后的对象，不存在时返回 None。"""
        conn = get_connection()
        try:
            cursor = conn.execute(
                "UPDATE students SET chinese=?, math=?, english=? WHERE name=?",
                (chinese, math, english, name),
            )
            conn.commit()
            if cursor.rowcount == 0:
                return None
            return StuGrade(name, chinese, math, english)
        finally:
            conn.close()

    def delete(self, name: str) -> bool:
        """按姓名删除学生。返回是否删除成功。"""
        conn = get_connection()
        try:
            cursor = conn.execute("DELETE FROM students WHERE name=?", (name,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def find_by_name(self, name: str) -> StuGrade | None:
        """按姓名查询学生。"""
        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT name, chinese, math, english FROM students WHERE name=?",
                (name,),
            ).fetchone()
            if row is None:
                return None
            return StuGrade(row["name"], row["chinese"], row["math"], row["english"])
        finally:
            conn.close()

    def list_all(self) -> list[StuGrade]:
        """列出全部学生成绩。"""
        conn = get_connection()
        try:
            rows = conn.execute(
                "SELECT name, chinese, math, english FROM students ORDER BY name"
            ).fetchall()
            return [
                StuGrade(r["name"], r["chinese"], r["math"], r["english"])
                for r in rows
            ]
        finally:
            conn.close()
