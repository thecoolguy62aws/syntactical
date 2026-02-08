import sys
import argparse
from lark import Lark, Transformer, v_args
import os

# --- SYNTACTICAL GRAMMAR ---
custom_grammar = r"""
    start: line_content+
    ?line_content: statement (SEMICOLON statement)* [SEMICOLON]
    ?statement: use_stmt | with_stmt | class_def | func_def | return_stmt 
             | assignment | if_stmt | while_stmt | for_stmt | try_stmt | expression | from_stmt
    block: "{" line_content+ "}"
    use_stmt: "use" IDENTIFIER ["as" IDENTIFIER]
    from_stmt: "from" IDENTIFIER "use" IDENTIFIER
    with_stmt: "with" expression "as" IDENTIFIER block
    class_def: "class" IDENTIFIER block
    func_def: "func" IDENTIFIER "(" [id_list] ")" block
    return_stmt: "return" expression
    try_stmt: "try" block "catch" IDENTIFIER block
    if_stmt: "if" expression block ["else" block]
    while_stmt: "while" expression block
    ?for_stmt: "for" IDENTIFIER "in" expression "to" expression block -> range_for
             | "for" "(" assignment SEMICOLON expression SEMICOLON assignment ")" block -> c_for
    assignment: target (EQUAL | INPLACE_OP) expression
    inc_dec_stmt: target INC_DEC_OP
    ?expression: logic_or
    ?logic_or: logic_and ("or" logic_and)*
    ?logic_and: logic_not ("and" logic_not)*
    ?logic_not: "not" logic_not -> logic_not | comparison
    ?comparison: sum (COMP_OP sum)*
    ?sum: product (SUM_OP product)*
    ?product: atom (MUL_OP atom)*
    ?atom: lambda_expr | primary | NUMBER | STRING | bool | list | set | dict | "(" expression ")"
    lambda_expr: "lambda" [id_list] "{" expression "}"
    ?primary: dotted_name | primary "(" [arg_list] ")" -> function_call | primary "[" expression "]" -> index_access
    dotted_name: IDENTIFIER ("." IDENTIFIER)*
    arg_list: expression ("," expression)*
    id_list: IDENTIFIER ("," IDENTIFIER)*
    list: "[" [arg_list] "]"
    set: "{" arg_list "}"
    dict: "{" [dict_pairs] "}"
    dict_pairs: key_value ("," key_value)*
    key_value: expression ":" expression
    bool: "true" -> true | "false" -> false
    target: dotted_name ("[" expression "]")*
    EQUAL: "="
    INPLACE_OP: "+=" | "-=" | "*=" | "/="
    INC_DEC_OP: "++" | "--"
    SUM_OP: "+" | "-"
    MUL_OP: "*" | "/"
    COMP_OP: "==" | "!=" | "<" | ">" | "<=" | ">="
    SEMICOLON: ";"
    IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/
    STRING: /\"\"\"(?s:.*?)\"\"\"|\'\'\'(?s:.*?)\'\'\'|\"(?:[^\"\\\\]|\\\\.)*\"|\'(?:[^\'\\\\]|\\\\.)*\'/
    COMMENT: "//" /[^\n]*/
    %import common.NUMBER
    %import common.WS
    %ignore WS
    %ignore COMMENT
"""

