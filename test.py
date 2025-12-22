from collections import Counter #统计文本中各个字符的词频，返回对应的字典
import heapq

"""class MinHeap:
    def __init__(self, data=None):
        # 私有列表存储堆元素（数组模拟完全二叉树）
        self._heap = []
        if data is not None and isinstance(data, list):
            self._heap = data.copy()  # 避免修改原列表
            # 堆化：从最后一个非叶子节点开始向下调整
            # 最后一个非叶子节点索引 = (元素个数-2) // 2
            for i in range((len(self._heap) - 2) // 2, -1, -1):
                self._sift_down(i)

    def _sift_up(self, idx):
        # 父节点索引 = (当前索引 - 1) // 2
        parent_idx = (idx - 1) // 2
        # 若当前节点 < 父节点，交换并继续向上调整
        while idx > 0 and self._heap[idx] < self._heap[parent_idx]:
            self._heap[idx], self._heap[parent_idx] = self._heap[parent_idx], self._heap[idx]
            idx = parent_idx
            parent_idx = (idx - 1) // 2

    def _sift_down(self, idx):
        heap_size = len(self._heap)
        while True:
            # 初始化最小元素索引为当前节点
            min_idx = idx
            # 左子节点索引 = 2*idx + 1
            left_idx = 2 * idx + 1
            # 右子节点索引 = 2*idx + 2
            right_idx = 2 * idx + 2

            # 若左子节点存在且更小，更新最小索引
            if left_idx < heap_size and self._heap[left_idx] < self._heap[min_idx]:
                min_idx = left_idx
            # 若右子节点存在且更小，更新最小索引
            if right_idx < heap_size and self._heap[right_idx] < self._heap[min_idx]:
                min_idx = right_idx

            # 若最小索引就是当前节点，说明已满足堆性质，终止调整
            if min_idx == idx:
                break
            # 否则交换当前节点和最小子节点，继续向下调整
            self._heap[idx], self._heap[min_idx] = self._heap[min_idx], self._heap[idx]
            idx = min_idx

    def push(self, item):
        # 1. 先将元素追加到堆的末尾
        self._heap.append(item)
        # 2. 向上调整最后一个元素（新插入的元素）
        self._sift_up(len(self._heap) - 1)

    def pop(self)
        if self.is_empty():
            raise IndexError("pop from empty min-heap")
        # 1. 交换堆顶（第一个元素）和堆尾（最后一个元素）
        self._heap[0], self._heap[-1] = self._heap[-1], self._heap[0]
        # 2. 弹出堆尾（原堆顶）
        min_item = self._heap.pop()
        # 3. 向下调整新的堆顶元素
        if not self.is_empty():
            self._sift_down(0)
        return min_item

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty min-heap")
        return self._heap[0]

    def is_empty(self):
        return len(self._heap) == 0

    def size(self):
        return len(self._heap)

    def __str__(self):
        return f"MinHeap({self._heap})"
"""
class Node:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    # 最小堆中依据节点的频率进行排序
    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(freq_dict):
    # 创建一个堆，初始放入每个字符节点
    heap = []
    for char, freq in freq_dict.items():
        heap.append(Node(char, freq))
    heapq.heapify(heap)

    # 如果只有一个字符, 直接返回该节点作为根节点
    if len(heap) == 1:
        only_node = heapq.heappop(heap)
        return Node(None, only_node.freq, left=only_node, right=None)

    # 不断合并频率最低的两个节点，直到堆中只有一个节点
    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = Node(None, n1.freq + n2.freq, left=n1, right=n2)
        heapq.heappush(heap, merged)
    return heap[0]


def calculate_wlp(root):
    def dfs(node, depth):
        if node is None:
            return 0

        if node.left is None and node.right is None:
            return node.freq * depth

        left_wpl = dfs(node.left, depth + 1)
        right_wpl = dfs(node.right, depth + 1)

        return left_wpl + right_wpl

    return dfs(root, 0)
#计算哈夫曼树的wpl值

def print_huffman_tree(node, indent="", prefix="root", is_last=True):
    #indent控制缩进，prefix为当前节点的前缀标识
    if node is None:
        return

    node_label = f"{node.char if node.char is not None else 'None'}({node.freq})"

    connector = "└── " if is_last else "├── "
    print(indent + prefix + connector + node_label)

    child_indent = indent + ("    " if is_last else "│   ")

    children = []
    if node.left:
        children.append((node.left, "left", False))
    if node.right:
        children.append((node.right, "right", True))

    for i, (child, child_prefix, child_is_last) in enumerate(children):
        actual_is_last = child_is_last if len(children) == 1 else (i == len(children) - 1)
        print_huffman_tree(child, child_indent, child_prefix, actual_is_last)
    #图形化哈夫曼树

def generate_codes(node, prefix="", code_map=None):
    if code_map is None:
        code_map = {}
    if node is None:
        return code_map
    if node.char is not None:
        code_map[node.char] = prefix if prefix != "" else "0"  #非叶子节点的char为none,存储该节点代表的字符
    else:
        generate_codes(node.left, prefix + "0", code_map)
        generate_codes(node.right, prefix + "1", code_map)
    return code_map
    #递归生成哈夫曼编码，左为0，右为1

