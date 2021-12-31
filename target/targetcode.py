# -*- coding:utf-8 -*-

# 自己定义的栈
class MinStack(object):
    def __init__(self):
        self.stack = []  # 存放所有元素
        self.minStack = []  # 存放每一次压入数据时，栈中的最小值                  # （如果压入数据的值大于栈中的最小值就不需要重复压入最小值，
        # 小于或者等于栈中最小值则需要压入）

    def push(self, x):
        self.stack.append(x)
        if not self.minStack or self.minStack[-1] >= x:
            self.minStack.append(x)

    def pop(self):  # 移除栈顶元素时，判断是否移除栈中最小值
        if self.minStack[-1] == self.stack[-1]:
            del self.minStack[-1]
        self.stack.pop()

    def top(self):  # 获取栈顶元素
        return self.stack[-1]

    def get_min(self):  # 获取栈中的最小值
        return self.minStack[-1]

    def all(self):  # 列表栈中所有的元素
        return self.stack[:]


class AsmCode(object):
    def __init__(self):
        self.i = 0
        self.w_label = 0  # while循环标签序号
        self.I_label = 0  # if or else if标签序号
        self.label = 0  # 判断标签序号
        self.opr_set = {'+', '-', '*', '/', '++', '--', '+=', '-=', '/=', '*=', '%=', '=', '%'}
        self.judge_set = {'>', '<', '>=', '<=', '==', '&&', '||', '!', '!='}
        self.__while_label = MinStack()  # while的标签
        self.__IF_label = MinStack()  # IF的标签
        self.F_label = 0  # for标签序号
        self.__FOR_label = MinStack()  # for标签
        self.__judge_if = 0  # judge 序号
        self.__judge_label = MinStack()  # judge 跳出的标号
        self.code = list()
        self.s = ""  # 用来存一个输入
        self.text_code = list()  # 存放代码
        self.temp_set = set()  # 存放定义的变量，方便后续判断变量是否已定义
        self.data_code = list()  # 存放定义的变量
        self.func_code = list()  # 存函数代码
        self.include_code = []

    def run(self):
        self.__analyze(self.code)

    # 处理四元式
    def push_code(self, middle_code):
        for item in middle_code:
            code_list = list()
            for i in item:
                code_list.append(i)
            while len(code_list) < 4:
                code_list.append('NULL')
            self.code.append(code_list)
            print(code_list)

    # 对于产生的中间代码进行处理
    def __analyze(self, middle_text_code):
        num = 0  # 标记当前四元式位置
        middle_code = iter(middle_text_code)

        for item in middle_code:

            if item[0] == 'int':
                self.__initialize(item)
            elif item[0] in self.opr_set:
                self.__anaylze_opr(item)
            elif item[0] in self.judge_set:
                self.__anaylez_judge(item)
            elif item[0] == 'BEGIN' and item[1] == 'WHILE':
                t = self.__while_begin(middle_text_code, num)
                for i in range(0, t - num):
                    next(middle_code)
                num = t
            elif item[0] == 'END' and item[1] == 'WHILE':
                self.__white_end()
            elif item[0] == 'BEGIN' and item[1] == 'JUDGEMENT':
                judge_id = "judge" + str(self.__judge_if)
                self.__judge_label.push(judge_id)
                self.__judge_if += 1
            elif item[0] == 'BEFIN' and item[1] == 'IF':
                t = self.__if_begin(middle_text_code, num)
                for i in range(0, t - num):
                    next(middle_code)
                num = t
            elif (item[0] == 'END' and item[1] == 'IF') or (item[0] == 'END' and item[1] == 'ELSE IF'):
                self.text_code.append("jmp " + self.__judge_label.top())
            elif item[0] == 'BEGIN' and item[1] == 'ELSE IF':
                t = self.__elseif_begin(middle_text_code, num)
                for i in range(0, t - num):
                    next(middle_code)
                num = t
            elif item[0] == 'BEGIN' and item[1] == 'ELSE':
                self.text_code.append(self.__IF_label.top() + ":")
                self.__IF_label.pop()
            elif item[0] == 'END' and item[1] == 'JUDGEMENT':
                self.text_code.append(self.__judge_label.top() + ":")
                self.__judge_label.pop()
            elif item[0] == 'BEGIN' and item[1] == 'FOR':
                t = self.__for_begin(middle_text_code, num)
                for i in range(0, t - num):
                    next(middle_code)
                num = t
            elif item[0] == 'END' and item[1] == 'FOR':
                self.__for_end()
            elif item[0] == 'BEGINFUNC' and item[1] != 'main':
                t = self.__beginfunc(item, middle_text_code, num)
                for i in range(0, t - num):
                    next(middle_code)
                num = t
            elif item[0] == 'CALLFUNC':
                self.__callfunc(item)
            elif item[0] == 'OUT':
                self.__out(item)
            elif item[0] == 'INPUT':
                self.__input(item)
            else:
                pass
            num += 1

    # while循环开始
    def __while_begin(self, middle_text_code, num):
        lab = "W" + str(self.w_label)
        self.w_label += 1
        t = num + 1
        new_list = list()
        last_temp = ""
        while middle_text_code[t][0] != 'END':
            new_list.append(middle_text_code[t])
            print(middle_text_code[t])
            if str(middle_text_code[t + 1][0]) == 'END' and str(middle_text_code[t + 1][1]) == 'CONDITION':
                last_temp = middle_text_code[t][3]
                break
            t += 1
        self.text_code.append(lab + ":")
        self.__analyze(new_list)
        self.text_code.append("mov eax," + str(last_temp))
        self.text_code.append("mov ebx,0")
        self.text_code.append("cmp eax,ebx")
        new_lab = "W" + str(self.w_label)
        self.w_label += 1
        self.text_code.append("je " + new_lab)
        self.__while_label.push(new_lab)
        self.__while_label.push(lab)
        return t

    # while循环结束
    def __white_end(self):
        self.text_code.append('jmp ' + self.__while_label.top())
        self.__while_label.pop()
        self.text_code.append(self.__while_label.top() + ":")
        self.__while_label.pop()

    # if判断开始
    def __if_begin(self, middle_text_code, num):
        t = num + 1
        new_list = list()
        last_temp = ""
        while middle_text_code[t][0] != 'END':
            new_list.append(middle_text_code[t])
            if str(middle_text_code[t + 1][0]) == 'END' and str(middle_text_code[t + 1][1]) == 'CONDITION':
                last_temp = middle_text_code[t][3]
                break
            t += 1
        self.__analyze(new_list)
        self.text_code.append("mov eax," + str(last_temp))
        self.text_code.append("mov ebx,0")
        self.text_code.append("cmp eax,ebx")
        new_lab_if = "I" + str(self.I_label)
        self.I_label += 1
        self.text_code.append("je " + new_lab_if)
        self.__IF_label.push(new_lab_if)
        return t

    # else if 开始
    def __elseif_begin(self, middle_text_code, num):
        self.text_code.append(self.__IF_label.top() + ":")
        t = num + 1
        new_list = list()
        last_temp = ""
        while middle_text_code[t][0] != 'END':
            new_list.append(middle_text_code[t])
            if str(middle_text_code[t + 1][0]) == 'END' and str(middle_text_code[t + 1][1]) == 'CONDITION':
                last_temp = middle_text_code[t][3]
                break
            t += 1
        self.__analyze(new_list)
        self.text_code.append("mov eax," + str(last_temp))
        self.text_code.append("mov ebx,0")
        self.text_code.append("cmp eax,ebx")
        new_lab_if = "I" + str(self.I_label)
        self.I_label += 1
        self.text_code.append("je " + new_lab_if)
        self.__IF_label.push(new_lab_if)
        return t

    # for循环
    def __for_begin(self, middle_text_code, num):
        t = num + 1
        list_any = list()
        while middle_text_code[t][0] != 'BEGIN' and middle_text_code[t] != 'CONDITION':
            list_any.append(middle_text_code[t])
            t += 1
        self.__analyze(list_any)
        new_list = list()
        last_temp = ""
        t = t - 1
        while middle_text_code[t][0] != 'END' and middle_text_code[t][0] != 'CONDITION':
            new_list.append(middle_text_code[t + 1])
            if str(middle_text_code[t + 1][0]) == 'END' and str(middle_text_code[t + 1][1]) == 'CONDITION':
                last_temp = middle_text_code[t][3]
                break
            t += 1
        h = num + 1
        list_s = list()

        while middle_text_code[h][0] != 'BEGIN' and middle_text_code[h] != 'CONDITION':
            list_s.append(middle_text_code[h])
            h += 1
        self.__analyze(list_s)
        lab = "F" + str(self.F_label)
        self.F_label += 1
        self.text_code.append(lab + ":")
        self.__analyze(new_list)
        self.text_code.append("mov eax," + str(last_temp))
        self.text_code.append("mov ebx,0")
        self.text_code.append("cmp eax,ebx")
        new_lab_for = "F" + str(self.F_label)
        self.F_label += 1
        self.text_code.append("je " + new_lab_for)
        self.__FOR_label.push(new_lab_for)
        self.__FOR_label.push(lab)
        return t - 1

    # 结束for循环
    def __for_end(self):
        self.text_code.append('jmp ' + self.__FOR_label.top())
        self.__FOR_label.pop()
        self.text_code.append(self.__FOR_label.top() + ":")
        self.__FOR_label.pop()

    # 函数定义
    def __beginfunc(self, item, middle_text_code, num):
        t = num
        self.func_code.append(item[1] + " PROC,")
        target = 0
        func_name = item[1]
        for value in middle_text_code[num][2]:
            if target == len(item[2]) - 1:
                self.func_code.append("  " + value + ":dword")
            else:
                self.func_code.append("  " + value + ": dword,")
                target += 1
        t += 1
        return_list = []
        func_anaylze_list = list()
        while middle_text_code[t][0] != "ENDFUNC":
            func_anaylze_list.append(middle_text_code[t])
            if middle_text_code[t + 1][0] == 'ENDFUNC':
                return_list = middle_text_code[t]
                break
            t += 1
        func_anaylze_code = AsmCode()
        func_anaylze_code.push_code(func_anaylze_list)
        func_anaylze_code.run()
        func_text_list = func_anaylze_code.text_code
        func_data_list = func_anaylze_code.data_code
        for code in func_text_list:
            self.func_code.append("  " + code)
        for data in func_data_list:
            self.data_code.append(data)
        self.func_code.append("  mov eax," + return_list[1])
        self.func_code.append("  ret")
        self.func_code.append(func_name + " ENDP")
        return t

    # 调用函数
    def __callfunc(self, item):
        str_param = ''
        for param in item[2]:
            str_param = str_param + ','
            str_param = str_param + str(param)
        self.text_code.append("invoke " + item[1] + str_param)
        if item[3] in self.temp_set:
            self.text_code.append("mov " + item[3] + ",eax")
        else:
            self.data_code.append(item[3] + "  dd  ?")
            self.text_code.append("mov " + item[3] + ",eax")
            self.temp_set.add(item[3])

    # 判断处理
    def __anaylez_judge(self, item):
        if item[0] == '&&':
            self.__and(item)
        elif item[0] == '||':
            self.__or(item)
        elif item[0] == '!':
            self.__not(item)
        elif item[0] == '==':
            self.__je(item)
        elif item[0] == '>':
            self.__ja(item)
        elif item[0] == '<':
            self.__jb(item)
        elif item[0] == '<=':
            self.__jna(item)
        elif item[0] == '>=':
            self.__jnb(item)
        elif item[0] == '!=':
            self.__jne(item)
        else:
            pass

    # 运算符处理
    def __anaylze_opr(self, item):
        if item[0] == '=':
            self.__opr_equal(item)
        elif item[0] == '+':
            self.__opr_add(item)
        elif item[0] == '-':
            self.__opr_sub(item)
        elif item[0] == '*':
            self.__opr_mul(item)
        elif item[0] == '/':
            self.__opr_div(item)
        elif item[0] == '%':
            self.__opr_rem(item)
        elif item[0] == '++':
            self.__opr_add_own(item)
        elif item[0] == '--':
            self.__opr_sub_own(item)
        elif item[0] == '+=':
            self.__opr_add_equ(item)
        elif item[0] == '-=':
            self.__opr_sub_equ(item)
        elif item[0] == '*=':
            self.__opr_mul_equ(item)
        elif item[0] == '/=':
            self.__opr_div_equ(item)
        elif item[0] == '%=':
            self.__opr_rem_equ(item)
        else:
            pass

    # 输出
    def __out(self, item):
        len_str = "len" + str(self.i)  # 输出格式标签
        t = 0
        p = ""
        for p_str in item[1]:
            p += p_str
            t += 1
        v = ""
        k = t
        for value in item[2]:
            if t == 1:
                v += str(value)
            else:
                v += "," + str(value)
            t -= 1
        self.data_code.append(len_str + "  db " + str(p) + ",0")
        self.text_code.append("invoke crt_printf,addr newline")
        self.text_code.append("invoke crt_printf,addr " + len_str + str(v))
        self.i += 1

    # 输入
    def __input(self, item):
        len_str = "len" + str(self.i)
        self.data_code.append(len_str + "  db " + "\"" + "%s" + "\"" + ",0")
        for value in item[1]:
            self.s = "invoke crt_scanf,addr " + str(len_str) + ",addr " + str(value)
            self.text_code.append("invoke crt_scanf,addr " + len_str + ",addr " + value)
            self.text_code.append("sub " + value + ",30h")
        self.i += 1

    # 与
    def __and(self, item):
        if item[3] in self.temp_set:
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("and eax,ebx")
            self.text_code.append("mov " + item[3] + ",eax")
        else:
            self.data_code.append(item[3] + "  dd  ?")
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("and eax,ebx")
            self.text_code.append("mov " + item[3] + ",eax")
            self.temp_set.add(item[3])

    # 或
    def __or(self, item):
        if item[3] in self.temp_set:
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("or eax,ebx")
            self.text_code.append("mov " + item[3] + ",eax")
        else:
            self.data_code.append(item[3] + "  dd  ?")
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("or eax,ebx")
            self.text_code.append("mov " + item[3] + ",eax")
            self.temp_set.add(item[3])

    # 非
    def __not(self, item):
        if item[2] in self.temp_set:
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("neg eax")
            self.text_code.append("mov ebx,1")
            self.text_code.append("add eax,ebx")
            self.text_code.append("mov " + item[2] + ",eax")
        else:
            self.data_code.append(item[2] + " dd  ?")
            self.temp_set.add(item[2])
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("neg eax")
            self.text_code.append("mov ebx,1")
            self.text_code.append("add eax,ebx")
            self.text_code.append("mov " + item[2] + ",eax")

    # ==
    def __je(self, item):
        if item[3] in self.temp_set:
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("je " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
        else:
            self.data_code.append(item[3] + "  dd  ?")
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("je " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
            self.temp_set.add(item[3])

    #  !=
    def __jne(self, item):
        if item[3] in self.temp_set:
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("jne " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
        else:
            self.data_code.append(item[3] + "  dd  ?")
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("jne " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
            self.temp_set.add(item[3])

    # >
    def __ja(self, item):
        if item[3] in self.temp_set:
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("ja " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
        else:
            self.data_code.append(item[3] + "  dd  ?")
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("ja " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
            self.temp_set.add(item[3])

    # <
    def __jb(self, item):
        if item[3] in self.temp_set:
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("jb " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
        else:
            self.data_code.append(item[3] + "  dd  ?")
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("jb " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
            self.temp_set.add(item[3])

    # >=
    def __jna(self, item):
        if item[3] in self.temp_set:
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("jna " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
        else:
            self.data_code.append(item[3] + "  dd  ?")
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("jna " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
            self.temp_set.add(item[3])

    # <=
    def __jnb(self, item):
        if item[3] in self.temp_set:
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("jnb " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
        else:
            self.data_code.append(item[3] + "  dd  ?")
            self.text_code.append("mov eax," + item[1])
            self.text_code.append("mov ebx," + item[2])
            self.text_code.append("cmp eax,ebx")
            lab = "L" + str(self.label)
            self.label += 1
            self.text_code.append("jnb " + lab)
            self.text_code.append("mov edx,0")
            self.text_code.append("mov " + item[3] + ",edx")
            lab2 = "L" + str(self.label)
            self.text_code.append("jmp " + lab2)
            self.label += 1
            self.text_code.append(lab + ":")
            self.text_code.append("mov edx,1")
            self.text_code.append("mov " + item[3] + ",edx")
            self.text_code.append(lab2 + ":")
            self.temp_set.add(item[3])

    # 定义变量
    def __initialize(self, item):
        """
        定义变量
        """
        id = item[2]
        value = item[3]
        if value == 'undefined':
            self.data_code.append(id + "  dd  ?")
            self.temp_set.add(id)
        elif value in self.temp_set:
            if id in self.temp_set:
                self.text_code.append("mov eax," + value)
                self.text_code.append("mov " + id + ",eax")
            else:
                self.data_code.append(id + "  dd  ?")
                self.text_code.append("mov edx," + value)
                self.text_code.append("mov " + id + ",edx")
                self.temp_set.add(id)
        elif item[2] in self.temp_set:
            self.text_code.append("mov eax," + item[3])
            self.text_code.append("mov " + item[2] + ",eax")
        else:
            self.data_code.append(id + "  dd  " + value)
            self.temp_set.add(id)

    # =
    def __opr_equal(self, item):
        self.text_code.append("mov eax," + item[2])
        self.text_code.append("mov " + item[1] + ",eax")

    # +
    def __opr_add(self, item):
        if len(item) == 4:
            if item[3] in self.temp_set:
                self.text_code.append("mov eax," + item[1])
                self.text_code.append("add eax," + item[2])
                self.text_code.append("mov " + item[3] + ",eax")
            else:
                self.data_code.append(item[3] + "  dd  ?")
                self.text_code.append("mov eax," + item[1])
                self.text_code.append("add eax," + item[2])
                self.text_code.append("mov " + item[3] + ",eax")
                self.temp_set.add(item[3])

    # -
    def __opr_sub(self, item):
        if len(item) == 4:
            if item[3] in self.temp_set:
                self.text_code.append("mov eax," + item[1])
                self.text_code.append("mov ebx," + item[2])
                self.text_code.append("sub eax,ebx")
                self.text_code.append("mov " + item[3] + ",eax")
            else:
                self.data_code.append(item[3] + "  dd  ?")
                self.text_code.append("mov eax," + item[1])
                self.text_code.append("mov ebx," + item[2])
                self.text_code.append("sub eax,ebx")
                self.text_code.append("mov " + item[3] + ",eax")
                self.temp_set.add(item[3])

    # *
    def __opr_mul(self, item):
        if len(item) == 4:
            if item[3] in self.temp_set:
                self.text_code.append("mov eax," + item[1])
                self.text_code.append("mov ebx," + item[2])
                self.text_code.append("mul ebx")
                self.text_code.append("mov " + item[3] + ",eax")
            else:
                self.data_code.append(item[3] + "  dd  ?")
                self.text_code.append("mov eax," + item[1])
                self.text_code.append("mov ebx," + item[2])
                self.text_code.append("mul ebx")
                self.text_code.append("mov " + item[3] + ",eax")
                self.temp_set.add(item[3])

    # /
    def __opr_div(self, item):
        if len(item) == 4:
            if item[3] in self.temp_set:
                self.text_code.append("mov edx,0")
                self.text_code.append("mov eax,dword ptr " + item[1])
                self.text_code.append("mov ebx," + item[2])
                self.text_code.append("div ebx")
                self.text_code.append("mov " + item[3] + ",eax")
            else:
                self.data_code.append(item[3] + "  dd  ?")
                self.text_code.append("mov edx,0")
                self.text_code.append("mov eax,dword ptr " + item[1])
                self.text_code.append("mov ebx," + item[2])
                self.text_code.append("div ebx")
                self.text_code.append("mov " + item[3] + ",eax")
                self.temp_set.add(item[3])

    # %
    def __opr_rem(self, item):
        if len(item) == 4:
            if item[3] in self.temp_set:
                self.text_code.append("mov edx,0")
                self.text_code.append("mov eax,dword ptr " + item[1])
                self.text_code.append("mov ebx," + item[2])
                self.text_code.append("div ebx")
                self.text_code.append("mov " + item[3] + ",edx")
            else:
                self.data_code.append(item[3] + "  dd  ?")
                self.text_code.append("mov edx,0")
                self.text_code.append("mov eax,dword ptr " + item[1])
                self.text_code.append("mov ebx," + item[2])
                self.text_code.append("div ebx")
                self.text_code.append("mov " + item[3] + ",edx")
                self.temp_set.add(item[3])

    # ++
    def __opr_add_own(self, item):
        self.text_code.append("mov eax," + item[1])
        self.text_code.append("mov ebx,1")
        self.text_code.append("add eax,ebx")
        self.text_code.append("mov " + item[1] + ",eax")

    # --
    def __opr_sub_own(self, item):
        self.text_code.append("mov eax," + item[1])
        self.text_code.append("mov ebx,1")
        self.text_code.append("sub eax,ebx")
        self.text_code.append("mov " + item[1] + ",eax")

    # +=
    def __opr_add_equ(self, item):
        self.text_code.append("mov eax," + item[1])
        self.text_code.append("add eax," + item[2])
        self.text_code.append("mov " + item[1] + ",eax")

    # -=
    def __opr_sub_equ(self, item):
        self.text_code.append("mov eax," + item[1])
        self.text_code.append("sub eax," + item[2])
        self.text_code.append("mov " + item[1] + ",eax")

    # *=
    def __opr_mul_equ(self, item):
        self.text_code.append("mov eax," + item[1])
        self.text_code.append("mov ebx," + item[2])
        self.text_code.append("mul ebx")
        self.text_code.append("mov " + item[1] + ",eax")

    # /=
    def __opr_div_equ(self, item):
        self.text_code.append("mov edx,0")
        self.text_code.append("mov eax,dword ptr " + item[1])
        self.text_code.append("mov ebx," + item[2])
        self.text_code.append("div ebx")
        self.text_code.append("mov " + item[1] + ",eax")

    # %=
    def __opr_rem_equ(self, item):
        self.text_code.append("mov edx,0")
        self.text_code.append("mov eax,dword ptr " + item[1])
        self.text_code.append("mov ebx," + item[2])
        self.text_code.append("div ebx")
        self.text_code.append("mov " + item[1] + ",edx")

    # 汇编语言包含的一些头文件
    def __include(self):
        self.include_code.append(".386")
        self.include_code.append(".model flat, stdcall")
        self.include_code.append("option casemap :none")
        self.include_code.append("include	windows.inc")
        self.include_code.append("include kernel32.inc")
        self.include_code.append("include masm32.inc")
        self.include_code.append("includelib kernel32.lib")
        self.include_code.append("includelib masm32.lib")
        self.include_code.append("include msvcrt.inc")
        self.include_code.append("includelib msvcrt.lib")
        self.include_code.append(".data")
        self.include_code.append("len equ 100")

    # 输出汇编语言并写入文件
    def print_code(self):
        self.__include()
        self.data_code.append("newline db 0ah,0dh")
        with open("targetcode.txt", "w") as f:
            for include_data in self.include_code:
                print(include_data)
                f.write(include_data)
                f.write('\n')
            for data in self.data_code:
                print("  " + data)
                f.write("  " + data)
                f.write('\n')
            print(".code")
            f.write(".code")
            f.write('\n')
            for fun_code in self.func_code:
                print(fun_code)
                f.write(fun_code)
                f.write('\n')
            print("start:")
            f.write("start:")
            f.write('\n')
            self.text_code.append(self.s)
            self.text_code.append("ret;")
            for code in self.text_code:
                print("  " + code)
                f.write("  " + code)
                f.write('\n')

            print("end start")
            f.write("end start")
            f.write('\r\n')
            f.close()