@v_args(inline=True)
class ToPython(Transformer):
    def start(self, *lines): 
        # Inject imports automatically
        return "import os\nimport json\n" + "\n".join(map(str, lines))

    def line_content(self, *statements):
        return "\n".join(str(s) for s in statements if str(s) != ";")
    
    def block(self, *lines):
        body = "\n".join(map(str, lines))
        return "\n".join(f"    {line}" for line in body.split("\n"))

    def lambda_expr(self, args=None, expr=None):
        if expr is None: return f"lambda: {args}"
        return f"lambda {args}: {expr}"

    def function_call(self, name, args=""):
        py_name = str(name)
        call_args = str(args) if args is not None else ""
        if py_name == "print": return f"print({call_args}, end='')"
        if py_name == "println": return f"print({call_args})"
        if py_name == "input": return f"input({call_args})"
        if py_name == "system": return f"os.system({call_args})"
        

        if py_name == "jsonEncode": return f"json.dumps({call_args})"
        if py_name == "jsonDecode": return f"json.loads({call_args})"
        
        return f"{py_name}({call_args})"

    def STRING(self, token):
        raw = str(token)
        return f"f{raw}" if "{" in raw and "}" in raw else raw

    def use_stmt(self, name, alias=None): return f"import {name} as {alias}" if alias else f"import {name}"
    def from_stmt(self, name, module): return f"from {name} import {module}"
    def try_stmt(self, t_b, e_v, c_b): return f"try:\n{t_b}\nexcept Exception as {e_v}:\n{c_b}"
    def class_def(self, n, b): return f"class {n}:\n{b}"
    def func_def(self, n, a=None, b=""): return f"def {n}({a or ''}):\n{b}"
    def range_for(self, v, s, e, b): return f"for {v} in range({s}, {e}):\n{b}"
    def c_for(self, i, c, s, b): return f"{i}\nwhile {c}:\n{b}\n    {s}"
    def if_stmt(self, c, b, eb=None): return f"if {c}:\n{b}" + (f"\nelse:\n{eb}" if eb else "")
    def while_stmt(self, c, b): return f"while {c}:\n{b}"
    def with_stmt(self, c, h, b): return f"with {c} as {h}:\n{b}"
    def return_stmt(self, e): return f"return {e}"
    def assignment(self, t, o, v): return f"{t} {o} {v}"
    def index_access(self, t, i): return f"{t}[{i}]"
    def dotted_name(self, *p): return ".".join(map(str, p))
    def arg_list(self, *i): return ", ".join(map(str, i))
    def id_list(self, *i): return ", ".join(map(str, i))
    def list(self, i=""): return f"[{i or ''}]"
    def set(self, items): return f"{{{items}}}"
    def dict(self, i=""): return f"{{{i or ''}}}"
    def dict_pairs(self, *p): return ", ".join(map(str, p))
    def key_value(self, k, v): return f"{k}: {v}"
    def true(self): return "True"
    def false(self): return "False"
    def logic_not(self, v): return f"not {v}"
    def logic_or(self, *args): return " or ".join(map(str, args))
    def logic_and(self, *args): return " and ".join(map(str, args))
    def target(self, name, *indices):
        res = str(name)
        for idx in indices: res += f"[{idx}]"
        return res
    def comparison(self, *a): return " ".join(map(str, a))
    def sum(self, *a): return " ".join(map(str, a))
    def product(self, *a): return " ".join(map(str, a))
    def IDENTIFIER(self, t): return str(t)
    def NUMBER(self, t): return str(t)
    def COMP_OP(self, t): return str(t)
    def SUM_OP(self, t): return str(t)
    def MUL_OP(self, t): return str(t)
    def INPLACE_OP(self, t): return str(t)
    def INC_DEC_OP(self, t): return str(t)
    def EQUAL(self, t): return str(t)
    def SEMICOLON(self, t): return ";"

def main():
    arg_parser = argparse.ArgumentParser(description="Syntactical Language Runner")
    arg_parser.add_argument("filename", help="Path to your script")
    arg_parser.add_argument("-p", "--python", action="store_true", help="Instead of running the code, save it as python in the same directory.")
    args = arg_parser.parse_args()

    try:
        with open(args.filename, "r") as f: source = f.read()
        l_parser = Lark(custom_grammar, parser='lalr')
        python_code = ToPython().transform(l_parser.parse(source))

        if not args.python:
            exec(python_code, {"__name__": "__main__"})
        else:
            if args.filename.endswith(".syn"):
                python_file_name = f"{args.filename[:-4]}.py"
            else:
                python_file_name = f"{args.filename}.py"
            if os.path.isfile(python_file_name):
                print("File already exists.")
                exit(1)
            else:
                with open(python_file_name, 'w') as f:
                    f.write(python_code)
    except Exception as e:
        print(f"Syntactical Error: {e}")

if __name__ == "__main__":
    main()