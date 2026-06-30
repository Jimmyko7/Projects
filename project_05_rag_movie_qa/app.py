"""
app.py — RAG 电影问答 Streamlit 应用
使用: streamlit run app.py
"""

import streamlit as st
import os
from openai import OpenAI

from config import (
    SESSION_DIR, COLLECTION_NAME, RETRIEVAL_K,
    DEFAULT_NICK, DEFAULT_CHARACTER, LLM_MODEL, LLM_BASE_URL,
)
from rag_engine import load_vector_store, search_movies, build_prompt
from session_manager import generate_name, list_all, save, load, delete


# ═══════════════ 初始化 ═══════════════

st.set_page_config(
    page_title="RAG 电影问答", page_icon="🎬",
    layout="wide", initial_sidebar_state="expanded",
)
st.title("🎬 RAG 电影智能问答")
st.caption("LangChain + Chroma + DeepSeek | TMDB Top 300 知识库")

for key, default in [
    ("messages", []), ("nick_name", DEFAULT_NICK),
    ("character", DEFAULT_CHARACTER), ("current_session", generate_name()),
    ("rag_enabled", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


@st.cache_resource
def get_vector_store():
    return load_vector_store()

vector_store = get_vector_store()
rag_available = vector_store is not None

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url=LLM_BASE_URL,
)


# ═══════════════ 聊天历史 ═══════════════

st.text(f"会话: {st.session_state.current_session}")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("movie_refs"):
            with st.expander("📚 参考资料"):
                for r in msg["movie_refs"]:
                    st.caption(f"🎥 {r[0]} ({r[1]}) | {r[3]} | 评分:{r[2]}")


# ═══════════════ 侧边栏 ═══════════════

with st.sidebar:
    st.subheader("🎮 控制面板")
    st.divider()

    # RAG 开关
    st.subheader("🔍 知识库检索 (RAG)")
    if rag_available:
        rag = st.toggle(
            "启用电影知识库", value=st.session_state.rag_enabled,
            help="从 TMDB Top 300 检索相关电影",
        )
        st.session_state.rag_enabled = rag
        st.success("✅ RAG 已启用" if rag else "ℹ️ 普通对话模式")
    else:
        st.warning("⚠️ 向量库未就绪")
        st.caption("运行 01_build_kb.py 并设置 DASHSCOPE_API_KEY")
        st.session_state.rag_enabled = False

    st.divider()

    # 会话管理
    st.subheader("💬 会话管理")
    if st.button("新建会话", use_container_width=True, icon="✏️"):
        save({
            "nick_name": st.session_state.nick_name,
            "character": st.session_state.character,
            "rag_enabled": st.session_state.rag_enabled,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages,
        }, SESSION_DIR)
        empty = any(
            load(s, SESSION_DIR) and not load(s, SESSION_DIR).get("messages")
            for s in list_all(SESSION_DIR)
        )
        if empty:
            st.warning("存在空会话，请先删除!")
        else:
            st.session_state.current_session = generate_name()
            st.session_state.messages = []
            st.session_state.rag_enabled = False
            st.rerun()

    st.text("历史会话")
    for s in list_all(SESSION_DIR):
        c1, c2 = st.columns([4, 1])
        with c1:
            t = "primary" if s == st.session_state.current_session else "secondary"
            if st.button(s, icon="📄", key=f"sel_{s}", type=t):
                d = load(s, SESSION_DIR)
                if d:
                    st.session_state.current_session = s
                    st.session_state.nick_name = d.get("nick_name", DEFAULT_NICK)
                    st.session_state.character = d.get("character", DEFAULT_CHARACTER)
                    st.session_state.messages = d.get("messages", [])
                    st.session_state.rag_enabled = d.get("rag_enabled", False)
                st.rerun()
        with c2:
            if st.button("", icon="❌", key=f"del_{s}"):
                delete(s, SESSION_DIR)
                if s == st.session_state.current_session:
                    st.session_state.messages = []
                    st.session_state.current_session = generate_name()
                st.rerun()

    st.divider()

    # 角色设置
    st.subheader("🧑 角色设置")
    nick = st.text_input("昵称", value=st.session_state.nick_name)
    if nick:
        st.session_state.nick_name = nick
    char = st.text_area("性格", value=st.session_state.character)
    if char:
        st.session_state.character = char


# ═══════════════ 聊天 ═══════════════

if prompt := st.chat_input("试试问电影相关的问题！"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    rag_context, movie_refs = "", []
    if st.session_state.rag_enabled and rag_available:
        with st.spinner("🔍 检索中..."):
            rag_context, movie_refs = search_movies(prompt, vector_store)  # k 自动选择
        if movie_refs:
            st.caption(f"📚 检索到 {len(movie_refs)} 部相关电影")

    system = build_prompt(
        st.session_state.nick_name, st.session_state.character, rag_context,
    ) if (st.session_state.rag_enabled and rag_context) else \
        f"昵称:{st.session_state.nick_name}  性格:{st.session_state.character}"

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "system", "content": system}, *st.session_state.messages],
        stream=True,
    )

    placeholder = st.empty()
    full = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            full += chunk.choices[0].delta.content
            placeholder.chat_message("assistant").write(full)

    st.session_state.messages.append({
        "role": "assistant", "content": full, "movie_refs": movie_refs,
    })
    save({
        "nick_name": st.session_state.nick_name,
        "character": st.session_state.character,
        "rag_enabled": st.session_state.rag_enabled,
        "current_session": st.session_state.current_session,
        "messages": st.session_state.messages,
    }, SESSION_DIR)

st.sidebar.divider()
st.sidebar.caption(
    f"📦 {COLLECTION_NAME if rag_available else '未就绪'} | "
    f"🔍 Top{RETRIEVAL_K} | 🤖 {LLM_MODEL}"
)
