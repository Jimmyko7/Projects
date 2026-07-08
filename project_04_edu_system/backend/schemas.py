"""Pydantic 数据模型 — v2.1：分页 + AI 分析 schema 新增"""

from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


# ── 学生 CRUD ──────────────────────────────────────────

class StudentCreate(BaseModel):
    """添加学生请求体。Pydantic 自动校验 0~100 范围。"""
    name: str = Field(..., min_length=1, description="学生姓名")
    chinese: int = Field(..., ge=0, le=100, description="语文成绩 (0~100)")
    math: int = Field(..., ge=0, le=100, description="数学成绩 (0~100)")
    english: int = Field(..., ge=0, le=100, description="英语成绩 (0~100)")


class StudentUpdate(BaseModel):
    """修改成绩请求体。所有字段可选。"""
    chinese: int | None = Field(default=None, ge=0, le=100)
    math: int | None = Field(default=None, ge=0, le=100)
    english: int | None = Field(default=None, ge=0, le=100)


class StudentResponse(BaseModel):
    """单个学生响应体。"""
    name: str
    chinese: int
    math: int
    english: int
    total: int = Field(..., description="三科总分")


class MessageResponse(BaseModel):
    message: str


# ── 分页（v2.1 新增）───────────────────────────────────

class PaginatedStudentResponse(BaseModel):
    """分页响应体——含学生列表 + 分页元信息。"""
    items: list[StudentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ── AI 分析（v2.1 新增）────────────────────────────────

class AIAnalyzeRequest(BaseModel):
    """AI 成绩分析请求体。question 为空时使用默认分析维度。"""
    question: str | None = Field(default=None, description="自定义分析问题")


class AIAnalyzeResponse(BaseModel):
    """AI 成绩分析响应体。"""
    student_name: str
    chinese: int
    math: int
    english: int
    total: int
    analysis: str = Field(..., description="AI 生成的分析文本")
    model: str = Field(default="deepseek-chat", description="使用的 LLM 模型")
