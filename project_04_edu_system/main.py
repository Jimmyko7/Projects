"""
教务管理系统 — OOP + SQLite 持久化

架构：StuGrade (Model) → StudentRepository (数据层) → EduManagement (业务+菜单)

功能：
  1. 添加学生成绩    2. 修改学生成绩    3. 删除学生成绩
  4. 查询指定学生    5. 展示全部学生    6. 退出系统
"""

import sys
from pathlib import Path

# 确保从任意目录运行都能找到同目录模块
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from models import StuGrade
from repository import StudentRepository
from database import init_db


class EduManagement:
    """教务管理系统 — 业务逻辑 + 控制台菜单"""

    sys_version = 1.1
    sys_name = "教务管理系统（SQLite 版）"

    def __init__(self, repo: StudentRepository):
        self.repo = repo

    # ── 添加 ──────────────────────────────────────────
    def add_stu(self) -> None:
        name = input("请输入要添加的学生名字：")
        try:
            chinese = int(input("请输入语文成绩："))
            math = int(input("请输入数学成绩："))
            english = int(input("请输入英语成绩："))
        except ValueError:
            print("成绩必须为数字，请重新输入！")
            return

        if not (0 <= chinese <= 100 and 0 <= math <= 100 and 0 <= english <= 100):
            print("各科成绩必须在 0 ~ 100 之间")
            return

        try:
            self.repo.add(name, chinese, math, english)
            print("学生信息添加成功！")
        except ValueError as e:
            print(e)

    # ── 修改 ──────────────────────────────────────────
    def update_stu(self) -> None:
        name = input("请输入要修改的学生名字：")
        existing = self.repo.find_by_name(name)
        if existing is None:
            print("未找到学生，修改失败！")
            return

        print(f"当前成绩：{existing}")
        try:
            chinese = int(input("请输入修改后的语文成绩："))
            math = int(input("请输入修改后的数学成绩："))
            english = int(input("请输入修改后的英语成绩："))
        except ValueError:
            print("成绩必须为数字，请重新输入！")
            return

        if not (0 <= chinese <= 100 and 0 <= math <= 100 and 0 <= english <= 100):
            print("各科成绩必须在 0 ~ 100 之间")
            return

        self.repo.update(name, chinese, math, english)
        updated = self.repo.find_by_name(name)
        print("修改成功！")
        print(f"修改后成绩：{updated}")

    # ── 删除 ──────────────────────────────────────────
    def delete_stu(self) -> None:
        name = input("请输入要删除的学生名字：")
        if self.repo.delete(name):
            print("删除成功！")
        else:
            print("未找到学生，删除失败！")

    # ── 查询 ──────────────────────────────────────────
    def search_stu(self) -> None:
        name = input("请输入要查询的学生名字：")
        stu = self.repo.find_by_name(name)
        if stu:
            print(f"学生信息：{stu}")
        else:
            print("未找到学生，查询失败！")

    # ── 展示全部 ──────────────────────────────────────
    def display_all(self) -> None:
        students = self.repo.list_all()
        if not students:
            print("暂无学生成绩记录！")
            return
        for s in students:
            print(s)

    # ── 主菜单 ────────────────────────────────────────
    def run(self) -> None:
        init_db()
        print(f"{self.sys_name} v{self.sys_version}")
        while True:
            print(
                "=== 1.添加 2.修改 3.删除 4.查询 5.展示全部 6.退出 ==="
            )
            try:
                num = int(input("请输入要执行的步骤（1~6）："))
                match num:
                    case 1: self.add_stu()
                    case 2: self.update_stu()
                    case 3: self.delete_stu()
                    case 4: self.search_stu()
                    case 5: self.display_all()
                    case 6:
                        print("退出成功！")
                        break
                    case _:
                        print("输入错误！")
            except ValueError:
                print("输入的数据有问题，请检查，然后重新输入！")
            except Exception as e:
                print(f"程序运行错误，请联系管理员，错误信息：{e}")


if __name__ == "__main__":
    repo = StudentRepository()
    edu = EduManagement(repo)
    edu.run()
