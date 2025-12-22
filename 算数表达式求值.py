class Stack:

    def __init__(self):
        self.stack = []

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        if self.empty():
            raise IndexError("栈为空（无法弹出元素）")
        return self.stack.pop()

    def empty(self):
        return len(self.stack) == 0

    def size(self):
        return len(self.stack)

    def top(self):
        if self.empty():
            print("栈为空")
            return None
        return self.stack[-1]


class ArithmeticExpressionValue:

    def __init__(self,expression):
        self.expression = expression
        if  self.expression[-1] != "=":
            raise ValueError("表达式结尾应为'='")

    def SymbolPriority(self,symbol):
        priority = {"=" : 0 ,"+" : 1 ,"-" : 1 ,"*" : 2 ,"/" : 2 ,"(" : 0} #为运算符优先级标注大小关系
        return priority.get(symbol,-1)

    def calculate(self):
        num_stack = Stack()
        symbol_stack = Stack()
        symbol_stack.push("=") #提前压入一个等号作为结束运算的标志,避免出现遍历完成却没有计算的情况

        i=0
        n=len(self.expression)
        while i < n :
            s = self.expression[i]
            if s.isdigit():
                num=0
                while i < n and self.expression[i].isdigit(): #找出表达式中的数字字符
                    num = num * 10 + int(self.expression[i]) #通过while循环把输入的字符串中的数字转化成整数
                    i += 1
                num_stack.push(num)
                continue
            else :

                   if s == "(" :
                        symbol_stack.push("(") #只要有左括号就入栈

                   elif s == ")" :
                        while symbol_stack.top() != "(" :
                            self.value(num_stack,symbol_stack) #遇到右括号，弹栈计算
                        symbol_stack.pop()

                   elif s == "=" :
                        while symbol_stack.top() != "=" : #等于号直接入栈并计算
                            self.value(num_stack,symbol_stack)
                        break
                   else:
                        while self.SymbolPriority(symbol_stack.top()) >= self.SymbolPriority(s): #判断栈顶元素和栈外元素的优先级，如果栈外元素优先级小就计算，否则入栈
                            self.value(num_stack,symbol_stack)
                        symbol_stack.push(s)

                   i += 1
        return num_stack.pop()

    def value(self,num_stack,symbol_stack):
        s = symbol_stack.pop() #计算表达式的值时，逐个将栈顶元素弹出

        if s in ("(" , "=") :
            return

        num1 = num_stack.pop()
        num2 = num_stack.pop()

        result = None

        if s ==  "+" :
            result = num1 + num2

        elif s == "-" :
            result = num2 - num1

        elif s == "*" :
            result = num1 * num2

        elif s == "/" :
            result = num2 / num1

        num_stack.push(result) #计算完成后再将结果压入栈中


if __name__ == "__main__":
    expr = input("请输入以'='结尾的算术表达式：")
    try:
        evaluator = ArithmeticExpressionValue(expr)
        result = evaluator.calculate()
        print(f"计算结果：{result}")
    except Exception as e:
        print(f"错误：{e}")










