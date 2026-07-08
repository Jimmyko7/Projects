"""routers/ai.py — AI 成绩分析端点（v2.1 新增）

调用 DeepSeek API 对单个学生成绩进行智能分析。
未配置 DEEPSEEK_API_KEY 时自动降级为本地规则分析。
"""
import os
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

_PARENT = Path(__file__).resolve().parent.parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

from repository import StudentRepository
from backend.schemas import AIAnalyzeRequest, AIAnalyzeResponse

router = APIRouter(prefix="/api/v1/ai", tags=["AI 分析"])
repo = StudentRepository()

LLM_MODEL = "deepseek-chat"
LLM_BASE_URL = "https://api.deepseek.com"


def _build_prompt(name: str, chinese: int, math: int, english: int, question: str | None) -> str:
    """构建成绩分析 prompt。"""
    total = chinese + math + english
    avg = total / 3
    default_dimensions = "1. 各科强弱项对比 2. 偏科情况 3. 针对性提升建议 4. 总体评价"
    return (
        f"你是一位资深的教育数据分析师。请分析以下学生的成绩：\n\n"
        f"姓名：{name}\n"
        f"语文：{chinese} | 数学：{math} | 英语：{english}\n"
        f"总分：{total}/300 | 平均分：{avg:.1f}\n\n"
        f"{'用户问题：' + question if question else '请从以下维度分析：'}"
        f"{default_dimensions if not question else ''}\n\n"
        f"要求：分析简洁专业，建议具体可操作，不超过 300 字。"
    )


def _local_analysis(name: str, chinese: int, math: int, english: int) -> str:
    """本地规则分析——LLM 不可用时的降级方案。"""
    total = chinese + math + english
    avg = total / 3
    scores = {"语文": chinese, "数学": math, "英语": english}
    best = max(scores, key=scores.get)
    worst = min(scores, key=scores.get)

    if avg >= 85:
        level, advice = "优秀", "保持当前学习节奏，可适当拓展竞赛或深度学习内容。"
    elif avg >= 70:
        level, advice = "良好", f"重点关注{worst}科目，建议每天额外投入30分钟针对性练习。"
    else:
        level, advice = f"需努力", f"建议从{worst}基础抓起，制定每日学习计划，定期自测巩固。"

    return (
        f"【成绩概览】总分{total}/300，平均分{avg:.1f}，等级：{level}。\n"
        f"【强弱项】优势科目：{best}({scores[best]}分)；薄弱科目：{worst}({scores[worst]}分)。\n"
        f"【提升建议】{advice}\n"
        f"【说明】当前为本地规则分析（未配置 DEEPSEEK_API_KEY），"
        f"设置环境变量后可获得更细致的 AI 分析。"
    )


@router.post("/analyze/{name}", response_model=AIAnalyzeResponse)
def ai_analyze_student(name: str, body: AIAnalyzeRequest | None = None):
    """AI 成绩分析——对指定学生生成个性化学习建议。

    优先使用 DeepSeek LLM 生成分析；
    未配置 DEEPSEEK_API_KEY 时自动降级为本地规则分析。

    示例：
      POST /api/v1/ai/analyze/张三
      POST /api/v1/ai/analyze/张三  {"question": "他的数学还有救吗？"}
    """
    s = repo.find_by_name(name)
    if s is None:
        raise HTTPException(status_code=404, detail=f"学生 '{name}' 不存在")

    question = body.question if body else None
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    model_used = LLM_MODEL if api_key else "local-rules"

    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=LLM_BASE_URL)
            prompt = _build_prompt(name, s.chinese, s.math, s.english, question)
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "你是一位资深教育数据分析师。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
            )
            analysis = response.choices[0].message.content
        except Exception as e:
            analysis = (
                f"[AI 调用失败: {type(e).__name__}] {e}\n\n"
                + _local_analysis(name, s.chinese, s.math, s.english)
            )
            model_used = "local-rules (fallback after error)"
    else:
        analysis = _local_analysis(name, s.chinese, s.math, s.english)

    return AIAnalyzeResponse(
        student_name=name,
        chinese=s.chinese, math=s.math, english=s.english,
        total=s.chinese + s.math + s.english,
        analysis=analysis,
        model=model_used,
    )
