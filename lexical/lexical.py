"""
词法分析器
"""
from lexical.rule import *
from error import LexicalError
import re


class Token:
    """
    Token
    """

    def __init__(self, token_type='', token_str='', token_line=-1):
        """
        构造
        :param token_type: Token 的类型
        :param token_str: Token 的内容
        :param token_line: Token 所在行数
        """
        self.type = token_type
        self.str = token_str
        self.line = token_line


class Lexical:
    """
    词法分析器
    """

    def __init__(self):
        """
        构造
        """
        # 错误
        self.__error = None

        # 源代码
        self.__source = ''

        # 分隔出来的每一行
        self.__lines = list()

        # 结果
        self.__tokens = list()

    def load_source(self, source):
        """
        装载源代码
        :param source: 源代码
        """
        self.__source = source

    def execute(self):
        """
        执行词法分析
        :return: 词法分析是否成功
        """
        self.__del_notes()
        self.__split_lines()
        if self.__split_tokens():
            self.__del_spaces()
            return True
        else:
            return False

    def get_result(self):
        """
        获取结果
        :return: token 列表
        """
        return self.__tokens

    def get_error(self):
        """
        获取错误
        :return: 错误原因
        """
        return self.__error

    def __del_notes(self):
        """
        删除注释
        :return: 是否删除成功
        """
        for note in note_char_type:
            self.__source = re.sub(regex_dict[note], "", self.__source)

    def __split_lines(self):
        """
        将完成源代码分割成行序列
        """
        # 清空 __tokens
        self.__tokens.clear()
        # 按行分割
        temp = self.__source.split('\n')
        # 将分割出来的行序列添加到 __tokens 中
        self.__lines = temp

    def __split_tokens(self):
        """
        从行序列中分割出 token
        :return: 是否分割成功
        """
        # 先将 __lines 拷贝一份到临时变量中
        lines = list()
        for line in self.__lines:
            lines.append(line)
        # 缓冲区
        buffer = ''
        # 当前所在行数
        current_line_num = 0
        # 结果
        tokens = list()

        # 参与匹配的 type 名
        types = list()
        for i in token_type:
            types.append(i)
        for i in split_char_type:
            types.append(i)

        while len(lines) > 0:
            # 当前循环中是否匹配成功
            match_this_time = False

            # 如果缓冲区中没有数据了，就填充一行到缓冲区
            while buffer == '':
                buffer = lines[0].strip()
                del lines[0]
                # 行号自增
                current_line_num += 1
                if len(lines) == 0:
                    break

            # 开始匹配
            # 尝试用所有的正则表达式来匹配
            for t in types:  # 根据优先级匹配
                match = re.compile(regex_dict[t]).match(buffer)
                # 如果匹配到了
                if match:
                    # 将其添加到 tokens 中
                    tokens.append(Token(t, buffer[match.start():match.end()], current_line_num))
                    # buffer 去除已经匹配的部分
                    buffer = buffer[match.end():].strip()
                    match_this_time = True
                    break
            # 如果匹配完所有的正则表达式都不成功
            if not match_this_time:
                # 报错
                self.__error = LexicalError('词法错误', current_line_num)
                # 返回失败
                return False
        # 循环正常结束则说明完全匹配成功，将结果保存到 __tokens 中，返回成功
        for token in tokens:
            self.__tokens.append(token)
        return True

    def __del_spaces(self):
        """
        删除 __tokens 中的空格
        """
        # 新建临时变量
        tokens = list()
        # 将 __tokens 中的内容拷贝到 tokens 中
        for token in self.__tokens:
            tokens.append(token)
        # 清空 __tokens
        self.__tokens.clear()
        # 如果不是空格就添加进原来的 __tokens，相当于从原来的列表中去除了空格
        for token in tokens:
            if token.type != split_char_type[0]:
                self.__tokens.append(token)
