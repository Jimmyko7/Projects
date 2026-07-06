# 教务管理系统 — 从项目学 FastAPI + React 全栈开发

> 本文档不教你"从零学起"，而是带你把一个**你亲手写的 Python 控制台项目**
> 一步步看懂它是如何变成前后端分离 Web 系统的。
> 所有代码都有中文注释，对照着看即可。

---

## 启动方法

打开 **两个终端**：

**终端 1 — 后端（FastAPI）：**
```bash
cd project_04_edu_system
python -m uvicorn backend.main:app --reload --port 8000
```
启动后访问 http://localhost:8000/docs → **自动生成的 Swagger API 文档**（可以直接在页面里测试 API）

**终端 2 — 前端（React）：**
```bash
cd project_04_edu_system/frontend
npm install      # 首次运行
npm run dev
```
启动后访问 http://localhost:5173 → **浏览器中操作学生成绩**

---

## 一、整体架构：从控制台到 Web 发生了什么？

```
改造前（控制台 v1.0）              改造后（Web v2.0）
─────────────────────             ─────────────────────
main.py                            backend/main.py
  ├── input("请输入...")    →        ├── @app.get("/api/students")
  ├── print("添加成功")     →        ├── @app.post("/api/students")
  └── while True: 菜单循环   →        └── FastAPI 自动处理 HTTP 请求

models.py                          backend/schemas.py
  └── StuGrade (纯类)       →        └── Pydantic BaseModel (自动校验)

repository.py                      repository.py（不动！）
database.py                        database.py（不动！）
  └── SQLite CRUD           →        └── 原封不动保留
```

**核心思路：** 控制台的 `input()` 和 `print()` 被替换成了 HTTP 请求和 JSON 响应，
**数据层代码完全不动**。

---

## 二、后端分层精读

### 2.1 入口文件 `backend/main.py` — FastAPI 应用

这是整个后端的"大脑"，对照你原来的 `main.py` 看：

| 原版 main.py | 新版 backend/main.py | 变化 |
|-------------|---------------------|------|
| `EduManagement.run()` 死循环菜单 | `@app.get/post/put/delete` 路由装饰器 | 控制台循环 → HTTP 路由 |
| `input("请输入...")` 读用户输入 | FastAPI 自动从请求体解析 JSON | 手动输入 → Pydantic 自动解析 |
| `print("添加成功")` | `return StudentResponse(...)` | 打印字符串 → 返回 JSON |
| `except ValueError: print(e)` | `raise HTTPException(status_code=409)` | 打印错误 → HTTP 状态码 |

**关键知识点：**

- **路由装饰器** `@app.get("/api/students")`：告诉 FastAPI"当浏览器请求这个 URL 时，执行这个函数"。你在 `/docs` 页面看到的每个接口就是这些函数自动生成的。
- **`response_model=List[StudentResponse]`**：告诉 FastAPI 返回数据长什么样，用于自动生成 API 文档和做类型检查。
- **CORS 中间件**：因为前端跑在 `localhost:5173`，后端跑在 `localhost:8000`，浏览器默认禁止跨域请求。`CORSMiddleware` 告诉浏览器"允许 5173 访问我"。
- **Vite proxy 双保险**：`vite.config.ts` 里也配了 `/api` 代理到 `8000`，这样前端 fetch `/api/students` 时浏览器以为是同源请求。

### 2.2 数据模型 `backend/schemas.py` — Pydantic

这是你原来的 `models.py` 的"升级版"：

```python
# 原来：纯 Python 类，没有校验能力
class StuGrade:
    def __init__(self, s_name, s_chinese, ...):
        self.name = s_name
        ...

# 现在：Pydantic BaseModel，自动校验 + 生成文档
class StudentCreate(BaseModel):
    name: str = Field(..., min_length=1)
    chinese: int = Field(..., ge=0, le=100)  # ge = greater or equal, le = less or equal
```

**面试话术：** "我用 Pydantic 做请求校验，如果前端传了语文成绩 150，FastAPI 直接返回 422 并列出 `chinese: ensure this value is less than or equal to 100`，不需要手动写 if 判断。"

### 2.3 数据访问层 `repository.py` — 完全没动

这是整个改造的核心亮点：**你的 Repository 模式代码一行没改**。

```python
# backend/main.py 中直接引用原来的代码
from repository import StudentRepository
repo = StudentRepository()
repo.add(name, chinese, math, english)    # 完全复用
repo.list_all()                           # 完全复用
```

**面试话术：** "我以前写的控制台版本已经用了 Repository 模式做数据层封装，改造成 REST API 时数据层代码完全不需要动，只加了一个 HTTP 路由层。这证明了分层架构的价值。"

---

## 三、前端分层精读

### 3.1 技术选型理由

| 技术 | 为什么选它 |
|------|-----------|
| **React 18 + TypeScript** | React 是国内 AI/互联网公司绝对主流；TypeScript 提供类型安全 |
| **Vite** | 极快的开发服务器，替代 Webpack/CRA |
| **纯 fetch API** | 不用 axios，项目小不需要额外依赖；面试时可以说"我用原生 fetch 更懂底层" |
| **纯 CSS** | 不用 UI 库，展现你懂 CSS；面试时可以提"这个阶段先手写，大项目会用 Ant Design/shadcn" |

### 3.2 文件职责

```
frontend/src/
├── types/student.ts        # TypeScript 接口定义 ← 相当于后端的 schemas.py
├── api/studentApi.ts       # API 调用封装   ← 相当于后端的 repository.py
├── components/
│   ├── StudentList.tsx     # 学生列表组件   ← 纯展示 + 删除
│   └── StudentForm.tsx     # 表单组件       ← 新增 + 编辑（一个组件两种模式）
├── App.tsx                 # 页面状态管理   ← 相当于后端的 EduManagement.run()
├── App.css                 # 页面级样式
├── index.css               # 全局样式
└── main.tsx                # React 入口
```

