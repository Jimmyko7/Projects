"""
FastAPI 应用入口 + RESTful API 路由

启动命令：
    cd project_04_edu_system
    python -m uvicorn backend.main:app --reload --port 8000

打开浏览器访问：
    http://localhost:8000/docs    ← 自动生成的 Swagger 文档（可直接在页面中测试 API）
    http://localhost:8000/redoc   ← 另一种风格的 API 文档

架构说明：
    前端 (React) → HTTP REST API → FastAPI 路由 (本文件)
                                      ↓
                                  schemas.py (请求校验)
                                      ↓
                                  ../repository.py (数据访问)
                                      ↓
                                  ../database.py (SQLite)
"""
import sys
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# 将父目录加入 sys.path，以便 import 同级的 repository 和 database 模块
_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

from database import init_db
from repository import StudentRepository
from backend.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    MessageResponse,
)

# ── 应用初始化 ──────────────────────────────────────
app = FastAPI(
    title="教务管理系统 API",
    version="2.0",
    description="学生成绩 RESTful API —— 支持增删改查",
)

# CORS 中间件：允许前端（localhost:5173）跨域访问后端 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 Repository 实例（单例，整个应用共享一个数据库连接池）
repo = StudentRepository()


@app.on_event("startup")
def startup():
    """应用启动时自动建表（幂等，数据库已存在也不会报错）。"""
    init_db()


# ── 路由：查询全部学生 ──────────────────────────────
@app.get("/api/students", response_model=List[StudentResponse])
def list_students():
    """获取全部学生成绩列表，按姓名排序。"""
    students = repo.list_all()
    return [
        StudentResponse(
            name=s.name,
            chinese=s.chinese,
            math=s.math,
            english=s.english,
            total=s.chinese + s.math + s.english,
        )
        for s in students
    ]


# ── 路由：按姓名查询 ────────────────────────────────
@app.get("/api/students/{name}", response_model=StudentResponse)
def get_student(name: str):
    """按姓名查询单个学生成绩。"""
    s = repo.find_by_name(name)
    if s is None:
        raise HTTPException(status_code=404, detail=f"学生 '{name}' 不存在")
    return StudentResponse(
        name=s.name,
        chinese=s.chinese,
        math=s.math,
        english=s.english,
        total=s.chinese + s.math + s.english,
    )


# ── 路由：添加学生 ──────────────────────────────────
@app.post("/api/students", response_model=StudentResponse, status_code=201)
def create_student(body: StudentCreate):
    """添加一名学生成绩。姓名重复时返回 409 冲突。"""
    try:
        s = repo.add(body.name, body.chinese, body.math, body.english)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return StudentResponse(
        name=s.name,
        chinese=s.chinese,
        math=s.math,
        english=s.english,
        total=s.chinese + s.math + s.english,
    )


# ── 路由：修改成绩 ──────────────────────────────────
@app.put("/api/students/{name}", response_model=StudentResponse)
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
        name=updated.name,
        chinese=updated.chinese,
        math=updated.math,
        english=updated.english,
        total=updated.chinese + updated.math + updated.english,
    )


# ── 路由：删除学生 ──────────────────────────────────
@app.delete("/api/students/{name}", response_model=MessageResponse)
def delete_student(name: str):
    """按姓名删除学生。"""
    if repo.delete(name):
        return MessageResponse(message=f"学生 '{name}' 已删除")
    raise HTTPException(status_code=404, detail=f"学生 '{name}' 不存在")
