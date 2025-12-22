
import json
import re

class task_information:

    def __init__(self,task_name,task_description,task_priority,task_deadline):
        self.task_name = task_name
        self.task_description = task_description
        self.task_priority = task_priority
        self.task_deadline = task_deadline

    def show_task_info(self):
        return f"任务名称：{self.task_name} 任务描述{self.task_description} 任务优先级{self.task_priority} 任务截止日期{self.task_deadline}"

class task_management_system():

    def __init__(self):
        self.tasks = {}

    def deadline_to_tuple(self, date_str):
        parts = date_str.split('-')
        return (int(parts[0]), int(parts[1]), int(parts[2]))

    def add_task(self,task_name,task_description,task_priority,task_deadline):
        new_task = task_information(task_name,task_description,task_priority,task_deadline)
        self.tasks[task_name] = (new_task)

    def remove_task(self,task_name):
            if task_name in self.tasks:
                del self.tasks[task_name]
                print("任务{task_name}已删除")
            else :
                print("找不到该任务")

    def query_task(self,task_name=None,task_deadline=None):
        results = []
        for  task in self.tasks.values():
           if task_name is None and task_deadline is None:
               results.append(task)
           elif task_name is not None and task.task_name == task_name:
               results.append(task)
           elif task_deadline is not None and task.task_deadline < task_deadline:
               results.append(task)
        return results

#定义一个重设任务名称的类的方法，将新的任务参数设置为None，结合if语句更新原来的任务参数

    def reset_task(self,old_task_name,task_description,task_priority,task_deadline
                   ,new_task_name=None,new_task_description=None,new_task_priority=None,new_task_deadline=None):

        if old_task_name not in self.tasks:
            print(f"任务'{old_task_name}'不存在")
            return
        task = self.tasks[old_task_name]

        # 更新任务名称
        if new_task_name and new_task_name != old_task_name:
            del self.tasks[old_task_name]
            task.task_name = new_task_name
            self.tasks[new_task_name] = task  # 用新名称作为键
            print("任务名称已更新")

        # 更新任务描述
        if new_task_description is not None:
            task.task_description = new_task_description
            print("任务描述已更新")

        # 更新优先级（验证范围）
        if new_task_priority is not None:
            if 1 <= new_task_priority <= 5:
                task.task_priority = new_task_priority
                print("任务优先级已更新")
            else:
                print("优先级必须在1-5之间，更新失败")

        # 更新截止日期（简化验证，可复用 input_task_deadline 的逻辑）
        if new_task_deadline:
            date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
            if date_pattern.match(new_task_deadline):
                year, month, day = map(int, new_task_deadline.split('-'))
                if 1 <= month <= 12 and 1 <= day <= 31:
                    task.task_deadline = new_task_deadline
                    print("任务截止日期已更新")
                else:
                    print("日期无效，更新失败")
            else:
                print("日期格式错误，更新失败")

#定义一个查找任务的类的方法，默认根据优先级查找，将优先级设置为True，如果想通过时间查找，则需要在使用时给方法传入None参数

    def check_task_list(self,sort_by_priority=True):

        task_list = list(self.tasks.values())

        if sort_by_priority:
            task_list.sort(key=lambda x: x.task_priority, reverse=True)

        else:
            task_list.sort(key=lambda x: self.deadline_to_tuple(x.task_deadline))

#这里使用for循环遍历task列表里的任务和任务优先级并将其打印出来

        for priority_index , task in enumerate(task_list,1):
            print(f"任务{priority_index}:")
            print(task.show_task_info())
            print("-"*50)

    def write_to_file(self,file_name):
        task_list = []
        for task in self.tasks.values():
            task_dict = {
                "task_name" : task.task_name,
                "task_description" : task.task_description,
                "task_priority" : task.task_priority,
                "task_deadline" : task.task_deadline
            }
            task_list.append(task_dict)

        with open(file_name,'w',encoding = "utf-8") as f:
            json.dump(task_list,f,ensure_ascii=False,indent=4)

        print("任务已保存到{file_name}")

def input_task_name():
        while True:
            task_name = input("请输入任务名称（不能为空）：").strip()
            if task_name:
                return task_name
            print("任务名称不能为空，请重新输入！")

def input_task_description():
        desc = input("请输入任务描述（可不填，直接回车则为'无'）：").strip()
        return desc if desc else "无"

