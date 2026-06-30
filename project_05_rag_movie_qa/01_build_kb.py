"""
=============================================================================
01_build_kb.py — TMDB 电影向量知识库构建
=============================================================================

将 data/movies.csv（300部TMDB电影）构建为可检索的 Chroma 向量知识库。

流程：CSV加载 → Document构建 → 中文分块 → DashScope嵌入 → Chroma持久化

使用前提：设置 DASHSCOPE_API_KEY 环境变量
使用方式：python 01_build_kb.py
=============================================================================
"""

import os
import sys
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings("ignore", message=".*langchain-community.*is being sunset.*")
# 屏蔽 langchain-community 弃用警告（因 langchain-dashscope 尚未适配 langchain-core 1.x）
# LangChain 组件
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 路径配置
SCRIPT_DIR = Path(__file__).resolve().parent
MOVIE_CSV = SCRIPT_DIR.parent / "data" / "movies.csv"
CHROMA_DIR = SCRIPT_DIR / "chroma_db"

# 分块参数
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
SEPARATORS = ["\n\n", "。", "！", "？", "；", "，", "\n", " ", ""]

# Chroma 配置
COLLECTION_NAME = "tmdb_movies"
EMBEDDING_MODEL = "text-embedding-v4"


def verify_api_key():
    """验证 DashScope API Key 已配置"""
    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("=" * 60)
        print("ERROR: DASHSCOPE_API_KEY 环境变量未设置")
        print("=" * 60)
        print("\n请设置后重试：")
        print("  set DASHSCOPE_API_KEY=your-key    (CMD)")
        print('  $env:DASHSCOPE_API_KEY="your-key"  (PowerShell)')
        print("\n获取 Key: https://dashscope.console.aliyun.com/apiKey")
        sys.exit(1)
    print("DASHSCOPE_API_KEY 已配置")


def load_movies_from_csv(csv_path: str) -> pd.DataFrame:
    """从 CSV 加载电影数据并清洗"""
    print(f"\n加载电影数据: {csv_path}")

    if not os.path.exists(csv_path):
        print(f"文件不存在: {csv_path}")
        print("   请确保 data/movies.csv 存在（可运行 project_02_web_scraper 获取）")
        sys.exit(1)

    df = pd.read_csv(csv_path, encoding="utf-8")
    print(f"   共 {len(df)} 部电影, 列: {', '.join(df.columns.tolist())}")
    df = df.fillna("未知")
    return df



def build_documents(df: pd.DataFrame) -> list[Document]:
    """
    将每部电影构建为 LangChain Document 对象

    page_content: 拼接关键文本字段用于向量嵌入
    metadata: 存储结构化字段用于过滤和展示
    """
    print("\n构建 Document 对象...")

    documents = []
    for idx, row in df.iterrows():
        parts = []
        if row.get("电影名") and row["电影名"] != "未知":
            parts.append(f"【电影名】{row['电影名']}")
        if row.get("年份") and row["年份"] != "未知":
            parts.append(f"【年份】{row['年份']}")
        if row.get("类型") and row["类型"] != "未知":
            parts.append(f"【类型】{row['类型']}")
        if row.get("导演") and row["导演"] != "未知":
            parts.append(f"【导演】{row['导演']}")
        if row.get("语言") and row["语言"] != "未知":
            parts.append(f"【语言】{row['语言']}")
        if row.get("评分") and row["评分"] != "未知":
            parts.append(f"【评分】{row['评分']}/100")
        if row.get("宣传语") and row["宣传语"] != "未知":
            parts.append(f"【宣传语】{row['宣传语']}")
        if row.get("简介") and row["简介"] not in ("未知", "简介"):
            parts.append(f"【简介】{row['简介']}")

        page_content = "\n".join(parts)

        metadata = {
            "source": "tmdb_top300",
            "movie_name": str(row.get("电影名", "未知")),
            "year": str(row.get("年份", "未知")),
            "genre": str(row.get("类型", "未知")),
            "director": str(row.get("导演", "未知")),
            "language": str(row.get("语言", "未知")),
            "rating": str(row.get("评分", "未知")),
        }

        documents.append(Document(page_content=page_content, metadata=metadata))

    print(f"   生成 {len(documents)} 个 Document")
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """文本分割：将长文档切分为适合嵌入的小块"""
    print("\n文本分割...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
        length_function=len,
        is_separator_regex=False,
    )

    split_docs = splitter.split_documents(documents)
    print(f"   分割前: {len(documents)}, 分割后: {len(split_docs)} 个 Chunk")

    if split_docs:
        print(f"\n   样本 Chunk ({len(split_docs[0].page_content)}字符):")
        print(f"   {split_docs[0].page_content[:200]}...")

    return split_docs


