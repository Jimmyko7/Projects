# Project 4 — 教务管理系统 v2.1

FastAPI + React + TypeScript + SQLite 前后端分离的全栈 Web 应用。

> v1.0 纯控制台 OOP 版本（保留于根目录 `main.py`）  
> v2.0 基于 Repository + SQLite，向上扩展了 REST API 和 Web 前端  
> v2.1 连接池优化 + 分页搜索排序 + AI 成绩分析 + 路由拆分

## 功能

- 学生成绩增删改查（Web UI + REST API 双入口）
- **分页、搜索、排序**（v2.1 新增）
- 成绩校验（前端 0~100 + 后端 Pydantic 0~100 + 数据库 CHECK 三重保障）
- **AI 成绩分析**（v2.1 新增：DeepSeek LLM + 本地规则降级）
- SQLite WAL 模式 + 线程连接复用
- 自动生成 Swagger API 文档（`/docs`）
- 旧 API 路径 307 兼容重定向

## 技术栈

| 层 | 技术 |
|----|------|
| **前端** | React 18 + TypeScript + Vite |
| **后端** | FastAPI + Pydantic v2 |
| **数据库** | SQLite3 WAL 模式（标准库，零额外依赖） |
| **AI** | DeepSeek API（可选，未配置时自动降级本地规则） |
| **设计模式** | Repository 模式、分层架构、RESTful API、路由模块化 |

## 运行（需两个终端）

```bash
# 终端 1 — 后端 API 服务
cd project_04_edu_system
python -m uvicorn backend.main:app --reload --port 8000

# 终端 2 — 前端开发服务器
cd project_04_edu_system/frontend
npm install        # 首次运行
npm run dev
```

- 后端 Swagger 文档：http://localhost:8000/docs
- 前端页面：http://localhost:5173

> 控制台版本（v1.0）仍可运行：`python project_04_edu_system/main.py`

## 架构

```
                  ┌─────────────────────┐
                  │   React 前端 :5173   │
                  │  StudentList / Form  │
                  └──────────┬──────────┘
                             │ REST API (JSON)
                             │ /api/v1/*
                  ┌──────────▼──────────┐
                  │  FastAPI 路由        │  ← backend/main.py → routers/
                  │  ├─ students.py     │    学生 CRUD + 分页
                  │  └─ ai.py           │    AI 成绩分析
                  │  Pydantic 校验       │  ← backend/schemas.py
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │  StudentRepository   │  ← repository.py
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │  SQLite WAL 模式     │  ← database.py
                  │  (student.db)       │    线程连接复用
                  └─────────────────────┘
```

## 文件说明

| 文件 / 目录 | 职责 |
|-------------|------|
| `backend/main.py` | FastAPI 应用入口 + 路由注册 + 旧 API 兼容 |
| `backend/schemas.py` | Pydantic 请求/响应模型（含分页 + AI 分析） |
| `backend/routers/students.py` | 学生 CRUD + 分页搜索排序路由 |
| `backend/routers/ai.py` | AI 成绩分析端点（DeepSeek + 降级） |
| `repository.py` | `StudentRepository` — SQLite CRUD + 分页 |
| `database.py` | 数据库连接 + WAL 模式 + 线程复用 |
| `models.py` | `StuGrade` 数据类 |
| `main.py` | 控制台版本入口（v1.0，保留） |
| `frontend/src/` | React 前端源码 |

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/students` | 学生列表（分页+搜索+排序） |
| `GET` | `/api/v1/students/{name}` | 按姓名查询 |
| `POST` | `/api/v1/students` | 添加学生 |
| `PUT` | `/api/v1/students/{name}` | 修改成绩 |
| `DELETE` | `/api/v1/students/{name}` | 删除学生 |
| `POST` | `/api/v1/ai/analyze/{name}` | AI 成绩分析 |
| `*` | `/api/*` | → 307 重定向到 `/api/v1/*` |

**分页参数**：`?page=1&page_size=20&search=张&sort_by=total&order=desc`

## 迭代历程

| 版本 | 新增能力 |
|------|---------|
| v1.0 | 控制台交互 + SQLite 持久化 + Repository 模式 |
| v2.0 | FastAPI REST API + React Web UI + Swagger 文档 |
| v2.1 | 连接池优化 + 分页搜索排序 + AI 成绩分析 + 路由拆分 + API 版本化 |
