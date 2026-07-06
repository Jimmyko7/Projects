# Project 4 — 教务管理系统 v2.0

FastAPI + React + TypeScript + SQLite 前后端分离的全栈 Web 应用。

> v1.0 为纯控制台 OOP 版本（保留于根目录 `main.py`），  
> v2.0 基于同一套 Repository + SQLite 数据层，向上扩展了 REST API 和 Web 前端。

## 功能

- 学生成绩增删改查（Web UI + REST API 双入口）
- 成绩校验（前端 0~100 + 后端 Pydantic 0~100 + 数据库 CHECK 三重保障）
- 按姓名唯一索引，重名自动提示冲突（409）
- SQLite 持久化存储
- 自动生成 Swagger API 文档（`/docs`）

## 技术栈

| 层 | 技术 |
|----|------|
| **前端** | React 18 + TypeScript + Vite |
| **后端** | FastAPI + Pydantic v2 |
| **数据库** | SQLite3（标准库，零额外依赖） |
| **设计模式** | Repository 模式、分层架构、RESTful API |

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
                  │  StudentList / Form │
                  └──────────┬──────────┘
                             │ REST API (JSON)
                  ┌──────────▼──────────┐
                  │  FastAPI 路由 :8000  │  ← backend/main.py
                  │  Pydantic 校验       │  ← backend/schemas.py
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │  StudentRepository   │  ← repository.py（v1 代码未动）
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │  SQLite (student.db) │  ← database.py（v1 代码未动）
                  └─────────────────────┘
```

## 文件说明

| 文件 / 目录 | 职责 |
|-------------|------|
| `backend/main.py` | FastAPI 应用入口 + 5 个 RESTful 路由 |
| `backend/schemas.py` | Pydantic 请求/响应模型 |
| `repository.py` | `StudentRepository` — SQLite CRUD 封装（v1 代码未动） |
| `database.py` | 数据库连接 + 建表（v1 代码未动） |
| `models.py` | `StuGrade` 数据类（v1 代码未动） |
| `main.py` | 控制台版本入口（v1.0，保留） |
| `frontend/src/` | React 前端源码 |
| `LEARNING_GUIDE.md` | 从项目学 FastAPI + React 的配套文档 |

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/students` | 获取全部学生 |
| `GET` | `/api/students/{name}` | 按姓名查询 |
| `POST` | `/api/students` | 添加学生（重名返回 409） |
| `PUT` | `/api/students/{name}` | 修改成绩（支持部分更新） |
| `DELETE` | `/api/students/{name}` | 删除学生 |

## 迭代历程

| 版本 | 新增能力 |
|------|---------|
| v1.0 | 控制台交互 + SQLite 持久化 + Repository 模式 |
| v2.0 | FastAPI REST API + React Web UI + 前端校验 + Swagger 文档 |