# Windows 文件删除重试参数
_MAX_RMDIR_RETRIES = 3
_RMDIR_RETRY_DELAY = 1.0


def _rmtree_onerror(func, path, exc_info) -> None:
    """shutil.rmtree 错误回调：处理 Windows 文件锁定，重试后仍失败则抛出。"""
    import time

    for attempt in range(_MAX_RMDIR_RETRIES):
        time.sleep(_RMDIR_RETRY_DELAY)
        try:
            func(path)
            return
        except OSError:
            if attempt == _MAX_RMDIR_RETRIES - 1:
                raise


def _cleanup_old_collection() -> None:
    """清理旧的 ChromaDB collection。

    优先使用 chromadb API（正确关闭 SQLite 句柄），
    失败时回退到文件系统删除并带重试（处理 Windows 文件锁定）。
    """
    if not os.path.exists(CHROMA_DIR) or not os.listdir(CHROMA_DIR):
        return

    # 方式一：通过 chromadb API 删除 collection
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            client.delete_collection(COLLECTION_NAME)
            print("   已通过 ChromaDB API 清空旧向量库")
            return
        except ValueError:
            # Collection 不存在，回退到文件系统删除
            pass
        finally:
            del client
    except ImportError:
        pass

    # 方式二：文件系统删除（Windows 文件锁定重试）
    import shutil

    shutil.rmtree(CHROMA_DIR, onerror=_rmtree_onerror)
    print("   已清空旧向量库")


def build_vector_store(documents: list[Document]):
    """构建 Chroma 向量数据库并持久化"""
    print(f"\n生成向量嵌入...")
    print(f"   模型: {EMBEDDING_MODEL}, Collection: {COLLECTION_NAME}")

    _cleanup_old_collection()

    embeddings = DashScopeEmbeddings(model=EMBEDDING_MODEL)
    ids = [f"movie_chunk_{i:04d}" for i in range(len(documents))]

    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        ids=ids,
    )

    count = vector_store._collection.count()
    print(f"\n构建完成！存储 {count} 个文档块, 路径: {CHROMA_DIR}")
    return vector_store


def run_quick_test(vector_store: Chroma):
    """快速检索验证"""
    print("\n" + "=" * 60)
    print("快速检索验证")
    print("=" * 60)

    queries = ["科幻冒险电影", "日本动画", "犯罪悬疑", "励志感人"]
    for q in queries:
        print(f"\n查询: \"{q}\"")
        results = vector_store.similarity_search(q, k=2)
        for i, doc in enumerate(results):
            name = doc.metadata.get("movie_name", "?")
            print(f"   {i+1}. {name} — {doc.page_content[:80]}...")


def main():
    print("=" * 60)
    print("TMDB 电影向量知识库构建工具")
    print("=" * 60)

    verify_api_key()
    df = load_movies_from_csv(str(MOVIE_CSV))
    documents = build_documents(df)
    split_docs = split_documents(documents)
    vector_store = build_vector_store(split_docs)
    run_quick_test(vector_store)

    print("\n" + "=" * 60)
    print("完成！可运行 02/03/04 进行检索和问答")
    print("=" * 60)


if __name__ == "__main__":
    main()
