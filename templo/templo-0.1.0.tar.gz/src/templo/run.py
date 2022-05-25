import builtins
import io
import operator
import sys
import typing as t
import yaml
from yaml import Loader
from templo.parser import parser


def template(tmpl, dic=None):
    if isinstance(tmpl, io.TextIOBase):
        tp = tmpl
        tmpl = tmpl.read()
        tp.seek(0)
    elif type(tmpl) is not str:
        print("Bad first argument!")
        return None

    ast = parser.parse(tmpl)

    if dic is None:
        def _render(d=None):
            if type(d) is str:
                d = yaml.load(d, Loader=Loader)
            elif isinstance(d, io.TextIOBase):
                dp = d
                d = yaml.load(d.read(), Loader=Loader)
                dp.seek(0)
            elif type(d) is not dict and d is not None:
                print("Bad first argument!")
                return None
            return run(ast, d)
        return _render
    else:
        if type(dic) is str:
            dic = yaml.load(dic, Loader=Loader)
        elif isinstance(dic, io.TextIOBase):
            dic = yaml.load(dic.read(), Loader=Loader)
        elif type(dic) is not dict:
            print("Bad second argument!")
            return None
        return run(ast, dic)


def run(ast, dic):
    out = ""
    for x in ast:
        match x[0]:
            case "text":
                out += x[1]
            case "print":
                out += str(run([x[1]], dic))
            case "if":
                for cond, elems in x[1]:
                    if run([cond], dic):
                        out += run(elems, dic)
                        break
            case "for":
                for a in dic[x[2]]:
                    dic[x[1]] = a
                    out += run(x[3], dic)
            case "fordict":
                for a, b in dic[x[3]].items():
                    dic[x[1]] = a
                    dic[x[2]] = b
                    out += run(x[4], dic)
            case "repeat":
                for _ in range(run([x[1]], dic)):
                    out += run(x[2], dic)
            case "variable":
                try:
                    out = dic.get(x[1], None)
                except AttributeError:
                    out = None
            case "int":
                out = int(x[1])
            case "float":
                out = float(x[1])
            case "bool":
                out = x[1] == "True"
            case "list":
                out = list(map(lambda y: run([y], dic), x[1]))
            case "tuple":
                out = tuple(map(lambda y: run([y], dic), x[1]))
            case "+" | "-" | "*" | "/" | "//" | "%" | "**" | "==" | "!=" | ">" | ">=" | "<" | "<=" | "in" | "notin" | "and" | "or":
                out = OPERATORS[x[0]](run([x[1]], dic), run([x[2]], dic))
            case "uplus":
                out = +run([x[1]], dic)
            case "uminus":
                out = -run([x[1]], dic)
            case "is":
                out = TESTS[x[2]](run([x[1]], dic))
            case "isnot":
                out = not TESTS[x[2]](run([x[1]], dic))
            case "not":
                out = not run([x[1]], dic)
            case "filter":
                out = getattr(builtins, x[2])(run([x[1]], dic))
            case "item":
                out = run([x[1]], dic).__getitem__(run([x[2]], dic))
            case "attr":
                out = getattr(run([x[1]], dic), x[2])
            case "method":
                args = tuple(map(lambda y: run([y], dic), x[3]))
                out = getattr(run([x[1]], dic), x[2])(*args)
            case _:
                pass
    return out


OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "//": operator.floordiv,
    "%": lambda x, y: x % y,
    "**": lambda x, y: x**y,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "in": lambda x, y: operator.contains(y, x),
    "notin": lambda x, y: not operator.contains(y, x),
    "and": lambda x, y: x and y,
    "or": lambda x, y: x or y,
}


TESTS = {
    "odd": lambda value: value % 2 == 1,
    "even": lambda value: value % 2 == 0,
    "none": lambda value: value is None,
    "boolean": lambda value: value is True or value is False,
    "false": lambda value: value is False,
    "true": lambda value: value is True,
    "integer": lambda value: isinstance(value, int) and value is not True and value is not False,
    "float": lambda value: isinstance(value, float),
    "lower": lambda value: str(value).islower(),
    "upper": lambda value: str(value).isupper(),
    "string": lambda value: isinstance(value, str),
}


def main(argv):
    import readline

    while True:
        try:
            s = input("template > ")
        except EOFError:
            break
        if not s:
            continue
        result = parser.parse(s)
        if parser.success:
            print("ast:", result)
            print(run(result, None))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
