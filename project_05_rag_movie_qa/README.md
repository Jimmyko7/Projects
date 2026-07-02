# Project 5 — RAG 电影智能问答 🔥

基于 **LangChain + Chroma + DeepSeek** 的 RAG 检索增强生成系统。

## 功能

- 🧬 电影向量知识库构建（CSV → Chroma）
- 🔍 语义检索（自然语言搜电影）
- 💬 RAG 问答（检索 + LLM 生成）
- 🌐 Streamlit Web UI（一键切换检索/对话模式）

## 架构

```
用户提问 → Chroma 向量检索 (top-3)
              → 格式化上下文
              → 注入系统提示词
              → DeepSeek 流式生成
              → 展示答案 + 电影引用
```

## 技术栈

| 组件 | 技术 |
|------|------|
| LLM | DeepSeek |
| 嵌入 | DashScope (text-embedding-v4) |
| 向量库 | Chroma |
| 框架 | LangChain + LangChain Community |
| UI | Streamlit |

## 运行

```bash
# Step 1: 构建向量知识库（一次性）
python project_05_rag_movie_qa/01_build_kb.py

# Step 2: 命令行 RAG 问答
python project_05_rag_movie_qa/02_rag_cli.py

# Step 3: Streamlit Web 界面
streamlit run project_05_rag_movie_qa/app.py
```

## 文件

| 文件 | 作用 |
|------|------|
| `01_build_kb.py` | CSV→Document→分割→嵌入→Chroma |
| `02_rag_cli.py` | 命令行问答（手动+LCEL双实现） |
| `app.py` | Web UI（RAG开关+引用展示） |
| `方案文档.md` | 技术方案：架构/设计决策/学习路径 |
