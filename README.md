# Python AI 全栈项目集

> 5 个独立项目，展示从 Python 基础到 RAG 检索增强生成的完整工程能力。

## 项目清单

| # | 项目 | 技术栈 | 难度 |
|---|------|--------|------|
| 1 | [AI 智能伴侣](./project_01_ai_chatbot/) | Streamlit + DeepSeek API | ⭐⭐ |
| 2 | [网络爬虫](./project_02_web_scraper/) | requests + lxml + XPath | ⭐⭐ |
| 3 | [数据分析](./project_03_data_analysis/) | Pandas + Matplotlib + Jupyter | ⭐⭐ |
| 4 | [教务管理系统](./project_04_edu_system/) | 纯 OOP（面向对象） | ⭐ |
| 5 | **[RAG 电影问答](./project_05_rag_movie_qa/)** | LangChain + Chroma + RAG | ⭐⭐⭐ |

## 项目关系

```
TMDB 爬虫                       数据分析
(project_02) ──→ movies.csv ──→ (project_03)
                     │
                     ▼
              RAG 电影问答 (project_05) ←── AI 伴侣 (project_01)
              向量检索 + LLM 生成         Streamlit 聊天 UI
```

项目 5（RAG）是核心亮点，串联了爬虫、数据分析和 AI 应用三个方向。

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
export DEEPSEEK_API_KEY=sk-your-key      # Linux/macOS
set DEEPSEEK_API_KEY=sk-your-key         # Windows
set DASHSCOPE_API_KEY=sk-your-key        # 仅 RAG 项目需要

# 3. 运行各项目（见各项目 README）
```

## 环境变量

| 变量 | 用途 | 哪些项目需要 |
|------|------|-------------|
| `DEEPSEEK_API_KEY` | DeepSeek LLM 调用 | project_01, project_05 |
| `DASHSCOPE_API_KEY` | 阿里云向量嵌入 | project_05 |
