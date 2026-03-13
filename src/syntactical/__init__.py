from lark import Lark
from syntactical import syntactical

# This is for importing for use in compiling Syntactical with your own Python (or Syntactical!) program
def toPython(source):
    l_parser = Lark(syntactical.grammar, parser='lalr')
    python_code = syntactical.ToPython().transform(l_parser.parse(source))
    return python_code

# This is for importing for use in running Syntactical with your own Python (or Syntactical!) program
def run(source):
    l_parser = Lark(syntactical.grammar, parser='lalr')
    python_code = syntactical.ToPython().transform(l_parser.parse(source))
    exec(python_code, {"__name__": "__main__"})