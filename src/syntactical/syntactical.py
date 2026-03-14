import sys
import argparse
from lark import Lark, Transformer, v_args
import os
from syntactical import version # This imports the __version__ variable from version.py

# This is the main grammar of the language; it has all of the statements and things:
grammar = r"""
    start: line_content+
    ?line_content: statement (SEMICOLON statement)* [SEMICOLON]
    ?statement: import_stmt | with_stmt | class_def | func_def | return_stmt 
            | assignment | if_stmt | while_stmt | for_stmt | try_stmt 
            | break_stmt | continue_stmt | pass_stmt | inc_dec_stmt
            | expression | from_stmt | global_stmt
    break_stmt: "break"
    continue_stmt: "continue"
    pass_stmt: "pass"
    global_stmt: "global" id_list
    block: "{" line_content+ "}"
    module_path: IDENTIFIER (("." IDENTIFIER) | ("/" IDENTIFIER))*
    import_stmt: "import" module_path ["as" IDENTIFIER]
    from_stmt: "from" module_path "import" IDENTIFIER
    with_stmt: "with" expression "as" IDENTIFIER block
    class_def: "class" IDENTIFIER block
    func_def: "func" IDENTIFIER "(" [id_list] ")" block
    return_stmt: "return" expression
    try_stmt: "try" block "catch" IDENTIFIER block
    if_stmt: "if" expression block ("else" "if" expression block)* ["else" block]
    while_stmt: "while" expression block
    ?for_stmt: "for" IDENTIFIER "in" expression "to" expression block -> range_for
            | "for" IDENTIFIER "in" expression block               -> iterable_for
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
    lambda_expr: "func" "(" [id_list] ")" "=>" "{" expression "}"
    ?primary: dotted_name | primary "(" [arg_list] ")" -> function_call | primary "[" expression "]" -> index_access
    dotted_name: IDENTIFIER ("." IDENTIFIER)*
    arg_list: argument ("," argument)*
    ?argument: IDENTIFIER "=" expression   -> kw_argument
            | expression
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
    MUL_OP: "*" | "/" | "%"
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
# This is the class for the main transformer; it is like the core of this whole language:
@v_args(inline=True)
class ToPython(Transformer):

    # The start; this is like where the transformer well, starts, just what it does first:
    def start(self, *lines): 
        # Inject imports automatically:
        return "import os\nimport json\nimport time\n" + "\n".join(map(str, lines))

    # Litterly just the content on a line:
    def line_content(self, *statements):
        return "\n".join(str(s) for s in statements if str(s) != ";")
    
    # A block (like the code in a if statement with {curly brackets}):
    def block(self, *lines):
        body = "\n".join(map(str, lines))
        return "\n".join(f"    {line}" for line in body.split("\n"))

    # Lambda expression:
    def lambda_expr(self, args=None, expr=None):
        if expr is None: return f"lambda: {args}"
        return f"lambda {args}: {expr}"

    # Function calls are here. Here you can find all the functions in the language:
    def function_call(self, name, args=""):
        py_name = str(name)
        call_args = str(args) if args is not None else ""

        # Print functions:
        if py_name == "print": return f"print({call_args}, end='')"
        if py_name == "println": return f"print({call_args})"

        # Input functions:
        if py_name == "input": return f"input({call_args})"

        # System functions:
        if py_name == "system": return f"os.system({call_args})"

        # All json functions:
        if py_name == "json_dumps": return f"json.dumps({call_args})"
        if py_name == "json_dump": return f"json.dump({call_args})"
        if py_name == "json_loads": return f"json.loads({call_args})"
        if py_name == "json_load": return f"json.load({call_args})"
        
        # Exit and stop functions:
        exit_aliases = ["exit", "stop"] # aliases for exit()
        if py_name in exit_aliases: return f"exit({call_args})"

        # Time sleep function:
        if py_name == "sleep": return f"time.sleep({call_args})"

        return f"{py_name}({call_args})"

    # A string:
    def STRING(self, token):
        raw = str(token)
        return f"f{raw}" if "{" in raw and "}" in raw else raw

    # These next few methods are import statement stuff:        
    def module_path(self, *parts):
        return "".join(str(p) for p in parts).replace("/", ".")

    # This is the import statement:
    def import_stmt(self, name, alias=None):
        module = str(name)
        alias_name = alias if alias else module.split(".")[-1]

        code = f"""
