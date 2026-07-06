"""models.py — 数据模型"""


class StuGrade:
    """学生成绩数据类"""

    def __init__(self, s_name: str, s_chinese: int, s_math: int, s_english: int):
        self.name = s_name
        self.chinese = s_chinese
        self.math = s_math
        self.english = s_english

    def __str__(self) -> str:
        total = self.chinese + self.math + self.english
        return (
            f"姓名：{self.name} | 语文：{self.chinese} | "
            f"数学：{self.math} | 英语：{self.english} | 总分：{total}"
        )

    def update(self, chinese: int | None = None, math: int | None = None, english: int | None = None) -> None:
        """修改成绩（仅更新传入的科目）。"""
        if chinese is not None:
            self.chinese = chinese
        if math is not None:
            self.math = math
        if english is not None:
            self.english = english
