symbol_type = [
    'void',
    'funName',
    'int',
    'bool',
    'num',
    'operator',
    'statement'
]


class Symbol:
    """
    符号基类
    """

    def __init__(self, name, type="variable", value="undefined", parent=None, return_type="void"):
        self.return_type = return_type
        self.name = name  # 变量姓名
        self.type = type
        self.value = value
        self.children = list()
        self.parent = parent


class SymbolTable:

    def __init__(self):
        self.root = Symbol("programme", "programme")
        self.nowFunc = self.root

    def update_params(self, id, value):
        nowState = self.nowFunc
        while nowState is not None:
            for i in range(len(nowState.children)):
                if nowState.children[i].type == "variable":
                    if nowState.children[i].name == id:
                        nowState.children[i].value = value
                        return True
            nowState = nowState.parent
        return False

    def push_back_params(self, symbol):
        """
        插入变量
        """
        for item in self.nowFunc.children:
            if item.type == 'variable':
                if item.name == symbol.name:
                    return False
        symbol.parent = self.nowFunc
        self.nowFunc.children.append(symbol)
        return True

    def push_back_func(self, symbol):
        """
        插入函数
        """
        for item in self.root.children:
            if item.name == symbol.name:
                return False
        symbol.parent = self.root
        self.root.children.append(symbol)
        self.nowFunc = symbol
        return True

    def find_id(self, id, need_value=True):
        """
        找该函数全局变量
        """
        nowState = self.nowFunc
        while nowState is not None:
            for item in nowState.children:
                if item.type == "variable":
                    if item.name == id:
                        if need_value:
                            if item.value == 'undefined':
                                return None
                            else:
                                return item
                        else:
                            return item
            nowState = nowState.parent
        return None

    def find_global_function(self, id):
        """
        找全局函数
        """
        for item in self.root.children:
            if item.name == id:
                return item
        return False

    def push_back_statement(self, id):
        """
        插入局部语句
        """
        symbol = Symbol(id, "statement", return_type=self.nowFunc.return_type)
        symbol.parent = self.nowFunc
        self.nowFunc.children.append(symbol)
        self.nowFunc = symbol

    def pop(self):
        """
        弹出语句或者函数
        """
        self.nowFunc = self.nowFunc.parent

    def print_item(self, root):
        print("type: ", root.type, ",name:", root.name, ",address:", id(root))
        if len(root.children) == 0:
            return
        print("children: ")
        for item in root.children:
            print("type: ", item.type, ",name:", item.name, ",address:", id(item), " return_type", item.return_type)
        print("\n")
        for item in root.children:
            self.print_item(item)

    def print_table(self):
        self.print_item(self.root)
