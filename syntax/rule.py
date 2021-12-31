class Sign:
    """
    符号
    """

    def __init__(self, sign_type, sign_str='', sign_line=-1):
        """
        构造
        :param sign_type: 符号的类型
        :param sign_str: 符号的内容(可以为空)
        :param sign_line: 符号所在行数(可以为空)
        """
        self.type = sign_type
        self.str = sign_str
        self.line = sign_line

    def is_terminal_sign(self):
        """
        是不是终结符
        :return: True/False
        """
        if self.type == 'empty':
            return True
        else:
            for i in terminal_sign_type:
                if i == self.type:
                    return True
            return False

    def is_non_terminal_sign(self):
        """
        是不是非终结符
        :return: True/False
        """
        for i in non_terminal_sign_type:
            if i == self.type:
                return True
        return False

    def is_empty_sign(self):
        """
        是不是空字
        :return: True/False
        """
        return self.type == 'empty'


class Production:
    """
    产生式
    """

    def __init__(self, left_type, right_types):
        """
        产生式左边
        :param left_type: 产生式左边的符号类型
        :param right_types: 产生式右边的符号类型列表
        """
        self.left = Sign(left_type)
        self.right = list()
        for i in right_types:
            self.right.append(Sign(i))

        # 调试用的
        self.string = self.left.type + ' ->'
        for i in self.right:
            self.string += ' ' + i.type


# 所有终结符的类型
terminal_sign_type = [
    "scanf",
    "printf",
    'else',
    'if',
    'int',
    'bool',
    'char',
    'return',
    'true',
    'false',
    'void',
    'while',
    'for',
    'input-id',
    "string",
    'ch',
    'id',
    'num',
    "++",
    "--",
    'and',
    'or',
    'mul-operator',  # += -= *= /= %=
    'equal-sign',  # >= <= == !=
    '+',
    '-',  # + -
    'higher-operator',
    'single-judge',  # > < !
    '=',  # =
    ';',
    ',',
    '&',
    '(',
    ')',
    '[',
    ']',
    '{',
    '}',
    '!',
    # 在这之前添加非终结符类型，请务必不要动 'pound'
    'pound'  # 表示# 号意味着结束
]

# 所有非终结符的类型
non_terminal_sign_type = [

]

# 文法产生式
productions = [
]


def fileOutProductions():
    f = open("grammar.txt",encoding="utf-8")
    non_terminal_sign = set()
    global productions
    while True:
        line = f.readline()
        if line:
            string = line.split('->')
            left = string[0].strip()
            non_terminal_sign.add(left)
            rights = string[1].strip().split(' ')
            right = []
            for r in rights:
                if r == '' or r == '@':
                    continue
                right.append(r)
            c = Production(left, right)
            productions.append(c)
        else:
            break
    global non_terminal_sign_type
    for type in (list)(non_terminal_sign):
        non_terminal_sign_type.append(type)


# 文法开始符号
grammar_start = Sign('程序')
