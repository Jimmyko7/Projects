"""
FastAPI 应用入口（v2.1：路由拆分 + API 版本化 + AI 分析）

启动：python -m uvicorn backend.main:app --reload --port 8000
文档：http://localhost:8000/docs
"""
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

from database import init_db  # noqa: E402

app = FastAPI(
    title="教务管理系统 API",
    version="2.1",
    description="学生成绩 RESTful API — 增删改查 + 分页搜索 + AI 分析",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    """应用启动时自动建表（幂等）。"""
    init_db()


# ── 注册路由模块 ──────────────────────────────────────
from backend.routers import students, ai  # noqa: E402

app.include_router(students.router)
app.include_router(ai.router)


# ── 旧 API 兼容重定向（/api/* → /api/v1/*）────────────
@app.api_route("/api/students", methods=["GET"])
@app.api_route("/api/students/{name}", methods=["GET"])
@app.api_route("/api/students", methods=["POST"])
@app.api_route("/api/students/{name}", methods=["PUT", "DELETE"])
def redirect_old_api(name: str = ""):
    target = f"/api/v1/students/{name}".rstrip("/")
    return RedirectResponse(url=target, status_code=307)
