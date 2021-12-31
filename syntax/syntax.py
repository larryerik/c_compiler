"""
语法分析
"""
from syntax.rule import Sign, Production, terminal_sign_type, non_terminal_sign_type, productions, grammar_start
from error import SyntaxRuleError, SyntaxError, SemanticRuleError


class PredictingAnalysisTable:
    """
    预测分析表
    """

    def __init__(self):
        """
        构造
        """
        # 错误
        self.__error = None

        # 预测分析表
        self.__table = list()

        # 所有的非终结符
        self.__non_terminal_signs = list()
        # 所有的终结符
        self.__terminal_signs = list()

        # 载入所有的符号
        for i in non_terminal_sign_type:
            self.__non_terminal_signs.append(Sign(i))

        for i in terminal_sign_type:
            self.__terminal_signs.append(Sign(i))

        # 根据非终结符和终结符的数量为预测分析表分配空间，并且为每一个格子预先填上 None
        for i in non_terminal_sign_type:
            self.__table.append(list())
        for i in range(0, len(non_terminal_sign_type)):
            for j in terminal_sign_type:
                self.__table[i].append(None)

        # 为每一个非终结符建立 first 集和 follow 集
        self.__firsts = list()
        self.__follows = list()

        # 为每一个非终结符的 first 集和 follow 集分配空间
        for i in non_terminal_sign_type:
            self.__firsts.append(list())
            self.__follows.append(list())

    def compile(self):
        """
        编译预测分析表
        """
        # 对每一个文法元素求其 first 集
        self.__calculate_firsts()
        # PredictingAnalysisTable.__print_set(self.__firsts)
        # 对每一个文法元素求其 follow 集
        self.__calculate_follows()
        # PredictingAnalysisTable.__print_set(self.__follows)

        # 根据 first 集和 follow 集生成预测分析表
        success = self.__generate_table()
        # self.print_table()
        return success

    def get_production(self, non_terminal_sign, terminal_sign):
        """
        从预测分析表中获取产生式
        :param non_terminal_sign: 非终结符
        :param terminal_sign: 终结符
        :return: 产生式
        """
        x = self.__get_non_terminal_sign_index(non_terminal_sign)
        y = self.__get_terminal_sign_index(terminal_sign)
        return self.__table[x][y]

    def __set_add(self, container, sign):
        """
        将 sign 添加到 container 中并返回 True，如果其中已经有该元素了则返回 False
        :param container: 要添加到的集合
        :param sign: 符号
        :return: 添加是否成功
        """
        exist = False
        for elem in container:
            if elem.type == sign.type:
                exist = True
        if not exist:
            container.append(sign)
        return not exist

    def __get_terminal_sign_index(self, terminal_sign):
        """
        获取终结符的索引
        :param terminal_sign: 终结符
        :return: 索引(寻找失败返回 -1)
        """
        for i in range(0, len(self.__terminal_signs)):
            if terminal_sign.type == self.__terminal_signs[i].type:
                return i
        return -1

    def __get_non_terminal_sign_index(self, non_terminal_sign):
        """
        获取非终结符的索引
        :param non_terminal_sign: 非终结符
        :return: 索引(寻找失败返回 -1)
        """
        for i in range(0, len(self.__non_terminal_signs)):
            if non_terminal_sign.type == self.__non_terminal_signs[i].type:
                return i
        return -1

    def __get_non_terminal_sign_first(self, non_terminal_sign):
        """
        获取目标非终结符的 first 集的引用
        :param non_terminal_sign: 目标非终结符
        :return: 其 first 集的引用
        """
        return self.__firsts[self.__get_non_terminal_sign_index(non_terminal_sign)]

    def __get_non_terminal_sign_first_no_empty(self, non_terminal_sign):
        """
        获取目标非终结符的 first 集的非空拷贝
        :param non_terminal_sign: 目标非终结符
        :return: 其 first 集的非空拷贝
        """
        result = list()
        for i in self.__get_non_terminal_sign_first(non_terminal_sign):
            if not i.is_empty_sign():
                result.append(i)
        return result

    def __is_empty_in_non_terminal_sign_first(self, non_terminal_sign):
        """
        目标非终结符的 first 集中是否有空字
        :param non_terminal_sign: 目标非终结符
        :return: True/False
        """
        for i in self.__get_non_terminal_sign_first(non_terminal_sign):
            if i.is_empty_sign():
                return True
        return False

    def __get_non_terminal_sign_follow(self, non_terminal_sign):
        """
        获取非终结符的 follow 集
        :param non_terminal_sign: 非终结符
        :return: 其 follow 集
        """
        return self.__follows[self.__get_non_terminal_sign_index(non_terminal_sign)]

    def __calculate_firsts(self):
        """
        求所有的 first 集
        """
        # 立一个 flag，用来标志 firsts 集是否增大
        flag = True
        # 开始循环
        while flag:
            flag = False
            # 在每一次循环之中遍历所有产生式
            for production in productions:
                # 如果产生式右边为空
                if flag:
                    break
                if len(production.right) == 0:
                    # 将空字加入其 first 集
                    if self.__set_add(self.__get_non_terminal_sign_first(production.left), Sign('empty')):
                        flag = True
                # 如果产生式右边不为空
                else:
                    # 如果是以终结符开头，将终结符添加到其 first 集
                    if production.right[0].is_terminal_sign():
                        if self.__set_add(self.__get_non_terminal_sign_first(production.left), production.right[0]):
                            flag = True
                    # 如果是以非终结符开头
                    elif production.right[0].is_non_terminal_sign():
                        # (1) 将开头非终结符的 first 集中的所有非空元素添加到产生式左边非终结符的 first 集中
                        bigger = False
                        for i in self.__get_non_terminal_sign_first_no_empty(production.right[0]):
                            if self.__set_add(self.__get_non_terminal_sign_first(production.left), i):
                                bigger = True
                        if bigger:
                            flag = True

                        # (2) 从第一个非终结符开始循环，如果其 first 集中包含空字，那么将它下一个符号的 first
                        # 集添加到产生式左边非终结符的 first 集中去
                        for i in range(0, len(production.right)):
                            if production.right[i].is_non_terminal_sign():
                                # 如果包含空字
                                if self.__is_empty_in_non_terminal_sign_first(production.right[i]):
                                    # 如果它是最后一个，将空字填入
                                    if i == len(production.right) - 1:
                                        if self.__set_add(self.__get_non_terminal_sign_first(production.left),
                                                          Sign('empty')):
                                            flag = True
                                    # 如果不是最后一个
                                    else:
                                        # 如果它之后是终结符
                                        if production.right[i + 1].is_terminal_sign():
                                            if self.__set_add(self.__get_non_terminal_sign_first(production.left),
                                                              production.right[i + 1]):
                                                flag = True
                                        # 如果它之后是非终结符
                                        elif production.right[i + 1].is_non_terminal_sign():
                                            bigger = False
                                            for j in self.__get_non_terminal_sign_first_no_empty(
                                                    production.right[i + 1]):
                                                if self.__set_add(
                                                        self.__get_non_terminal_sign_first(production.left), j):
                                                    bigger = True
                                            if bigger:
                                                flag = True
                                        else:
                                            self.__error = SyntaxRuleError('终结符或非终结符类型错误')
                                            return False
                                # 如果不包含空字
                                else:
                                    break
                            else:
                                break
                    # 否则报错
                    else:
                        self.__error = SyntaxRuleError('终结符或非终结符类型错误')
                        return False

    def __calculate_follows(self):
        """
        求所有的 follow 集
        """
        first = list()
        flag = True
        while flag:
            flag = False
            # 遍历所有产生式
            for production in productions:
                if flag:
                    break
                # 如果产生式左边是开始符号
                if production.left.type == grammar_start.type:
                    if self.__set_add(self.__get_non_terminal_sign_follow(production.left), Sign('pound')):
                        flag = True

                # 遍历产生式右边
                for i in range(0, len(production.right)):
                    # 如果是非终结符
                    if production.right[i].is_non_terminal_sign():
                        # 如果它是产生式最后一个符号
                        if i == len(production.right) - 1:
                            # 将产生式左边非终结符的 follow 集添加到这个符号的 follow 集中
                            bigger = False
                            for j in self.__get_non_terminal_sign_follow(production.left):
                                if self.__set_add(self.__get_non_terminal_sign_follow(production.right[i]), j):
                                    bigger = True
                            if bigger:
                                flag = True
                        # 否则观察其之后的元素
                        else:
                            # 求他之后所有符号集合的 first 集
                            first.clear()
                            first += self.__calculate_set_first(production.right[i + 1:])
                            # (1) 将 first 中所有非空元素填入 follow
                            empty_find = False
                            for f in first:
                                if not f.is_empty_sign():
                                    self.__set_add(self.__get_non_terminal_sign_follow(production.right[i]), f)
                                else:
                                    empty_find = True

                            # (2) 如果 first 中含有空
                            if empty_find:
                                # 将产生式左边非终结符的 follow 集添加到这个符号的 follow 集中
                                bigger = False
                                for j in self.__get_non_terminal_sign_follow(production.left):
                                    if self.__set_add(self.__get_non_terminal_sign_follow(production.right[i]), j):
                                        bigger = True
                                if bigger:
                                    flag = True
                    # 如果是终结符
                    elif production.right[i].is_terminal_sign():
                        continue
                    # 否则报错
                    else:
                        self.__error = SyntaxRuleError('终结符或非终结符类型错误')
                        return False

    def __calculate_set_first(self, container):
        """
        计算一系列符号的 first 集
        :param container: 符号集合
        :return: first 集
        """

        # 开始求 first 集
        # 如果集合为空
        first = list()

        # 开始求 first 集
        # 如果产生式右边为空
        if len(container) == 0:
            # 将空字加入其 first 集
            self.__set_add(first, Sign('empty'))
        # 如果产生式右边补位空
        else:
            # 如果是以终结符开头，将终结符添加到 first 集
            if container[0].is_terminal_sign():
                self.__set_add(first, container[0])
            # 如果是以非终结符开头
            elif container[0].is_non_terminal_sign():
                # (1) 将开头非终结符的 first 集中的所有非空元素添加到 first 中
                for i in self.__get_non_terminal_sign_first_no_empty(container[0]):
                    self.__set_add(first, i)

                # (2) 从第一个非终结符开始循环，如果其 first 集中包含空字，那么将它的下一个符号的 first
                # 集添加到 first 中
                for i in range(0, len(container)):
                    if container[i].is_non_terminal_sign():
                        # 如果包含空字
                        if self.__is_empty_in_non_terminal_sign_first(container[i]):
                            # 如果它是最后一个，将空字填入
                            if i == len(container) - 1:
                                self.__set_add(first, Sign('empty'))
                            # 如果不是最后一个
                            else:
                                # 如果它之后是终结符
                                if container[i + 1].is_terminal_sign():
                                    self.__set_add(first, container[i + 1])
                                # 如果它之后是非终结符
                                elif container[i + 1].is_non_terminal_sign():
                                    for j in self.__get_non_terminal_sign_first_no_empty(container[i + 1]):
                                        self.__set_add(first, j)
                                # 否则报错
                                else:
                                    self.__error = SyntaxRuleError('终结符或非终结符类型错误')
                                    return False
                        # 如果不含空字
                        else:
                            break
                    else:
                        break
            # 否则报错
            else:
                self.__error = SyntaxRuleError('终结符或非终结符类型错误')
                return False

        return first

    def __insert_to_table(self, production, terminal):
        """
        将产生式插入预测分析表对应位置
        :param production: 产生式
        :param terminal: 终结符
        :return: 是否插入成功
        """
        # 先判断应该插入到的位置
        x = self.__get_non_terminal_sign_index(production.left)
        y = self.__get_terminal_sign_index(terminal)

        # 如果那个位置已经有产生式了
        if self.__table[x][y]:
            # 判断这个产生式是不是与要插入的产生式一样
            same_left = production.left.type == self.__table[x][y].left.type
            if same_left:
                same_right = True
                if len(production.right) != len(self.__table[x][y].right):
                    self.__error = SyntaxRuleError("文法非LL(1)" + production.str)
                    return False
                else:
                    for i in range(0, len(production.right)):
                        if production.right[i].type != self.__table[x][y].right[i].type:
                            same_right = False
                    if same_right:
                        # 执行插入
                        del self.__table[x][y]
                        self.__table[x].insert(y, production)
                        return True
                    else:
                        self.__error = SyntaxRuleError("文法非LL(1)" + production.str)
                        return False
            else:
                self.__error = SyntaxRuleError("文法非LL(1)" + production.str)
                return False
        # 如果那个位置为空，说明可以填入
        else:
            # 执行插入
            del self.__table[x][y]
            self.__table[x].insert(y, production)
            return True

    def __generate_table(self):
        """
        根据 first 集和 follow 集生成预测分析表
        :return: 是否生成成功
        """
        # 对每一条产生式应用规则
        for production in productions:
            # 先求出该产生式右边部分的 first 集
            first = self.__calculate_set_first(production.right)
            # 对每一个 first 集中的每一个终结符执行操作
            empty_find = False
            for i in list(first):
                if i.type == 'empty':
                    empty_find = True
                else:
                    if not self.__insert_to_table(production, i):
                        return False

            # 如果其 first 集中有空字，则对 follow 集中的每一个终结符执行操作
            if empty_find:
                for i in self.__get_non_terminal_sign_follow(production.left):
                    if not self.__insert_to_table(production, i):
                        return False

        return True

    def print_table(self):
        """
        打印预测分析表
        """
        for j in range(len(terminal_sign_type)):
            print("  \t", terminal_sign_type[j], end="")
        print()
        for i in range(0, len(non_terminal_sign_type)):
            print(non_terminal_sign_type[i], " ", end="")
            for j in range(len(terminal_sign_type)):
                if self.__table[i][j] != None:
                    print(self.__table[i][j].string, "\t", end="")
                else:
                    print(self.__table[i][j], "\t", end="")
            print()

    def __print_set(fisrt):
        """
        打印first或者follow集合
        """
        for i in range(len(fisrt)):
            print(non_terminal_sign_type[i], " 的first集合：", end="")
            for j in fisrt[i]:
                print(j.type, end=" ")
            print()


