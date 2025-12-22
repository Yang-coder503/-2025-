import numpy as np
import sys
from difflib import SequenceMatcher
import tkinter as tk

def remove_empty_lines(input_file, keep_empty=False):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not keep_empty:
                lines = [l for l in lines if l.strip() != ""]
        return lines
    except FileNotFoundError:
        print(f"错误：找不到文件 '{input_file}'")
        return []
    except Exception as e:
        print(f"读取文件 '{input_file}' 出错：{str(e)}")
        return []
#对要比较的文件做预处理，去除代码中的空行

def highlight(text, is_same):
    if is_same:
        return f"\033[32m{text}\033[0m"
    else:
        return f"\033[31m{text}\033[0m"
#高亮显示两个被比较的代码文件中的相似部分，32为绿，31为红

def get_matched_ranges(lines1, lines2):
    matcher = SequenceMatcher(None, lines1, lines2)
    matches = []
    for match in matcher.get_matching_blocks():
        i, j, length = match
        if length > 0:
            matches.append((i, i + length, j, j + length))
    return matches
#使用差异比较库中的函数计算相似度，用来处理比较文件时需要高亮显示的部分

def get_statistics_inf(result, keyword, symbols=["//", "#"]):
    total_lines = len(result)
    total_chars = 0
    comments_lines = 0
    comments_chars = 0
    assign_count = 0
    loop_count = 0
    choice_count = 0
    matched_lines = []

    for l in result:
        line_without_newline = l.rstrip('\r\n')
        total_chars += len(line_without_newline)

        stripped_line = l.lstrip()
        is_comment = False
        comment_content = ""
        for s in symbols:
            if stripped_line.startswith(s):
                is_comment = True
                comment_content = stripped_line[len(s):].strip()
                break
        if is_comment:
            comments_lines += 1
            comments_chars += len(comment_content)

    for i, line in enumerate(result, start=1):
        stripped = line.lstrip()
        if "=" in stripped and "==" not in stripped:
            assign_count += 1
        if stripped.startswith(("for", "while")):
            loop_count += 1
        if stripped.startswith(("if", "elif", "else")):
            choice_count += 1
        if keyword in line:
            matched_lines.append((i, line.rstrip()))

    avg_chars_per_line = round(total_chars / total_lines, 2) if total_lines > 0 else 0
    avg_comment_chars = round(comments_chars / comments_lines, 2) if comments_lines > 0 else 0

    stat_inf = {
        "去除空行后的总行数": total_lines,
        "平均每行字符数（非空行）": avg_chars_per_line,
        "注释行数（非空行中）": comments_lines,
        "注释平均字符数": avg_comment_chars,
        "赋值语句数": assign_count,
        "循环语句数": loop_count,
        "选择语句数": choice_count,
        "包含关键字的行": matched_lines
    }

    origin_vec = [total_lines, avg_chars_per_line, comments_lines,
                  avg_comment_chars, assign_count, loop_count, choice_count]
    return stat_inf, origin_vec
#获取代码文件的统计信息，包括总行数、总字符数、注释行数、注释字符数、赋值语句数、循环语句数、选择语句数和匹配的行,并把结果返回到一个字典里

def similarity_check(vec1, vec2, w):
    vec1_np = np.array(vec1)
    vec2_np = np.array(vec2)
    weighted_diff = (vec1_np - vec2_np) * w
    distance = np.sqrt(np.sum(weighted_diff **2))
    return 1 / (1 + distance)
#相似性检查函数，把每个代码文件的特征统计量作为向量输入到函数中，通过计算他们的加权欧氏距离来判断相似程度

def print_statistics():
    print("\n----- 打印文件统计信息 -----")
    file_path = input("请输入文件路径：").strip()
    if not file_path:
        print("错误：文件路径不能为空")
        return

    lines = remove_empty_lines(file_path)
    if not lines:
        print("无法获取文件内容，统计失败")
        return

    keyword = input("请输入需要统计的关键字：").strip()
    stat_inf, _ = get_statistics_inf(lines, keyword)

    print("\n===== 统计结果 =====")
    for key, value in stat_inf.items():
        if key == "包含关键字的行":
            print(f"\n{key}：")
            if value:
                for line_num, line_content in value:
                    print(f"  第{line_num}行：{line_content}")
            else:
                print("  无匹配行")
        else:
            print(f"{key}：{value}")