### 3.3 核心概念：从 Python 到 TypeScript 的对照

| Python (你熟悉的) | TypeScript/React (要学的) | 类比 |
|------------------|--------------------------|------|
| `class StuGrade` | `interface Student` | 数据类 → 接口 |
| `def add_stu(self)` | `const handleAdd = async () => {...}` | 方法 → 异步箭头函数 |
| `input("请输入")` | `<input onChange={...} />` | 控制台输入 → HTML 输入框 |
| `print(stu)` | `return (<tr><td>{s.name}</td></tr>)` | 打印 → JSX 渲染 |
| `except ValueError as e` | `catch (err) { setError(err.message) }` | 异常 → try/catch + 状态 |
| `self.repo.list_all()` | `await fetchAll()` | 同步调用 → 异步 HTTP 请求 |

### 3.4 数据流：一次"添加学生"的完整旅程

```
用户点击 [添加] 按钮
  ↓
StudentForm 组件 → handleSubmit → 前端校验（0~100）
  ↓
api/studentApi.ts → fetch POST /api/students  ← Vite proxy 转发到 localhost:8000
  ↓
backend/main.py → @app.post("/api/students")
  ↓
schemas.py → StudentCreate → Pydantic 校验（0~100 双重保障）
  ↓
repository.py → StudentRepository.add() → INSERT INTO students
  ↓
返回 JSON {name, chinese, math, english, total}
  ↓
App.tsx → loadStudents() → 刷新列表
  ↓
StudentList 组件 → 重新渲染表格（新学生出现）
```

### 3.5 三个重要 React 概念（你只需要先理解这三个）

**① `useState` — 组件状态**
```tsx
const [students, setStudents] = useState<Student[]>([])
//   ↑ 变量名     ↑ 修改函数            ↑ 初始值（空数组）
//
// 类比 Python：students = []; 但 React 中改数据必须用 setStudents()
// 因为 React 需要在数据变化时自动重新渲染页面
```

**② `useEffect` — 页面加载时执行**
```tsx
useEffect(() => {
  loadStudents()     // 页面打开时自动拉取学生列表
}, [])
//  ↑ 空数组 = "只在组件首次渲染时执行一次"
//  类比 Python 的 __init__ 或构造函数的初始化代码
```

**③ Props — 父组件传数据给子组件**
```tsx
// App.tsx（父组件）
<StudentList students={students} onEdit={handleEdit} />
//                   ↑ 数据传下去     ↑ 回调函数也传下去

// StudentList.tsx（子组件）
const StudentList: React.FC<StudentListProps> = ({ students, onEdit }) => {
  // 直接用 students，不需要再去请求
}
```

---

## 四、面试准备：怎么讲这个项目

### 开场（30 秒）
> "我改造了一个教务管理系统，从纯 Python 控制台应用升级成了 FastAPI + React 前后端分离的 Web 系统。后端用 Repository 模式封装 SQLite，前端用 TypeScript 做类型安全。整个过程展示了从单体应用到 RESTful 架构的演进。"

### 技术亮点（按面试官兴趣展开）

1. **分层架构不变** → "原来的 Repository 模式和数据库层一行没动，只加了 HTTP 路由层，这证明了分层设计的好处。"
2. **全栈类型安全** → "后端 Pydantic + 前端 TypeScript 共享同一套数据契约，改动一个字段两端同时报错。"
3. **自动文档** → "FastAPI 自动生成了 Swagger 文档，不需要额外写 API 文档，`/docs` 打开就能用。"
4. **未来 AI 扩展** → "后续可以加一个 `/api/ai/analyze` 端点，调用 LLM 分析成绩趋势、生成学习建议——这就是 AI Agent 的核心能力：API 调用 + 工具使用。"

### 可能会被问到的题

| 问题 | 回答方向 |
|------|---------|
| 为什么用 FastAPI 而不是 Flask？ | 异步性能更好、自动生成文档、Pydantic 类型校验、AI 生态（LangChain 原生支持） |
| 为什么不用 Redux/Zustand？ | 这个规模的项目，React 内置 useState 足够；TanStack Query 是更好的服务端状态方案 |
| 怎么处理并发？ | SQLite 写入串行化是瓶颈；生产环境会换成 PostgreSQL + SQLAlchemy 异步连接池 |
| CORS 是什么？ | 浏览器安全策略；后端加 CORSMiddleware + 前端 Vite proxy 双保险 |
| 怎么部署？ | 后端 uvicorn + nginx 反代；前端 Vite build → 静态文件扔 CDN/nginx |

---

## 五、下一步：自己动手改

理解了以上内容后，建议试做这些练习来巩固：

1. **加一个搜索框**：在列表上方加 `<input>`，输入姓名实时过滤学生列表（用 `useState` + `filter`）
2. **加按总分排序**：点表头"总分"按高低排序（用 `useState` + `sort`）
3. **后端加一个统计端点**：`GET /api/stats` 返回平均分、最高分（FastAPI 新路由）
4. **接入 LLM**：加 `/api/ai/analyze/{name}`，把成绩发给 DeepSeek 生成一段分析文字
5. **加 Ant Design**：把纯 CSS 换成 Ant Design 组件（`Table`, `Form`, `Modal`）

---

## 六、有用的外链

- [FastAPI 官方教程](https://fastapi.tiangolo.com/zh/) — 中文版，30 分钟能看完核心
- [React 官方教程](https://zh-hans.react.dev/learn) — 只看"快速入门"和"井字棋游戏"两节
- [TypeScript 5 分钟上手](https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html)
- [Vite 中文文档](https://cn.vitejs.dev/)
