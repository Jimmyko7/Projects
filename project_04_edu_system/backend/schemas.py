"""Pydantic 数据模型 —— 请求体 / 响应体的类型定义。

FastAPI 用 Pydantic 自动校验请求数据，生成 OpenAPI (Swagger) 文档。
与父目录的 models.py（StuGrade 数据类）不同：
  - models.py   → 纯 Python 数据类，供 Repository 内部使用
  - schemas.py  → Pydantic BaseModel，供 FastAPI 路由使用（自动校验 + 文档生成）
"""
from pydantic import BaseModel, Field


# ── 创建学生请求体 ────────────────────────────────
class StudentCreate(BaseModel):
    """添加学生时前端发来的 JSON 数据结构。

    Field(ge=0, le=100) → Pydantic 自动校验 0~100 范围，
    不符合时 FastAPI 返回 422 并提示具体错误字段。"""

    name: str = Field(..., min_length=1, description="学生姓名")
    chinese: int = Field(..., ge=0, le=100, description="语文成绩 (0~100)")
    math: int = Field(..., ge=0, le=100, description="数学成绩 (0~100)")
    english: int = Field(..., ge=0, le=100, description="英语成绩 (0~100)")


# ── 更新学生请求体 ────────────────────────────────
class StudentUpdate(BaseModel):
    """修改成绩时前端发来的 JSON 数据结构。

    所有字段可选：前端可以只传要改的科目。"""

    chinese: int | None = Field(default=None, ge=0, le=100, description="语文成绩 (0~100)")
    math: int | None = Field(default=None, ge=0, le=100, description="数学成绩 (0~100)")
    english: int | None = Field(default=None, ge=0, le=100, description="英语成绩 (0~100)")


# ── 学生响应体 ────────────────────────────────────
class StudentResponse(BaseModel):
    """返回给前端的 JSON 数据结构。"""

    name: str
    chinese: int
    math: int
    english: int
    total: int = Field(..., description="三科总分")


# ── 通用消息响应 ───────────────────────────────────
class MessageResponse(BaseModel):
    message: str
