# Project 1 — AI 智能伴侣

基于 **Streamlit + DeepSeek API** 的多轮对话聊天应用。

## 功能

- 💬 多轮对话 + 流式输出
- 🎭 角色扮演（自定义昵称/性格）
- 💾 会话管理（新建/切换/删除/JSON 持久化）

## 技术栈

- **前端**: Streamlit
- **LLM**: DeepSeek (deepseek-chat) via OpenAI SDK

## 运行

```bash
streamlit run project_01_ai_chatbot/app.py
```

## 迭代历程

| 版本 | 新增能力 |
|------|---------|
| v1 | 基础对话（系统提示 + 无状态） |
| v2 | 流式输出 + 会话记忆 |
| v3 | 角色扮演（昵称/性格自定义） |
| v4 | 会话管理（JSON 持久化） |
| v5 | 排序优化 + 错误处理 |