def compare_files_statistical():
    print("\n----- 文件相似度比较（统计特征） -----")
    keyword = input("请输入用于特征提取的关键字：").strip()
    if not keyword:
        print("错误：关键字不能为空")
        return

    try:
        n = int(input("请输入需要比较的文件数量（大于0）：").strip())
        if n <= 0:
            print("错误：文件数量必须大于0")
            return
    except ValueError:
        print("错误：请输入有效的数字")
        return

    compare_vecs = []
    for i in range(n):
        file_path = input(f"请输入第{i+1}个比较文件的路径：").strip()
        lines = remove_empty_lines(file_path)
        if not lines:
            print(f"文件 '{file_path}' 处理失败，已跳过")
            continue
        _, vec = get_statistics_inf(lines, keyword)
        compare_vecs.append((file_path, vec))

    if not compare_vecs:
        print("没有有效的比较文件，无法进行比较")
        return

    target_path = input("请输入目标文件的路径：").strip()
    target_lines = remove_empty_lines(target_path)
    if not target_lines:
        print("目标文件处理失败，比较终止")
        return
    _, target_vec = get_statistics_inf(target_lines, keyword)

    weights = [1, 1, 1, 2, 2, 2, 1]
    similarities = [(p, similarity_check(target_vec, v, weights)) for p, v in compare_vecs]
    similarities.sort(key=lambda x: x[1], reverse=True)

    print("\n===== 统计特征相似度结果 =====")
    print(f"目标文件：{target_path}")
    print(f"最相似的文件：{similarities[0][0]}（相似度：{similarities[0][1]:.4f}）")
    print("\n所有文件相似度（从高到低）：")
    for i, (path, score) in enumerate(similarities, 1):
        print(f"{i}. {path}：{score:.4f}")
#取某代码两个文件进行比较它们的统计信息

def compare_two_files_content():
    print("\n----- 两个文件内容详细对比 -----")
    file1 = input("请输入第一个文件的路径：").strip()
    file2 = input("请输入第二个文件的路径：").strip()
    if not file1 or not file2:
        print("错误：文件路径不能为空")
        return

    lines1 = remove_empty_lines(file1, keep_empty=True)
    lines2 = remove_empty_lines(file2, keep_empty=True)
    if not lines1 or not lines2:
        print("文件读取失败，无法比较")
        return

    matched_ranges = get_matched_ranges(lines1, lines2)
    line1_is_same = [False] * len(lines1)
    line2_is_same = [False] * len(lines2)
    for i1_start, i1_end, i2_start, i2_end in matched_ranges:
        for i in range(i1_start, i1_end):
            line1_is_same[i] = True
        for i in range(i2_start, i2_end):
            line2_is_same[i] = True

    total_lines = len(lines1) + len(lines2)
    same_lines = sum(line1_is_same) + sum(line2_is_same)
    content_similarity = same_lines / total_lines if total_lines > 0 else 0

    print(f"\n===== 内容对比结果（相似度：{content_similarity:.2f}） =====")
    print(f"文件1：{file1}（共{len(lines1)}行）")
    print(f"文件2：{file2}（共{len(lines2)}行）")
    print("\n【说明】绿色表示相同内容，红色表示不同内容\n")

    print(f"----- {file1} 内容 -----")
    for i, (line, is_same) in enumerate(zip(lines1, line1_is_same)):
        stripped = line.rstrip('\n')
        highlighted = highlight(stripped, is_same)
        print(f"{i+1:4d} | {highlighted}")

    print(f"\n----- {file2} 内容 -----")
    for i, (line, is_same) in enumerate(zip(lines2, line2_is_same)):
        stripped = line.rstrip('\n')
        highlighted = highlight(stripped, is_same)
        print(f"{i+1:4d} | {highlighted}")
#找到两个代码文件的相似的行并显示

root = tk.Tk()
root.title("CodeDetectingSystem")
root.geometry("400x300")

label = tk.Label(root, text="选择以下功能",font=("微软雅黑",12))
label.pack(pady=10)

button1 = tk.Button(root, text="打印单个代码的统计信息", command=print_statistics,bg="#4CAF50",fg="white" )
button2 = tk.Button(root, text="比较若干代码文件的相似度", command=compare_files_statistical,bg="#4CAF50",fg="white" )
button3 = tk.Button(root, text="比较两个文件中的相似内容", command=compare_two_files_content,bg="#4CAF50",fg="white" )
button4 = tk.Button(root, text="终止程序", command=sys.exit, bg="#4CAF50",fg="white" )

button1.pack(pady=10)
button2.pack(pady=10)
button3.pack(pady=10)
button4.pack(pady=10)

root.mainloop()

#图形化交互界面