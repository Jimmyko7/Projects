"""app.py — AI 智能伴侣 Streamlit 应用 | streamlit run app.py"""

import streamlit as st
import os
from openai import OpenAI
from config import SESSION_DIR, DEFAULT_NICK, DEFAULT_CHARACTER, LLM_MODEL, LLM_BASE_URL
from session_manager import generate_name, list_all, save, load, remove

st.set_page_config(page_title="AI 智能伴侣", page_icon="🦸", layout="wide", initial_sidebar_state="expanded")
st.title("AI 智能伴侣")

for k, v in [("messages", []), ("nick_name", DEFAULT_NICK), ("character", DEFAULT_CHARACTER), ("current_session", generate_name())]:
    if k not in st.session_state: st.session_state[k] = v

api_key = os.environ.get("DEEPSEEK_API_KEY")
if not api_key:
    st.error("❌ 未设置 DEEPSEEK_API_KEY 环境变量，请配置后重启应用。")
    st.stop()
client = OpenAI(api_key=api_key, base_url=LLM_BASE_URL)

st.text(f"会话: {st.session_state.current_session}")
for m in st.session_state.messages:
    st.chat_message(m["role"]).write(m["content"])

with st.sidebar:
    st.subheader("🎮 控制面板")
    if st.button("新建会话", use_container_width=True, icon="✏️"):
        save({"nick_name": st.session_state.nick_name, "character": st.session_state.character, "current_session": st.session_state.current_session, "messages": st.session_state.messages}, SESSION_DIR)
        if any(load(s, SESSION_DIR) and not load(s, SESSION_DIR).get("messages") for s in list_all(SESSION_DIR)):
            st.warning("存在空会话，请先删除!")
        else:
            st.session_state.current_session = generate_name(); st.session_state.messages = []; st.rerun()
    st.text("历史会话")
    for s in list_all(SESSION_DIR):
        c1, c2 = st.columns([4, 1])
        with c1:
            if st.button(s, icon="📄", key=f"s_{s}", type="primary" if s == st.session_state.current_session else "secondary"):
                d = load(s, SESSION_DIR)
                if d:
                    st.session_state.current_session = s
                    st.session_state.nick_name = d.get("nick_name", DEFAULT_NICK)
                    st.session_state.character = d.get("character", DEFAULT_CHARACTER)
                    st.session_state.messages = d.get("messages", [])
                st.rerun()
        with c2:
            if st.button("", icon="❌", key=f"d_{s}"):
                remove(s, SESSION_DIR)
                if s == st.session_state.current_session: st.session_state.messages = []; st.session_state.current_session = generate_name()
                st.rerun()
    st.divider()
    st.subheader("🧑 伴侣信息")
    if n := st.text_input("昵称", value=st.session_state.nick_name): st.session_state.nick_name = n
    if c := st.text_area("性格", value=st.session_state.character): st.session_state.character = c

if p := st.chat_input("请输入您的问题："):
    st.chat_message("user").write(p)
    st.session_state.messages.append({"role": "user", "content": p})
    resp = client.chat.completions.create(model=LLM_MODEL, messages=[{"role":"system","content":f"昵称:{st.session_state.nick_name}  性格:{st.session_state.character}"}, *st.session_state.messages], stream=True)
    ph = st.empty(); full = ""
    for ck in resp:
        if ck.choices[0].delta.content is not None: full += ck.choices[0].delta.content; ph.chat_message("assistant").write(full)
    st.session_state.messages.append({"role":"assistant","content":full})
    save({"nick_name":st.session_state.nick_name,"character":st.session_state.character,"current_session":st.session_state.current_session,"messages":st.session_state.messages}, SESSION_DIR)
