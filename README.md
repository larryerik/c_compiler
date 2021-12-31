python实现c编译到汇编代码

词法分析使用正则表达式，语法分析使用LL(1)文法分析器，
语义分析使用自上而下翻译

* main.py 编译器主程序
* error.py 存放错误相关的类和代码
* test.c 要编译的文件
* lexical 词法分析
* syntax 语法分析
* semantic 语义分析

rule.py 支持编译器的所有文法、词法、语义规则
