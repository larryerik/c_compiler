# 所有的 token 的类型
token_type = [
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
]

# 分隔符号
split_char_type = [
    'space'
]

# 注释
note_char_type = (
    'note1',
    'note2',
)

# 正则表达式字典
regex_dict = {
    'space': r'[ \t\r\a]*',
    "scanf": r"scanf",
    "printf": r"printf",
    'else': r'else',
    'if': r'if',
    'int': r'int',
    'return': r'return',
    'void': r'void',
    'while': r'while',
    'mul-operator': r'[\+|\-|\*\/\%]=',  # += -= *= /= %=
    'equal-sign': r'[>|=|<|!]=',  # >= <= == !=
    '+': r'\+',
    '-': r'\-',
    'higher-operator': r'[\*|\/|\%]',
    'single-judge': r'[>|<]',  # > <
    'input-id': r'&[_a-zA-Z][_a-zA-Z0-9]*',
    '=': r'=',
    ';': r';',
    ',': r',',
    '(': r'\(',
    ')': r'\)',
    '[': r'\[',
    ']': r'\]',
    '{': r'\{',
    '}': r'\}',
    'id': r'[_a-zA-Z][_a-zA-Z0-9]*',
    'num': r'[0-9]+',
    "++": r'\+\+',
    "--": r"\-\-",
    "string": r"\"[^\"\n]*\"",
    "note1": r"//[^\n]*",
    "note2": r"/\*((.|\n)*?)\*/",
    'for': r'for',
    'and': r'&&',
    'or': r'\|\|',
    '&': r'&',
    '!': r'!',
    'bool': r'bool',
    'char': r'char',
    'ch': r"'[a-z|A-Z]'",
    'true': r'true',
    'false': r'false',
}
