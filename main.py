"""
主程序
"""
from lexical.lexical import Lexical
from syntax.rule import fileOutProductions
from syntax.syntax import Syntax
from semantic.rule import *
from target.targetcode import AsmCode

# 创建词法分析器
lexical = Lexical()
# 载入源代码
with open('test.c') as text:
    sources = text.read()
lexical.load_source(sources)
# 执行词法分析
lexical_success = lexical.execute()
# 打印结果
print('词法分析是否成功:\t', lexical_success)
if lexical_success:
    lexical_result = lexical.get_result()
    print('词法分析结果:')
    for i in lexical_result:
        print(i.type, i.str, i.line)

    # # 开始执行语法分析
    fileOutProductions()
    syntax = Syntax()
    syntax.put_source(lexical_result)
    syntax_success = syntax.execute()
    print('语法分析和语义分析是否成功\t', syntax_success)
    if syntax_success:
        # print('语法分析结果:\n')
        # Tree.print_tree(syntax.grammar_tree.root)
        # print('语以分析结果:\n')
        semantic = Semantic(syntax.grammar_tree.root)
        semantic.execute()
        # 语义分析
        if not semantic.error:
            for item in semantic.middle_code:
                print(item)
            # 符号表
            semantic.symbolTable.print_table()
            asm_code = AsmCode()
            asm_code.push_code(semantic.middle_code)
            asm_code.run()
            asm_code.print_code()
    else:
        print('错误原因:\t', syntax.get_error().info, syntax.get_error().line, '行')
else:
    print('错误原因:\t', lexical.get_error().info)
