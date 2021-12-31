from semantic.symbol import *

grammar_transformation = {
    '变量申请': 'for_variables',
    '判断语句': 'judgement',
    '循环语句': 'loop',
    '赋值语句与函数调用': 'assignment_and_func',
    "id": "id",
    "单目运算符": 'unary_operator',
    "printf": "printf",
    "scanf": "scanf",
    "正确或者错误": 'right_or_wrong',
    "运算": 'opr',
}
error_message = {
    "undefined": "变量未定义",
    "uninitialized": "变量未赋值",
    "returnType": "函数返回类型错误",
    "type": "变量类型错误",
    "NotFoundFunc": "未找到函数定义",
    "sameFunc": "函数重复定义",
    "sameVariable": '变量重复定义',
    "typeError": "此类型不能运算",
}


class Semantic(object):

    def __init__(self, grammar_tree):
        self.grammar_tree = grammar_tree
        self.symbolTable = SymbolTable()
        self.middle_code = list()
        self.error = False
        self.temp_index = 1
        self.temp_str = "temp"

    def execute(self):
        if self.error:
            return
        self.__producer(self.grammar_tree)

    def __producer(self, node):
        """
        程序 已完结
        """
        if self.error:
            return
        self.__func(node.children[0])

    def __func(self, node):
        """
        函数 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return
        return_type = self.__return_type(node.children[0])
        id = node.children[1].value
        symbol = Symbol(name=id, type="function", return_type=return_type)
        # 函数重名报错
        if not self.symbolTable.push_back_func(symbol):
            self.__print_error(node.children[1], "sameFunc")
        else:
            parameter_list = list()
            self.__formal_parameter(node.children[3], parameter_list)
            self.middle_code.append(('BEGINFUNC', id, parameter_list))
            self.__function_body(node.children[6])
            self.middle_code.append(('ENDFUNC', id, parameter_list))
            self.symbolTable.pop()
            self.__func(node.children[8])

    def __formal_parameter(self, node, parameter_list):
        """
        形参 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return
        return_type = self.__return_type(node.children[0])
        id = node.children[1].value
        symbol = Symbol(name=id, type="variable", return_type=return_type, value="0")
        if not self.symbolTable.push_back_params(symbol):
            # 变量重复报错
            self.__print_error(node.children[1], "sameVariable")
        parameter_list.append(id)
        self.__formal_parameter2(node.children[2], parameter_list)

    def __formal_parameter2(self, node, parameter_list):
        """
        形参2 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return
        self.__formal_parameter(node.children[1], parameter_list)

    def __function_body(self, node):
        """
        函数主体 已完结
        """
        if self.error:
            return
        self.__processing_statement(node.children[0])
        self.__return_statement(node.children[1])

    def __processing_statement(self, node):
        """
        处理语句 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return
        global grammar_transformation
        if grammar_transformation[node.children[0].type] == 'for_variables':
            self.__for_variables(node.children[0])
        elif grammar_transformation[node.children[0].type] == 'judgement':
            self.__judgement_statement(node.children[0])
        elif grammar_transformation[node.children[0].type] == 'assignment_and_func':
            self.__assignment_and_func(node.children[0])
        elif grammar_transformation[node.children[0].type] == 'loop':
            self.__loop_statement(node.children[0])
        self.__processing_statement(node.children[len(node.children) - 1])

    def __loop_statement(self, node):
        """
        循环语句 已完结
        """
        if self.error:
            return
        if node.children[0].value == "while":
            self.middle_code.append(("BEGIN", "WHILE"))
            self.symbolTable.push_back_statement("while")
            self.middle_code.append(('BEGIN', 'CONDITION'))
            self.__condition(node.children[2])
            self.middle_code.append(('END', 'CONDITION'))
            self.__processing_statement(node.children[5])
            self.middle_code.append(('END', 'WHILE'))
            self.symbolTable.pop()
        else:
            self.middle_code.append(('BEGIN', 'FOR'))
            self.symbolTable.push_back_statement('for')
            self.__for__number1(node.children[2])
            self.middle_code.append(('BEGIN', 'CONDITION'))
            self.__condition(node.children[3])
            self.middle_code.append(('END', 'CONDITION'))
            self.__processing_statement(node.children[8])
            self.__assignment_and_func(node.children[5])
            self.middle_code.append(('END', 'FOR'))
            self.symbolTable.pop()

    def __for__number1(self, node):
        """
        for 第一段 已完结
        """
        if self.error:
            return
        if len(node.children) == 1:
            self.__for_variables(node.children[0])
        else:
            self.__assignment_and_func(node.children[0])

    def __assignment_and_func(self, node):
        """
        赋值语句与函数调用 已完结
        """
        if self.error:
            return
        global grammar_transformation
        if grammar_transformation[node.children[0].type] == "id":
            self.__assignment(node.children[0].value, node.children[1])
        elif grammar_transformation[node.children[0].type] == "unary_operator":
            if self.symbolTable.find_id(node.children[1].value, need_value=True):
                self.middle_code.append((node.children[0].children[0].value, node.children[1].value))
            else:
                self.__print_error(node.parent.children[1], "uninitialized")
        elif grammar_transformation[node.children[0].type] == "printf":
            self.middle_code.append(("OUT", node.children[2].value, self.__output_variables(node.children[3])))
        else:
            self.middle_code.append(("INPUT", self.__input_variables(node.children[4])))

    def __input_variables(self, node):
        """
        输入的变量 已完结
        """
        if self.error:
            return
        variable = list()
        string = node.children[0].value[1:]
        if self.symbolTable.find_id(string, need_value=False):
            self.symbolTable.update_params(string, "0")
            variable.append(string)
            self.__input_variables2(node.children[1], variable)
            return variable
        else:
            self.__print_error(node.children[0], "undefined")

    def __input_variables2(self, node, list):
        """
        输入变量2 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return
        else:
            string = node.children[1].value[1:]
            if self.symbolTable.find_id(string, need_value=False):
                self.symbolTable.update_params(string, "0")
                list.append(string)
                self.__input_variables2(node.children[2], list)
                return list
            else:
                self.__print_error(node.children[0], "undefined")
            self.__input_variables2(node.children[2], list)

    def __output_variables(self, node):
        """
        输出的变量 已完结
        """
        if self.error:
            return
        variable = list()
        if len(node.children) == 0:
            return variable
        self.__variables(node.children[1], variable)
        return variable

    def __assignment(self, left_node, node):
        """
        赋值语句 已完结
        """
        if self.error:
            return
        if len(node.children) == 2:
            expr = self.__operation(node.children[1])
            if node.children[0].type == '=':
                item = self.symbolTable.find_id(left_node, need_value=False)
                if item:
                    if item.return_type != expr.return_type:
                        self.__print_error(node.parent.children[0], "typeError")
                        return
                    else:
                        self.symbolTable.update_params(left_node, expr.name)
                        self.middle_code.append(('=', left_node, expr.name))
                else:
                    self.__print_error(node.parent.children[0], "undefined")
                    return
            else:
                item = self.symbolTable.find_id(left_node, need_value=True)
                if item:
                    if item.return_type != expr.return_type:
                        self.__print_error(node.parent.children[0], "typeError")
                    else:
                        self.symbolTable.update_params(left_node, expr.name)
                        opr = node.children[0].value
                        self.middle_code.append((opr, left_node, expr.name))
                else:
                    self.__print_error(node.parent.children[0], "uninitialized")
        elif len(node.children) == 1:
            item = self.symbolTable.find_id(left_node, need_value=True)
            if item:
                if item.return_type != 'int':
                    self.__print_error(node.parent.children[0], "typeError")
                else:
                    self.middle_code.append((node.children[0].children[0].value, left_node))
            else:
                self.__print_error(node.parent.children[0], "uninitialized")
        else:
            variable_list = list()
            self.__variables(node.children[1], variable_list)
            self.middle_code.append(("CALLFUNC", left_node, variable_list))

    def __for_variables(self, node):
        """
        变量申请 已完结
        """
        if self.error:
            return
        return_type = self.__return_type(node.children[0])
        init_value = self.__initialization(node.children[2])
        if init_value.name != 'undefined':
            if return_type != init_value.return_type:
                self.__print_error(node.children[1], "typeError")
        id = node.children[1].value
        symbol = Symbol(name=id, return_type=return_type, value=init_value.name)
        if not self.symbolTable.push_back_params(symbol):
            self.__print_error(node.children[1], "sameVariable")
        else:
            self.middle_code.append((return_type, '=', id, init_value.name))

    def __initialization(self, node):
        """
        赋初值 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return Symbol(name='undefined')
        else:
            return self.__initialization_content(node.children[1])

    def __initialization_content(self, node):
        """
        赋初值内容 已完结
        """
        if self.error:
            return
        if node.children[0].type == 'ch':
            return Symbol(name=node.children[0].value, return_type='char')
        elif grammar_transformation[node.children[0].type] == 'right_or_wrong':
            return Symbol(name=node.children[0].children[0].value, return_type='bool')
        else:
            return self.__operation(node.children[0])

    def __return_statement(self, node):
        """
        返回语句 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            if self.symbolTable.nowFunc.type == 'function':
                if not self.symbolTable.nowFunc.return_type == 'void':
                    self.__print_error(node.parent.parent.children[1], "returnType")
        else:
            expr = self.__operation(node.children[1])
            if not self.symbolTable.nowFunc.return_type == expr.return_type:
                self.__print_error(node.parent.parent.children[1], "returnType")
            else:
                self.middle_code.append(('RETURN', expr.name))

    def __entire_varibale(self, node):
        """
        整体变量 已完结
        """
        if self.error:
            return
        if len(node.children) == 1:
            return self.__number(node.children[0])
        else:
            return self.__function_and_operation(node.children[0], node.children[1])

    def __operation(self, node):
        """
        运算 已完结
        """
        if self.error:
            return
        left_node = self.__high_level(node.children[0])
        return self.__low_level2(left_node, node.children[1])

    def __very_high_level(self, node):
        """
        超高级 已完结
        """
        if self.error:
            return
        if len(node.children) == 1:
            return self.__entire_varibale(node.children[0])
        else:
            return self.__operation(node.children[1])

    def __high_level2(self, left_node, node):
        """
        高级2 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return left_node
        else:
            right_node = self.__very_high_level(node.children[1])
            if left_node.return_type != right_node.return_type:
                self.__print_error(node.children[0], "typeError")
                return
            else:
                id = self.temp_str + str(self.temp_index)
                self.temp_index += 1
                self.middle_code.append((node.children[0].value, left_node.name, right_node.name, id))
                this_node = Symbol(name=id, return_type=right_node.return_type)
                return self.__high_level2(this_node, node.children[2])

    def __high_level(self, node):
        """
        高级 已完结
        """
        if self.error:
            return
        left_node = self.__very_high_level(node.children[0])
        return self.__high_level2(left_node, node.children[1])

    def __low_level2(self, left_node, node):
        """
        低级2
        """
        if self.error:
            return
        if len(node.children) == 0:
            return left_node
        else:
            right_node = self.__high_level(node.children[1])
            if left_node.return_type != right_node.return_type:
                self.__print_error(node.children[0].children[0], "typeError")
            else:
                id = self.temp_str + str(self.temp_index)
                self.temp_index += 1
                self.middle_code.append((node.children[0].children[0].value, left_node.name, right_node.name, id))
                this_node = Symbol(name=id, return_type=left_node.return_type)
                return self.__low_level2(this_node, node.children[2])

    def __function_and_operation(self, left_node, node):
        """
        函数调用或运算 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            item = self.symbolTable.find_id(left_node.value, need_value=True)
            if item:
                return item
            else:
                self.__print_error(node.parent.children[0], "uninitialized")
        else:
            variables_list = list()
            self.__variables(node.children[1], variables_list)
            # 是函数调用，赋予命名
            item = self.symbolTable.find_global_function(left_node.value)
            if item:
                id = self.temp_str + str(self.temp_index)
                self.temp_index += 1
                self.middle_code.append(("CALLFUNC", left_node.value, variables_list, id))
                return Symbol(name=id, return_type=item.return_type)
            else:
                self.__print_error(node.parent.children[0], "NotFoundFunc")

    def __variables(self, node, variables_list):
        """
        变量 已完结
        """
        if self.error:
            return
        variables_list.append(self.__operation(node.children[0]).name)
        self.__variables2(node.children[1], variables_list)

    def __variables2(self, node, variables_list):
        """
        变量2 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return
        variables_list.append(self.__operation(node.children[1]).name)
        self.__variables2(node.children[2], variables_list)

    def __judgement_statement(self, node):
        """
        判断语句 已完结
        """
        if self.error:
            return
        self.symbolTable.push_back_statement("judge")
        self.symbolTable.push_back_statement("if")
        self.middle_code.append(('BEGIN', 'JUDGEMENT'))
        self.middle_code.append(('BEFIN', 'IF'))
        self.middle_code.append(('BEGIN', 'CONDITION'))
        self.__condition(node.children[2])
        self.middle_code.append(('END', 'CONDITION'))
        self.__function_body(node.children[5])
        self.middle_code.append(('END', 'IF'))
        self.symbolTable.pop()  # 跳出if
        self.__other_judge_statement(node.children[7])
        self.middle_code.append(('END', 'JUDGEMENT'))
        self.symbolTable.pop()  # 跳出judge

    def __other_judge_statement(self, node):
        """
        其他判断语句 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return
        self.__subjudgement_statement(node.children[1])

    def __subjudgement_statement(self, node):
        """
        子判断语句 已完结
        """
        if self.error:
            return
        if len(node.children) == 3:
            self.symbolTable.push_back_statement("else")
            self.middle_code.append(('BEGIN', 'ELSE'))
            self.__function_body(node.children[1])
            # 连续出两个，跳出判断语句
            self.middle_code.append(('END', 'ELSE'))
            self.symbolTable.pop()
            return
        self.symbolTable.push_back_statement("else if")
        self.middle_code.append(('BEGIN', 'ELSE IF'))
        self.middle_code.append(('BEGIN', 'CONDITION'))
        condition = self.__condition(node.children[2])
        self.middle_code.append(('END', 'CONDITION'))
        self.__function_body(node.children[5])
        self.middle_code.append(('END', 'ELSE IF'))
        self.symbolTable.pop()
        self.__other_judge_statement(node.children[7])

    def __condition(self, node):
        """
        条件 已完结
        """
        if self.error:
            return
        left_node = self.__judge(node.children[0])
        return self.__subjudgement(left_node, node.children[1])

    def __number(self, node):
        """
        数字
        """
        if self.error:
            return
        if len(node.children) == 1:
            return Symbol(name=node.children[0].value, return_type="int")
        else:
            return Symbol(name='-' + node.children[1].value, return_type="int")

    def __judge(self, node):
        """
        判断 已完结
        """
        if self.error:
            return
        if len(node.children) == 3:
            expr1 = self.__operation(node.children[0])
            expr2 = self.__operation(node.children[2])
            if expr1.return_type != expr2.return_type:
                self.__print_error(node.children[1].children[0], "typeError")
                return
            opr = node.children[1].children[0].value
            id = self.temp_str + str(self.temp_index)
            self.temp_index += 1
            self.middle_code.append((opr, expr1.name, expr2.name, id))
            return id
        else:
            right_id = self.__judge(node.children[2])
            id = self.temp_str + str(self.temp_index)
            self.temp_index += 1
            self.middle_code.append(("!", right_id, id))
            return id

    def __subjudgement(self, left_node, node):
        """
        子判断条件 已完结
        """
        if self.error:
            return
        if len(node.children) == 0:
            return left_node
        right_id = self.__judge(node.children[1])
        id = self.temp_str + str(self.temp_index)
        self.temp_index += 1
        self.middle_code.append((node.children[0].value, left_node, right_id, id))
        return self.__subjudgement(id, node.children[2])

    def __return_type(self, node):
        """
        返回值类型 已完结
        """
        if self.error:
            return
        return node.children[0].value

    def __print_error(self, node, string):
        self.error = True
        print("语义错误 %s in line %s " % (node.value, node.line))
        print("错误原因：%s" % error_message[string])
