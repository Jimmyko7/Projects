"""
=============================================================================
03.RAG电影问答.py — 命令行 RAG 电影问答系统
=============================================================================

功能：完整的 RAG（检索增强生成）问答流水线
  - 用户提问 → 向量检索 → 格式化上下文 → LLM 生成答案
  - 展示两种实现方式：手动组装 + LangChain LCEL 声明式链
  - 支持交互式多轮问答

使用前提：
  1. 已运行 01.电影知识库构建.py 生成 chroma_db/
  2. 已配置 DEEPSEEK_API_KEY + DASHSCOPE_API_KEY 环境变量

使用方式：
  python "03.RAG电影问答.py"

RAG-Agent 对照：
  参考 Chapter03/26（向量检索构建提示词）+ Chapter03/27（RunnablePassthrough LCEL）
=============================================================================
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore", message=".*langchain-community.*is being sunset.*")
# 屏蔽 langchain-community 弃用警告（因 langchain-dashscope 尚未适配 langchain-core 1.x）
from langchain_community.vectorstores import Chroma


from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from openai import OpenAI

from config import CHROMA_DIR, RETRIEVAL_K, LLM_MODEL, LLM_BASE_URL
from rag_engine import load_vector_store, get_retrieval_k

RAG_SYSTEM_PROMPT = """你是一个专业的电影顾问。请严格依据以下参考资料回答用户问题。

【参考资料】
{context}

【回答规则】
1. 优先使用参考资料中的信息
2. 列出相关电影的名称、年份、评分和简介
3. 如果参考资料不足以回答问题，如实说明
4. 回答简洁专业，不编造信息"""


def verify_environment():
    """验证环境配置"""
    errors = []
    if not os.environ.get("DASHSCOPE_API_KEY"):
        errors.append("DASHSCOPE_API_KEY")
    if not os.environ.get("DEEPSEEK_API_KEY"):
        errors.append("DEEPSEEK_API_KEY")
    if not os.path.exists(CHROMA_DIR):
        errors.append("chroma_db/ (请先运行 01.电影知识库构建.py)")
    if errors:
        print("ERROR: " + ", ".join(errors))
        sys.exit(1)


def create_llm_client() -> OpenAI:
    """创建 DeepSeek 客户端"""
    return OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url=LLM_BASE_URL,
    )


# ═══════════ 方式一：手动组装 RAG 流水线 ═══════════

def format_docs(docs: list[Document]) -> str:
    """将检索到的 Document 格式化为上下文字符串"""
    if not docs:
        return "无相关参考资料"
    parts = []
    for i, doc in enumerate(docs, 1):
        name = doc.metadata.get("movie_name", "未知")
        year = doc.metadata.get("year", "未知")
        rating = doc.metadata.get("rating", "未知")
        duration = doc.metadata.get("duration", "未知")
        parts.append(
            f"[参考{i}] {name} ({year}) 时长:{duration} 评分:{rating}"
        )
        parts.append(doc.page_content)
        parts.append("")
    return "\n".join(parts)


def rag_query_manual(query: str, vector_store: Chroma, client: OpenAI) -> tuple[str, list]:
    """
    手动组装 RAG 流水线

    步骤: 检索 → 格式化 → 构建提示词 → LLM生成
    """
    docs = vector_store.similarity_search(query, k=get_retrieval_k(query))
    context = format_docs(docs)

    movie_refs = [
        (d.metadata.get("movie_name", "?"),
         d.metadata.get("year", "?"),
         d.metadata.get("rating", "?"))
        for d in docs
    ]

    system_prompt = RAG_SYSTEM_PROMPT.format(context=context)
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            stream=False,
        )
        return response.choices[0].message.content, movie_refs
    except Exception as e:
        return f"[API调用失败: {type(e).__name__}] {e}", movie_refs


# ═══════════ 方式二：LangChain LCEL 声明式链 ═══════════

def rag_query_lcel(query: str, vector_store: Chroma) -> str:
    """
    LangChain LCEL 声明式 RAG 链

    使用管道操作符构建:
      {"input": query, "context": retriever | format_docs}
      | prompt | model | StrOutputParser

    与 RAG-Agent Chapter03/27 架构一致
    """
    from langchain_community.chat_models.openai import ChatOpenAI

    model = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/v1",
        temperature=0.7,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", RAG_SYSTEM_PROMPT),
        ("user", "{input}"),
    ])

    retriever = vector_store.as_retriever(search_kwargs={"k": RETRIEVAL_K})

    chain = (
        {"input": RunnablePassthrough(), "context": retriever | format_docs}
        | prompt | model | StrOutputParser()
    )

    return chain.invoke(query)


# ═══════════ 演示函数 ═══════════

def show_demo(vector_store: Chroma, client: OpenAI):
    """演示两种 RAG 实现方式"""
    queries = [
        "推荐几部科幻电影",
        "有没有关于人工智能的电影",
        "推荐适合全家一起看的动画片",
    ]
    for query in queries:
        print(f"\n{'='*60}")
        print(f"提问: {query}")
        print(f"{'='*60}")

        docs = vector_store.similarity_search(query, k=get_retrieval_k(query))
        print("\n[检索结果]")
        for i, doc in enumerate(docs):
            print(f"  {i+1}. {doc.metadata.get('movie_name','?')} "
                  f"({doc.metadata.get('year','?')})")

        print("\n[方式一：手动组装]")
        answer, refs = rag_query_manual(query, vector_store, client)
        print(f"  {answer}")

        print("\n[方式二：LangChain LCEL]")
        try:
            answer2 = rag_query_lcel(query, vector_store)
            print(f"  {answer2}")
        except Exception as e:
            print(f"  LCEL 出错: {e}")


# ═══════════ 交互式主循环 ═══════════

def interactive_loop(vector_store: Chroma, client: OpenAI):
    """交互式 RAG 问答"""
    print("\n" + "=" * 60)
    print("RAG 电影问答 — 交互模式")
    print("=" * 60)
    print("命令: /help | /demo | /quit\n")

    while True:
        try:
            query = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        try:
            if not query:
                continue
            if query == "/quit":
                print("再见！")
                break
            elif query == "/help":
                print("""
命令:
  /help  - 帮助  /demo  - 演示  /quit  - 退出
直接输入问题:
  "推荐科幻电影"  "1994年有什么好电影"
  "宫崎骏的动画片"  "评分最高的犯罪片"
                """)
            elif query == "/demo":
                show_demo(vector_store, client)
            else:
                print("检索中...")
                docs = vector_store.similarity_search(query, k=get_retrieval_k(query))
                print(f"找到 {len(docs)} 条参考资料:")
                for i, doc in enumerate(docs):
                    print(f"  {i+1}. {doc.metadata.get('movie_name','?')} "
                          f"({doc.metadata.get('year','?')})")
                print("\nAI 回答:")
                answer, _ = rag_query_manual(query, vector_store, client)
                print(f"  {answer}\n")
        except Exception as e:
            print(f"\n[错误] {type(e).__name__}: {e}")
            print("请重试或输入 /quit 退出\n")


def main():
    print("=" * 60)
    print("RAG 电影智能问答系统")
    print("=" * 60)
    verify_environment()
    print("初始化...")
    vector_store = load_vector_store()
    client = create_llm_client()
    print("就绪！")
    interactive_loop(vector_store, client)


if __name__ == "__main__":
    main()
