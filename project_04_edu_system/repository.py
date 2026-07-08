"""repository.py — StudentRepository 数据访问层（v2.1：连接复用 + 分页搜索排序）"""

import sys
import sqlite3
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from database import get_connection
from models import StuGrade


class StudentRepository:
    """学生成绩数据访问对象——封装全部 SQLite CRUD 操作。

    v2.1 变更：
      - 移除方法内的 conn.close()，信任线程局部连接复用
      - 新增 list_paginated() 支持分页、搜索、排序
    """

    # ── 基础 CRUD ──────────────────────────────────────

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

    def update(self, name: str, chinese: int, math: int, english: int) -> StuGrade | None:
        """按姓名更新成绩。返回更新后的对象，不存在时返回 None。"""
        conn = get_connection()
        cursor = conn.execute(
            "UPDATE students SET chinese=?, math=?, english=? WHERE name=?",
            (chinese, math, english, name),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None
        return StuGrade(name, chinese, math, english)

    def delete(self, name: str) -> bool:
        """按姓名删除学生。返回是否删除成功。"""
        conn = get_connection()
        cursor = conn.execute("DELETE FROM students WHERE name=?", (name,))
        conn.commit()
        return cursor.rowcount > 0

    def find_by_name(self, name: str) -> StuGrade | None:
        """按姓名查询学生。"""
        conn = get_connection()
        row = conn.execute(
            "SELECT name, chinese, math, english FROM students WHERE name=?",
            (name,),
        ).fetchone()
        if row is None:
            return None
        return StuGrade(row["name"], row["chinese"], row["math"], row["english"])

    def list_all(self) -> list[StuGrade]:
        """列出全部学生成绩（按姓名排序）。"""
        conn = get_connection()
        rows = conn.execute(
            "SELECT name, chinese, math, english FROM students ORDER BY name"
        ).fetchall()
        return [
            StuGrade(r["name"], r["chinese"], r["math"], r["english"])
            for r in rows
        ]

    # ── 分页 + 搜索 + 排序（v2.1 新增） ────────────────

    # 允许的排序字段白名单（防止 SQL 注入）
    _ALLOWED_SORT_FIELDS = {"name", "chinese", "math", "english", "total"}

    def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str = "name",
        order: str = "asc",
    ) -> tuple[list[StuGrade], int]:
        """分页查询学生成绩，支持搜索和排序。

        Args:
            page: 页码（1-based）
            page_size: 每页数量（1-100）
            search: 搜索关键词（模糊匹配姓名）
            sort_by: 排序字段（name/chinese/math/english/total）
            order: 排序方向（asc/desc）

        Returns:
            (学生列表, 总记录数)
        """
        conn = get_connection()

        # ── 构建 WHERE 子句 ──
        where_clause = ""
        params: list = []
        if search and search.strip():
            where_clause = "WHERE name LIKE ?"
            params.append(f"%{search.strip()}%")

        # ── 统计总数 ──
        count_sql = f"SELECT COUNT(*) FROM students {where_clause}"
        total = conn.execute(count_sql, params).fetchone()[0]

        # ── 排序字段校验（白名单，防止注入） ──
        if sort_by == "total":
            order_field = "(chinese + math + english)"
        elif sort_by in self._ALLOWED_SORT_FIELDS:
            order_field = sort_by
        else:
            order_field = "name"

        direction = "DESC" if order.lower() == "desc" else "ASC"

        # ── 分页查询 ──
        offset = (page - 1) * page_size
        query = (
            f"SELECT name, chinese, math, english FROM students "
            f"{where_clause} ORDER BY {order_field} {direction} "
            f"LIMIT ? OFFSET ?"
        )
        rows = conn.execute(query, params + [page_size, offset]).fetchall()

        students = [
            StuGrade(r["name"], r["chinese"], r["math"], r["english"])
            for r in rows
        ]
        return students, total
