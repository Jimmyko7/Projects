"""
rag_engine.py — RAG 检索引擎（CLI 和 Streamlit 共用）

职责：向量库加载 / 语义检索 / 上下文格式化 / 提示词构建
"""

import os
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, RETRIEVAL_K


def load_vector_store() -> Chroma | None:
    """加载 Chroma 持久化向量库（返回 None 表示不可用）"""
    if not os.path.exists(CHROMA_DIR):
        return None
    if not os.environ.get("DASHSCOPE_API_KEY"):
        return None
    try:
        embeddings = DashScopeEmbeddings(model=EMBEDDING_MODEL)
        return Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR),
        )
    except Exception:
        return None


def search_movies(query: str, vector_store, k: int = RETRIEVAL_K) -> tuple[str, list]:
    """
    语义检索电影知识库

    返回:
        (上下文字符串, [(片名,年份,评分,类型), ...])
    """
    if vector_store is None:
        return "", []

    docs = vector_store.similarity_search(query, k=k)
    if not docs:
        return "", []

    parts = ["【以下是从 TMDB 电影知识库检索到的参考资料】"]
    refs = []

    for i, doc in enumerate(docs, 1):
        name = doc.metadata.get("movie_name", "未知")
        year = doc.metadata.get("year", "未知")
        rating = doc.metadata.get("rating", "未知")
        genre = doc.metadata.get("genre", "未知")
        refs.append((name, year, rating, genre))
        parts.append(f"\n[参考{i}] {name} ({year}) 类型:{genre} 评分:{rating}")
        parts.append(doc.page_content[:300])

    parts.append("\n【请根据以上参考资料回答用户问题】")
    return "\n".join(parts), refs


def build_prompt(nick: str, character: str, context: str) -> str:
    """构建包含 RAG 上下文的系统提示词"""
    base = f"昵称:{nick}  性格:{character}"
    if context:
        base += f"\n\n{context}"
        base += "\n请根据参考资料回答。如资料不足可结合知识补充。"
    return base