class Node:
    """
    树节点
    """

    def __init__(self, data):
        """
        树节点
        :param data: 节点数据
        """
        self.data = data
        self.type = data.type
        self.children = list()
        self.parent = None
        self.value = data.str
        self.line = data.line

    def get_pre_brother(self, index):
        """
        获取它前 index 位的兄弟
        :param index: ..
        :return: 兄弟
        """
        self_index = 0
        for i in range(0, len(self.parent.children)):
            if self.parent.children[i] is self:
                self_index = i
        return self.parent.children[self_index - index]


class Tree:
    """
    树
    """

    def __init__(self, root):
        """
        构造
        :param root: 树的根节点
        """
        self.root = root

    def print_tree(root):
        l = list()
        print("father:", root.data.type)
        print("children:", end=" ")
        for i in root.children:
            l.append(i)
            print(i.data.type, end=", ")
        print()
        for i in l:
            Tree.print_tree(i)


class Stack:
    """
    栈
    """

    def __init__(self):
        """
        构造
        """
        self.__container = list()

    def push(self, elem):
        """
        入栈
        :param elem: 入栈元素
        """
        self.__container.append(elem)

    def pop(self):
        """
        将栈顶元素出栈
        :return: 栈顶元素
        """
        top = self.top()
        self.__container.pop()
        return top

    def top(self):
        """
        获取栈顶元素
        :return: 栈顶元素
        """
        return self.__container[-1]

    def empty(self):
        """
        栈是否为空
        :return: 栈是否为空
        """
        return len(self.__container) == 0