import os, sys, importlib.util

_module_name = "{module}"
_module_path = _module_name.replace(".", os.sep)

_syn_file = None
_py_file = None

# Search current dir + sys.path
for _p in [""] + sys.path:
    syn_candidate = os.path.join(_p, _module_path + ".syn")
    py_candidate = os.path.join(_p, _module_path + ".py")

    if os.path.isfile(syn_candidate):
        _syn_file = syn_candidate
        break

    if os.path.isfile(py_candidate):
        _py_file = py_candidate
        break

if _syn_file:
    from syntactical import toPython

    with open(_syn_file, "r") as f:
        _syn_code = f.read()

    _py_code = toPython(_syn_code)

    _module_globals = {{}}
    exec(_py_code, _module_globals)

    {alias_name} = type("SyntacticalModule", (), _module_globals)

elif _py_file:
    spec = importlib.util.spec_from_file_location("{alias_name}", _py_file)
    {alias_name} = importlib.util.module_from_spec(spec)
    spec.loader.exec_module({alias_name})

else:
    import importlib
    {alias_name} = importlib.import_module(_module_name)
        """
        return code

    # This is for if you use "from" with import:
    def from_stmt(self, name, module): return f"from {name} import {module}"

    # The try, catch statement:
    def try_stmt(self, t_b, e_v, c_b): return f"try:\n{t_b}\nexcept Exception as {e_v}:\n{c_b}"

    # Here's the class def:
    def class_def(self, n, b): return f"class {n}:\n{b}"

    # Here's the function def:
    def func_def(self, n, a=None, b=""): return f"def {n}({a or ''}):\n{b}" if n != "initialization" else f"def __init__({a or ''}):\n{b}"

    # Here's the for loops
    def range_for(self, v, s, e, b): return f"for {v} in range({s}, {e}):\n{b}"
    def c_for(self, i, c, s, b): return f"{i}\nwhile {c}:\n{b}\n    {s}"
    def iterable_for(self, var, iterable, body):
        return f"for {var} in {iterable}:\n{body}"

    # Break, continue, and pass statements:
    def break_stmt(self): return "break"
    def continue_stmt(self): return "continue"
    def pass_stmt(self): return "pass"

    # Here's the if statement, it's kind of complicated:
    def if_stmt(self, *parts):
        parts = [p for p in parts if p is not None]

        result = f"if {parts[0]}:\n{parts[1]}"
        i = 2

        while i + 1 < len(parts):
            result += f"\nelif {parts[i]}:\n{parts[i+1]}"
            i += 2

        if i < len(parts):
            result += f"\nelse:\n{parts[i]}"

        return result
    
    # Here's the while statement:
    def while_stmt(self, c, b): return f"while {c}:\n{b}"

    # Here's the with statement:
    def with_stmt(self, c, h, b): return f"with {c} as {h}:\n{b}"

    # This is the return statement.
    def return_stmt(self, e): return f"return {e}"

    # Increment statements:
    def inc_dec_stmt(self, name, op):
        if op == "++": return f"{name} = {name} + 1"
        elif op == "--": return f"{name} = {name} - 1"
        else: print("Syntactical (no pun intended) Error: bad incrementer (if all goes well, you should never see this error)")

    # Variable assignment:
    def assignment(self, t, o, v): return f"{t} {o} {v}"

    # Accessing index of list with [square brackets]
    def index_access(self, t, i): return f"{t}[{i}]"

    # Hierarchical dotted name:
    def dotted_name(self, *p): return ".".join(map(str, p))

    # Any list of arguments:
    def arg_list(self, *i): return ", ".join(map(str, i))

    # A specific keyword argument:
    def kw_argument(self, name, value): return f"{name}={value}"

    # Any list of identifiers:
    def id_list(self, *i): return ", ".join(map(str, i))

    # A list with [square brackets]:
    def list(self, i=""): return f"[{i or ''}]"

    # A set with {curly brackets}:
    def set(self, items): return f"{{{items}}}"

    # A dictionary with {curly brackets}:
    def dict(self, i=""): return f"{{{i or ''}}}"

    # The pairs inside a dictionary:
    def dict_pairs(self, *p): return ", ".join(map(str, p))

    # Any key values:
    def key_value(self, k, v): return f"{k}: {v}"

    # True:
    def true(self): return "True"

    # False:
    def false(self): return "False"

    # Some logic keywords:
    def logic_not(self, v): return f"not {v}"
    def logic_or(self, *args): return " or ".join(map(str, args))
    def logic_and(self, *args): return " and ".join(map(str, args))

    # Specifying a target:
    def target(self, name, *indices):
        res = str(name)
        for idx in indices: res += f"[{idx}]"
        return res
    
    # A comparison:
    def comparison(self, *a): return " ".join(map(str, a))

    # The global statement:
    def global_stmt(self, i): return f"global {i}"

    # Getting a sum:
    def sum(self, *a): return " ".join(map(str, a))

    # Getting a product:
    def product(self, *a): return " ".join(map(str, a))

    # Any identifier (like a name with a bunch of letters):
    def IDENTIFIER(self, t): return str(t)

    # Any number:
    def NUMBER(self, t): return str(t)

    # A compare operator:
    def COMP_OP(self, t): return str(t)

    # A sum operator:
    def SUM_OP(self, t): return str(t)

    # A multiplication operator:
    def MUL_OP(self, t): return str(t)

    # Any inplace operation:
    def INPLACE_OP(self, t): return str(t)

    # The increment or decrement operators:
    def INC_DEC_OP(self, t): return str(t)

    # The equal sign:
    def EQUAL(self, t): return str(t)

    # A semicolon:
    def SEMICOLON(self, t): return ";"

# This is the main function with the CLI arguments and stuff:
def main():
    # Just the arg_parser object:
    arg_parser = argparse.ArgumentParser(description="Syntactical Language Runner")

    # --version prints the current version of Syntactical in your terminal:
    arg_parser.add_argument('--version', action='version', version=f'Syntactical {version.__version__}')

    # The path to the Syntactical program/script:
    arg_parser.add_argument("filename", help="Path to your script")

    # This is --python; if used code gets saved as a Python file instead of running:
    arg_parser.add_argument("-p", "--python", action="store_true", help="Instead of running the code, save it as python in the same directory.")

    args, unknown = arg_parser.parse_known_args()

    # This checks if --version is used, if it is then argparse can handle it and we'll just exit:
    if '--version' in sys.argv:
        # handled by argparse, just exit
        exit(0)

    # Here your Syntactical code gets parsed, converted to Python, then either run or saved to a file:
    try:
        # Here the file you specified gets read:
        with open(args.filename, "r") as f: source = f.read()

        # Now the parser parses it:
        l_parser = Lark(grammar, parser='lalr')

        # Then the Python code gets generated with that "ToPython" class up there:
        python_code = ToPython().transform(l_parser.parse(source))

        # If the --python switch was not specified, run the code:
        if not args.python:
            exec(python_code, {"__name__": "__main__"})

        # If the --python switch was used, save the code as a file:
        else:
            python_file_name = f"{args.filename}.py"
            if os.path.isfile(python_file_name):
                print("File already exists.")
                exit(1)
            else:
                with open(python_file_name, 'w') as f:
                    f.write(python_code)

    # If an exception gets called print an error:
    except Exception as e:
        print(f"Syntactical (no pun intended) Error: {e}")

# Execute the whole program! When installed with Pip, the main() function is just run when you type "syntactical" in your terminal (it never gets to this)
# Please note: Syntactical only functions properly when installed with Pip, and some features won't work while running it from this file (specifically imports)
if __name__ == "__main__":
    main()