def encode_file(input_path, encoded_path, table_path):
    # 读取文本并统计各字符频率
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()
    freq = Counter(text)  # 使用Counter统计字符出现频率
    if len(freq) == 0:
        print("输入文件为空。")
        return

    # 构建Huffman树并生成编码表
    root = build_huffman_tree(freq)

    # 计算并打印WPL值
    wpl_value = calculate_wlp(root)
    print(f"\n哈夫曼树的带权路径长度(WPL): {wpl_value}")

    # 打印哈夫曼树结构
    print("\n哈夫曼树结构:")
    print_huffman_tree(root)

    # 生成编码表
    code_map = generate_codes(root)

    # 打印编码表
    print("\n生成的哈夫曼编码表:")
    for char, code in sorted(code_map.items(), key=lambda x: len(x[1]) if x[1] else 0):
        # 特殊字符显示处理
        char_display = repr(char) if char in ['\n', '\t', ' ', '\r'] else char
        print(f"  {char_display}: {code}")

    # 对文本进行Huffman编码
    encoded_bits = "".join(code_map[ch] for ch in text)
    # 将编码后的比特串保存到输出文件
    with open(encoded_path, 'w', encoding='utf-8') as f:
        f.write(encoded_bits)
    # 将编码表保存到文件
    with open(table_path, 'w', encoding='utf-8') as f:
        for ch, code in code_map.items():
            f.write(f"{ord(ch)} {code}\n")
    print(f"\n编码完成: 编码文件 {encoded_path}, 编码表 {table_path}")
    # 输出压缩相关信息
    original_size = len(text) * 8  # 原始字节数
    encoded_size = len(encoded_bits)
    compression_ratio = (1 - encoded_size / original_size) * 100 if original_size > 0 else 0
    print(f"压缩信息: 原始大小 {original_size} 比特, 编码后大小 {encoded_size} 比特, 压缩率 {compression_ratio:.2f}%")


def decode_file(encoded_path, table_path, decoded_path):
    # 读取编码表
    code_map = {}
    with open(table_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            char_code = int(parts[0])
            code = parts[1]
            code_map[chr(char_code)] = code
    if not code_map:
        print("编码表为空或格式无效。")
        return

    # 打印解码使用的编码表
    print("\n解码使用的编码表:")
    for char, code in sorted(code_map.items(), key=lambda x: len(x[1]) if x[1] else 0):
        char_display = repr(char) if char in ['\n', '\t', ' ', '\r'] else char
        print(f"  {char_display}: {code}")

    # 编码到字符重新解码
    code_to_char = {code: ch for ch, code in code_map.items()}
    # 读取编码文件（二进制字符串形式）
    with open(encoded_path, 'r', encoding='utf-8') as f:
        encoded_bits = f.read().strip()

    # 解码过程：逐位读取，直到匹配到编码表中的字符
    decoded_chars = []
    buffer = ""
    for bit in encoded_bits:
        buffer += bit
        if buffer in code_to_char:
            decoded_chars.append(code_to_char[buffer])
            buffer = ""
    #暴力匹配字符

    # 检查是否有未解码的剩余比特
    if buffer:
        print(f"警告: 存在未解码的剩余比特: {buffer}")

    decoded_text = "".join(decoded_chars)
    # 将解码结果写入输出文件
    with open(decoded_path, 'w', encoding='utf-8') as f:
        f.write(decoded_text)
    print(f"\n解码完成: 解码文件 {decoded_path}")
    print(f"解码统计: 编码比特数 {len(encoded_bits)}, 解码字符数 {len(decoded_text)}")


def main():
    print("=== 哈夫曼编码/解码工具 ===")
    mode = input("\n请选择操作模式(encode=编码 / decode=解码): ").strip().lower()
    if mode == "encode":
        input_path = input("请输入要编码的文本文件路径: ").strip()
        default_encoded = input_path + "_encoded.txt"
        default_table = input_path + "_table.txt"
        encoded_path = input(f"编码后输出文件路径(默认: {default_encoded}): ").strip() or default_encoded
        table_path = input(f"编码表输出路径(默认: {default_table}): ").strip() or default_table
        try:
            encode_file(input_path, encoded_path, table_path)
        except FileNotFoundError:
            print(f"错误: 找不到文件 '{input_path}'")
        except Exception as e:
            print(f"编码过程中出错: {e}")
    elif mode == "decode":
        encoded_path = input("请输入Huffman编码后的文件路径: ").strip()
        table_path = input("请输入对应的编码表文件路径: ").strip()
        default_decoded = "decoded.txt"
        decoded_path = input(f"解码后输出文件路径(默认: {default_decoded}): ").strip() or default_decoded
        try:
            decode_file(encoded_path, table_path, decoded_path)
        except FileNotFoundError as e:
            print(f"错误: 找不到文件 - {e}")
        except Exception as e:
            print(f"解码过程中出错: {e}")
    else:
        print("无效模式，请输入 'encode' 或 'decode'。")


if __name__ == "__main__":
    main()