class Syntax:
    """
    语法分析器
    """

    def __init__(self):
        """
        构造
        """
        # 语法树的构建
        self.grammar_tree = None
        # 准备存放错误
        self.__error = list()
        # 预测分析表的构建
        self.__pa_table = PredictingAnalysisTable()
        # 编译预测分析表
        if self.__pa_table.compile():
            self.__error.append(SyntaxRuleError('预测分析表编译失败'))
        # 准备存放词法分析的结果
        self.__source = list()
        # 将词法分析产生的 token 转换成的终结符
        self.__terminals = list()
        # self.__pa_table.print_table()

    def put_source(self, source):
        """
        装填词法分析结果
        :param source: 词法分析结果
        """
        self.__source.clear()
        self.__terminals.clear()
        # 装填词法分析结果
        for s in source:
            self.__source.append(s)
        # 将 tokens 转换成终结符
        for s in self.__source:
            self.__terminals.append(Sign(s.type, s.str, s.line))
        # 在所有 tokens 的最后填入一个 #
        self.__terminals.append(Sign('pound'))

    def get_error(self):
        """
        获取错误
        :return: 错误
        """
        return self.__error

    def execute(self):
        """
        执行操作
        :return: 语法分析是否成功
        """
        # 新建栈
        stack = Stack()
        # 清空错误
        self.__error = None
        # 新建临时语法树
        grammar_tree = Tree(Node(Sign(grammar_start.type)))

        # 将 # 入栈
        stack.push(Node(Sign('pound')))
        # 将语法树根节点入栈
        stack.push(grammar_tree.root)

        # 拷贝转换之后的终结符到输入串
        inputs = list()
        for sign in self.__terminals:
            inputs.append(sign)
        # 设置当前输入符号索引
        input_index = 0

        # 立下 flag
        flag = True
        while flag:
            #  如果 top 是非终结符
            if stack.top().data.is_non_terminal_sign():
                # 查看分析表
                production = self.__pa_table.get_production(stack.top().data, inputs[input_index])
                # 如果分析表对应位置存有产生式
                if production:
                    # 将语法树按照产生式进行生长
                    for i in range(0, len(production.right)):
                        stack.top().children.append(Node(Sign(production.right[i].type)))
                        stack.top().children[i].parent = stack.top()

                    # 将 top 出栈
                    top = stack.pop()

                    # 将 top 的孩子节点反序入栈
                    for i in range(len(production.right) - 1, -1, -1):
                        # for child in top.children[::-1]:
                        stack.push(top.children[i])
                # 如果分析表中存放着错误信息
                else:
                    stack.pop()
                    # self.__error = SyntaxError('语法错误 ' + inputs[input_index].str, inputs[input_index].line)
                    # break
            # 如果 top 是终结符
            else:
                # 如果 top = input
                if stack.top().data.type == inputs[input_index].type:
                    # 如果 top = #，宣布分析成功
                    if stack.top().data.type == 'pound':
                        flag = False
                    # 如果 top != #
                    else:
                        # 计算 top 的 value 属性
                        stack.top().line = inputs[input_index].line
                        stack.top().value = inputs[input_index].str
                        # 将 top 出栈，让 input_index 自增
                        stack.pop()
                        input_index += 1
                # 如果 top != input
                else:
                    self.__error = SyntaxError('语法错误 ' + inputs[input_index].str, inputs[input_index].line)
                    break
        if self.__error:

            return False
        else:

            self.grammar_tree = grammar_tree
            return True
