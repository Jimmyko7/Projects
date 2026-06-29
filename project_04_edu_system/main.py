# 采用面向对象的编程思想，完成教务管理系统的开发。教务管理系统可以管理在校学生的成绩信息，通过控制台菜单与用户交互，具体的功能如下:
# 1.添加学生成绩:根据输入的学生姓名、语文成绩、数学成绩、英语成绩，记录在系统中
# 2.修改学生成绩:根据输入的学生姓名，修改对应的学生成绩
# 3.删除学生成绩:根据输入的学生姓名，删除对应的学生成绩
# 4.查询指定学生成绩:根据输入的学生姓名，查找对应的学生成绩，并输出
# 5.展示全部学生成绩:展示出系统中所有学生的成绩

class StuGrade:
    # 定义实例方法
    def __init__(self, s_name, s_chinese, s_math, s_english):
        self.name = s_name
        self.chinese = s_chinese
        self.math = s_math
        self.english = s_english

    # 定义字符串的表示方法
    def __str__(self):
        return f"姓名：{self.name} | 语文：{self.chinese} | 数学：{self.math} | 英语：{self.english} | 总分：{self.chinese + self.math + self.english}"

    # 修改学生成绩
    def update(self, chinese=None, math=None, english=None):
        # 判断是否存在此名字
        if chinese is not None:
            self.chinese = chinese
        if math is not None:
            self.math = math
        if english is not None:
            self.english = english


class EduManagement:
    sys_version = 1.0
    sys_name = "教务管理系统"

    # 定义实例方法
    def __init__(self):
        self. stu_list = []

    # 添加学生成绩
    def add_stu(self):
        name = input("请输入要添加的学生名字：")
        for s in self.stu_list:
            if s.name == name:
                print("该学生姓名已存在！")
                return
        chinese = int(input("请输入语文成绩："))
        math = int(input("请输入数学成绩："))
        english = int(input("请输入英语成绩："))
        # 分数限制在0~100内
        if 0 <= chinese <= 100 and 0 <= math <= 100 and 0 <= english <= 100:
            stu = StuGrade(name,chinese, math, english)
            self.stu_list.append(stu)
            print("学生信息添加成功！")
        else:
            print("各科成绩必须在 0 ~ 100 之间")

    # 修改学生成绩
    def update_stu(self):
        name = input("请输入要修改的学生名字：")
        for s in self.stu_list:
            if s.name == name:
                print(f"当前成绩：{s}")
                chinese = int(input("请输入修改后的语文成绩："))
                math = int(input("请输入修改后的数学成绩："))
                english = int(input("请输入修改后的英语成绩："))
                # 分数限制在0~100内
                if 0 <= chinese <= 100 and 0 <= math <= 100 and 0 <= english <= 100:
                    s.update(chinese, math, english)
                    print("修改成功！")
                    print(f"修改后成绩：{s}")
                    return
                else:
                    print("各科成绩必须在 0 ~ 100 之间")
                    return
        print("未找到学生，修改失败！")

    # 删除学生成绩
    def delete_stu(self):
        name = input("请输入要删除的学生名字：")
        for s in self.stu_list:
            if s.name == name:
                self.stu_list.remove(s)
                print("删除成功！")
                return
        print("未找到学生，删除失败！")

    # 查询指定学生成绩
    def search_stu(self):
        name = input("请输入要查询的学生名字：")
        for s in self.stu_list:
            if s.name == name:
                print(f"学生信息：{s}")
                return
        print("未找到学生，查询失败！")

    # 展示全部学生成绩
    def display_all(self):
        for s in self.stu_list:
            print(f"{s}")

    # 运行
    def run(self):
        print(f"{self.sys_name}")
        while True:
            print("===1.添加学生成绩 2.修改学生成绩 3.删除学生成绩 4.查询指定学生成绩 5.展示全部学生成绩 6.退出系统===")
            num = int(input("请输入要执行的步骤（1~6）："))

            # 捕获异常
            try:
                match num:
                    case 1:
                        self.add_stu()
                    case 2:
                        self.update_stu()
                    case 3:
                        self.delete_stu()
                    case 4:
                        self.search_stu()
                    case 5:
                        self.display_all()
                    case 6:
                        print("退出成功！")
                        print(self.stu_list)
                        break
                    case _:
                        print("输入错误！")
                        continue
            except ValueError as e:
                print("输入的数据有问题，请检查，然后重新输入！")
            except Exception as e:
                print("程序运行错误，请联系管理员，错误信息：")
if __name__ == "__main__":

    edu = EduManagement()
    edu.run()


