"""routers/students.py — 学生成绩 CRUD 路由（v2.1：分页 + 搜索 + 排序）"""
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

_PARENT = Path(__file__).resolve().parent.parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

from repository import StudentRepository
from backend.schemas import (
    StudentCreate, StudentUpdate, StudentResponse,
    MessageResponse, PaginatedStudentResponse,
)

router = APIRouter(prefix="/api/v1/students", tags=["学生管理"])
repo = StudentRepository()


# ── 分页查询（v2.1 新增）───────────────────────────────

@router.get("", response_model=PaginatedStudentResponse)
def list_students(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
    search: str | None = Query(default=None, description="按姓名模糊搜索"),
    sort_by: str = Query(default="name", description="排序字段：name/chinese/math/english/total"),
    order: str = Query(default="asc", description="排序方向：asc/desc"),
):
    """获取学生成绩列表——支持分页、搜索、排序。

    示例：
      GET /api/v1/students?page=1&page_size=20
      GET /api/v1/students?search=张&sort_by=total&order=desc
    """
    students, total = repo.list_paginated(
        page=page, page_size=page_size, search=search,
        sort_by=sort_by, order=order,
    )
    items = [
        StudentResponse(
            name=s.name, chinese=s.chinese, math=s.math, english=s.english,
            total=s.chinese + s.math + s.english,
        )
        for s in students
    ]
    total_pages = (total + page_size - 1) // page_size
    return PaginatedStudentResponse(
        items=items, total=total, page=page,
        page_size=page_size, total_pages=total_pages,
    )


# ── 按姓名查询 ────────────────────────────────────────

@router.get("/{name}", response_model=StudentResponse)
def get_student(name: str):
    """按姓名查询单个学生成绩。"""
    s = repo.find_by_name(name)
    if s is None:
        raise HTTPException(status_code=404, detail=f"学生 '{name}' 不存在")
    return StudentResponse(
        name=s.name, chinese=s.chinese, math=s.math, english=s.english,
        total=s.chinese + s.math + s.english,
    )


# ── 添加学生 ──────────────────────────────────────────

@router.post("", response_model=StudentResponse, status_code=201)
def create_student(body: StudentCreate):
    """添加一名学生成绩。姓名重复时返回 409。"""
    try:
        s = repo.add(body.name, body.chinese, body.math, body.english)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return StudentResponse(
        name=s.name, chinese=s.chinese, math=s.math, english=s.english,
        total=s.chinese + s.math + s.english,
    )


# ── 修改成绩 ──────────────────────────────────────────

@router.put("/{name}", response_model=StudentResponse)
def update_student(name: str, body: StudentUpdate):
    """按姓名修改学生成绩（支持部分更新）。"""
    existing = repo.find_by_name(name)
    if existing is None:
        raise HTTPException(status_code=404, detail=f"学生 '{name}' 不存在")
    repo.update(
        name,
        body.chinese if body.chinese is not None else existing.chinese,
        body.math if body.math is not None else existing.math,
        body.english if body.english is not None else existing.english,
    )
    updated = repo.find_by_name(name)
    return StudentResponse(
        name=updated.name, chinese=updated.chinese,
        math=updated.math, english=updated.english,
        total=updated.chinese + updated.math + updated.english,
    )


# ── 删除学生 ──────────────────────────────────────────

@router.delete("/{name}", response_model=MessageResponse)
def delete_student(name: str):
    """按姓名删除学生。"""
    if repo.delete(name):
        return MessageResponse(message=f"学生 '{name}' 已删除")
    raise HTTPException(status_code=404, detail=f"学生 '{name}' 不存在")
