"""
rag_engine.py — RAG 检索引擎（CLI 和 Streamlit 共用）

职责：向量库加载 / 语义检索 / 上下文格式化 / 提示词构建
"""

import os
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma

from config import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, RETRIEVAL_K, RANKING_K

_RANKING_KEYWORDS = [
    "最", "排名", "排行", "top", "前几", "前5", "前10",
    "哪部最", "哪个最", "最长", "最短", "最高", "最低",
    "多少部", "几部", "几部电影", "列出", "有哪些",
]

# 数值字段名 → 从 metadata 提取的 key
_RANKING_FIELDS: dict[str, str] = {
    "评分": "rating",
    "年份": "year",
}


def _parse_duration_minutes(duration_str: str) -> int:
    """将 '3h 48m' 格式转换为分钟数。"""
    total = 0
    parts = str(duration_str).lower().split()
    for part in parts:
        if part.endswith("h"):
            try:
                total += int(part[:-1]) * 60
            except ValueError:
                pass
        elif part.endswith("m"):
            try:
                total += int(part[:-1])
            except ValueError:
                pass
    return total


def _detect_ranking_field(query: str) -> str | None:
    """检测查询涉及的排序字段。"""
    for keyword, field in _RANKING_FIELDS.items():
        if keyword in query:
            return field
    if "时长" in query:
        return "duration"
    return None


def _sort_docs_by_field(
    docs: list, field: str, reverse: bool = True
) -> list:
    """按 metadata 字段排序 Document 列表。"""
    def _key(doc):
        value = doc.metadata.get(field, "0" if field != "duration" else "0m")
        if field == "duration":
            return _parse_duration_minutes(value)
        if field == "rating":
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        if field == "year":
            try:
                return int(value)
            except (ValueError, TypeError):
                return 0
        return 0

    return sorted(docs, key=_key, reverse=reverse)


def _fetch_top_by_field(vector_store, field: str, top_k: int) -> list:
    """从 ChromaDB 全量拉取，按 metadata 字段排序取 top-K。

    绕过语义检索的召回盲区——保证数值极值一定被找到。
    仅用于 rating / year / duration 这类可排序字段。
    """
    from langchain_core.documents import Document as LCDocument

    try:
        raw = vector_store._collection.get(
            include=["documents", "metadatas"],
            limit=9999,  # ChromaDB 默认 limit 可能不够，显式设大
        )
    except Exception:
        return []

    if not raw or not raw["ids"]:
        return []

    docs = []
    for doc_id, content, meta in zip(
        raw["ids"], raw["documents"], raw["metadatas"]
    ):
        if content is None:
            content = ""
        meta = meta or {}
        docs.append(LCDocument(id=doc_id, page_content=content, metadata=meta))

    return _sort_docs_by_field(docs, field)[:top_k]


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


def _is_ranking_query(query: str) -> bool:
    """检测是否为排序/极值/列举类查询，这类查询需要更多候选才能准确回答。"""
    query_lower = query.lower()
    return any(kw in query_lower for kw in _RANKING_KEYWORDS)


def get_retrieval_k(query: str) -> int:
    """根据查询意图返回合适的检索数量。"""
    return RANKING_K if _is_ranking_query(query) else RETRIEVAL_K


def retrieve_docs(query: str, vector_store, k: int | None = None) -> list:
    """智能检索：动态 K + 极值全量排序，返回 Document 列表。

    所有调用方（CLI / Streamlit）统一走此入口，避免绕过排序逻辑。
    """
    if vector_store is None:
        return []

    if k is None:
        k = get_retrieval_k(query)

    is_ranking = _is_ranking_query(query)
    ranking_field = _detect_ranking_field(query) if is_ranking else None

    docs = vector_store.similarity_search(query, k=k)

    # 极值查询：全量拉取 + 数值排序，确保真正的极值一定在结果中
    if ranking_field and ranking_field in ("rating", "year", "duration"):
        extreme_docs = _fetch_top_by_field(
            vector_store, ranking_field, top_k=5
        )
        seen_names = {d.metadata.get("movie_name") for d in docs}
        for ed in extreme_docs:
            if ed.metadata.get("movie_name") not in seen_names:
                docs.append(ed)
                seen_names.add(ed.metadata.get("movie_name"))
        docs = _sort_docs_by_field(docs, ranking_field)
    elif ranking_field:
        docs = _sort_docs_by_field(docs, ranking_field)

    return docs


def search_movies(query: str, vector_store, k: int | None = None) -> tuple[str, list]:
    """
    语义检索电影知识库。

    k 为 None 时根据查询意图自动选择检索数量。
    返回:
        (上下文字符串, [(片名,年份,评分,类型,时长,主演), ...])
    """
    docs = retrieve_docs(query, vector_store, k)
    if not docs:
        return "", []

    parts = ["【以下是从 TMDB 电影知识库检索到的参考资料】"]
    refs = []

    for i, doc in enumerate(docs, 1):
        name = doc.metadata.get("movie_name", "未知")
        year = doc.metadata.get("year", "未知")
        rating = doc.metadata.get("rating", "未知")
        genre = doc.metadata.get("genre", "未知")
        duration = doc.metadata.get("duration", "未知")
        cast = doc.metadata.get("cast", "未知")
        refs.append((name, year, rating, genre, duration, cast))
        parts.append(
            f"\n[参考{i}] {name} ({year}) 类型:{genre} "
            f"时长:{duration} 评分:{rating}"
        )
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