def input_task_priority():
        while True:
            priority_input = input("请输入任务优先级（1-5，数字越大优先级越高）：").strip()
            if priority_input.isdigit():
                priority = int(priority_input)
                if 1 <= priority <= 5:
                    return priority
                print("优先级必须是1-5之间的整数，请重新输入！")
            else:
                print("优先级必须是数字，请重新输入！")

def input_task_deadline():
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        while True:
            deadline = input("请输入任务截止日期（格式：YYYY-MM-DD，例如2025-12-31）：").strip()
            if date_pattern.match(deadline):
                year, month, day = map(int, deadline.split('-'))
                if 1 <= month <= 12 and 1 <= day <= 31:
                    return deadline
                print("日期无效（月份需1-12，日期需1-31），请重新输入！")
            else:
                print("日期格式错误，请使用YYYY-MM-DD格式（例如2025-12-31）！")

#定义一个用户交互界面的类的方法，使用者可以方便地对任务管理系统进行操作

def user_interaction():

                tms = task_management_system()
                print("=" * 50)
                print("欢迎使用任务管理系统！")
                print("=" * 50)

#默认开启交互界面

                while True:
                    print("\n请选择操作（输入数字）：")
                    print("1. 添加新任务")
                    print("2. 删除任务")
                    print("3. 查询任务")
                    print("4. 修改任务")
                    print("5. 查看所有任务（按优先级排序）")
                    print("6. 查看所有任务（按截止日期排序）")
                    print("7. 保存任务到文件")
                    print("8. 退出系统")

                    choice = input("请输入操作编号（1-8）：").strip()

                    if choice == '1':
                        print("\n----- 添加新任务 -----")
                        task_name = input_task_name()
                        task_desc = input_task_description()
                        task_priority = input_task_priority()
                        task_deadline = input_task_deadline()
                        tms.add_task(task_name, task_desc, task_priority, task_deadline)

                    elif choice == '2':
                        print("\n----- 删除任务 -----")
                        task_name = input("请输入要删除的任务名称：").strip()
                        tms.remove_task(task_name)

                    elif choice == '3':
                        print("\n----- 查询任务 -----")
                        query_by = input("请选择查询方式（1-按名称，2-按截止日期，3-查询所有）：").strip()
                        if query_by == '1':
                            name = input("请输入要查询的任务名称：").strip()
                            results = tms.query_task(task_name=name)
                        elif query_by == '2':
                            date = input("请输入要查询的截止日期（YYYY-MM-DD）：").strip()
                            results = tms.query_task(task_deadline=date)
                        elif query_by == '3':
                            results = tms.query_task()
                        else:
                            print("无效的查询方式")
                            continue

                        if results:
                            print(f"\n查询到{len(results)}个任务：")
                            for task in results:
                                print("-" * 40)
                                print(task.show_task_info())
                        else:
                            print("未查询到匹配的任务")

                    elif choice == '4':
                        print("\n----- 修改任务 -----")
                        old_name = input("请输入要修改的任务名称：").strip()
                        if old_name not in tms.tasks:
                            print(f"任务'{old_name}'不存在，无法修改")
                            continue

                        print("请输入新的属性（不修改的项直接回车）：")
                        new_name = input("新任务名称：").strip() or None
                        new_desc = input("新任务描述：").strip() or None
                        new_priority_input = input("新优先级（1-5）：").strip()
                        new_priority = int(new_priority_input) if new_priority_input.isdigit() else None
                        new_deadline = input("新截止日期（YYYY-MM-DD）：").strip() or None
                        if new_deadline and not re.match(r'^\d{4}-\d{2}-\d{2}$', new_deadline):
                            print("截止日期格式错误，已忽略该修改")
                            new_deadline = None

                        tms.reset_task(old_name, new_name, new_desc, new_priority, new_deadline)

                    elif choice == '5':
                        tms.check_task_list(sort_by_priority=True)

                    elif choice == '6':
                        tms.check_task_list(sort_by_priority=False)

                    elif choice == '7':
                        file_name = input("请输入保存的文件名（例如tasks.json）：").strip() or "tasks.json"
                        tms.write_to_file(file_name)

                    elif choice == '8':
                        print("\n感谢使用，再见！")
                        break

                    else:
                        print("无效的操作编号，请输入1-8之间的数字！")


if __name__ == "__main__":
    user_interaction()




















