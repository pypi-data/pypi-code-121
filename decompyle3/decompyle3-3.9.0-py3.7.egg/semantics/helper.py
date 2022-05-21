import sys

from xdis import iscode
from decompyle3.parsers.treenode import SyntaxTree

minint = -sys.maxsize - 1
maxint = sys.maxsize

read_write_global_ops = frozenset(("STORE_GLOBAL", "DELETE_GLOBAL", "LOAD_GLOBAL"))
read_global_ops = frozenset(("STORE_GLOBAL", "DELETE_GLOBAL"))

# NOTE: we also need to check that the variable name is a free variable, not a cell variable.
nonglobal_ops = frozenset(("STORE_DEREF", "DELETE_DEREF"))


def escape_string(s: str, quotes=('"', "'", '"""', "'''")):
    quote = None
    for q in quotes:
        if s.find(q) == -1:
            quote = q
            break
        pass
    if quote is None:
        quote = '"""'
        s = s.replace('"""', '\\"""')

    for (orig, replace) in (("\t", "\\t"), ("\n", "\\n"), ("\r", "\\r")):
        s = s.replace(orig, replace)
    return "%s%s%s" % (quote, s, quote)


# FIXME: this and find_globals could be paramaterized with one of the
# above global ops
def find_all_globals(node, globs):
    """Search Syntax Tree node to find variable names that are global."""
    for n in node:
        if isinstance(n, SyntaxTree):
            globs = find_all_globals(n, globs)
        elif n.kind in read_write_global_ops:
            globs.add(n.pattr)
    return globs


def find_code_node(node, start: int):
    for i in range(-start, len(node) + 1):
        if node[-i].kind == "LOAD_CODE":
            code_node = node[-i]
            assert iscode(code_node.attr)
            return code_node
        pass
    assert False, "did not find code node starting at %d in %s" % (start, node)


def find_globals_and_nonlocals(node, globs, nonlocals, code, version):
    """search a node of parse tree to find variable names that need a
    either 'global' or 'nonlocal' statements added."""
    for n in node:
        if isinstance(n, SyntaxTree):
            globs, nonlocals = find_globals_and_nonlocals(
                n, globs, nonlocals, code, version
            )
        elif n.kind in read_global_ops:
            globs.add(n.pattr)
        elif (
            version >= (3, 0)
            and n.kind in nonglobal_ops
            and n.pattr in code.co_freevars
            and n.pattr != code.co_name
            and code.co_name != "<lambda>"
        ):
            nonlocals.add(n.pattr)
    return globs, nonlocals


# def find_globals(node, globs, global_ops=mkfunc_globals):
#     """Find globals in this statement."""
#     for n in node:
#         # print("XXX", n.kind, global_ops)
#         if isinstance(n, SyntaxTree):
#             # FIXME: do I need a caser for n.kind="mkfunc"?
#             if n.kind in ("if_exp_lambda", "return_expr_lambda"):
#                 globs = find_globals(n, globs, lambda_body_globals)
#             else:
#                 globs = find_globals(n, globs, global_ops)
#         elif n.kind in frozenset(global_ops):
#             globs.add(n.pattr)
#     return globs


def find_none(node):
    for n in node:
        if isinstance(n, SyntaxTree):
            if n not in ("return_stmt", "return_if_stmt"):
                if find_none(n):
                    return True
        elif n.kind == "LOAD_CONST" and n.pattr is None:
            return True
    return False


def flatten_list(node):
    """
    List of expressions may be nested in groups of 32 and 1024
    items. flatten that out and return the list
    """
    flat_elems = []
    for elem in node:
        if elem == "expr1024":
            for subelem in elem:
                assert subelem == "expr32"
                for subsubelem in subelem:
                    flat_elems.append(subsubelem)
        elif elem == "expr32":
            for subelem in elem:
                assert subelem == "expr"
                flat_elems.append(subelem)
        else:
            flat_elems.append(elem)
            pass
        pass
    return flat_elems


def is_lambda_mode(compile_mode: str) -> bool:
    return compile_mode in ("dictcomp", "genexpr", "lambda", "listcomp", "setcomp")


def strip_quotes(s: str) -> str:
    if s.startswith("'''") and s.endswith("'''"):
        s = s[3:-3]
    elif s.startswith('"""') and s.endswith('"""'):
        s = s[3:-3]
    elif s.startswith("'") and s.endswith("'"):
        s = s[1:-1]
    elif s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
        pass
    return s


def print_docstring(self, indent, docstring):
    quote = '"""'
    if docstring.find(quote) >= 0:
        if docstring.find("'''") == -1:
            quote = "'''"

    self.write(indent)
    docstring = repr(docstring.expandtabs())[1:-1]

    for (orig, replace) in (
        ("\\\\", "\t"),
        ("\\r\\n", "\n"),
        ("\\n", "\n"),
        ("\\r", "\n"),
        ('\\"', '"'),
        ("\\'", "'"),
    ):
        docstring = docstring.replace(orig, replace)

    # Do a raw string if there are backslashes but no other escaped characters:
    # also check some edge cases
    if (
        "\t" in docstring
        and "\\" not in docstring
        and len(docstring) >= 2
        and docstring[-1] != "\t"
        and (docstring[-1] != '"' or docstring[-2] == "\t")
    ):
        self.write("r")  # raw string
        # Restore backslashes unescaped since raw
        docstring = docstring.replace("\t", "\\")
    else:
        # Escape the last character if it is the same as the
        # triple quote character.
        quote1 = quote[-1]
        if len(docstring) and docstring[-1] == quote1:
            docstring = docstring[:-1] + "\\" + quote1

        # Escape triple quote when needed
        if quote == '"""':
            replace_str = '\\"""'
        else:
            assert quote == "'''"
            replace_str = "\\'''"

        docstring = docstring.replace(quote, replace_str)
        docstring = docstring.replace("\t", "\\\\")

    lines = docstring.split("\n")

    self.write(quote)
    if len(lines) == 0:
        self.println(quote)
    elif len(lines) == 1:
        self.println(lines[0], quote)
    else:
        self.println(lines[0])
        for line in lines[1:-1]:
            if line:
                self.println(line)
            else:
                self.println("\n\n")
                pass
            pass
        self.println(lines[-1], quote)
    return True


# if __name__ == '__main__':
#     from io import StringIO
#     class PrintFake():
#         def __init__(self):
#             self.pending_newlines = 0
#             self.f = StringIO()

#         def write(self, *data):
#             if (len(data) == 0) or (len(data) == 1 and data[0] == ''):
#                 return
#             out = ''.join((str(j) for j in data))
#             n = 0
#             for i in out:
#                 if i == '\n':
#                     n += 1
#                     if n == len(out):
#                         self.pending_newlines = max(self.pending_newlines, n)
#                         return
#                 elif n:
#                     self.pending_newlines = max(self.pending_newlines, n)
#                     out = out[n:]
#                     break
#                 else:
#                     break

#             if self.pending_newlines > 0:
#                 self.f.write('\n'*self.pending_newlines)
#                 self.pending_newlines = 0

#             for i in out[::-1]:
#                 if i == '\n':
#                     self.pending_newlines += 1
#                 else:
#                     break

#             if self.pending_newlines:
#                 out = out[:-self.pending_newlines]
#             self.f.write(out)
#         def println(self, *data):
#             if data and not(len(data) == 1 and data[0] ==''):
#                 self.write(*data)
#             self.pending_newlines = max(self.pending_newlines, 1)
#             return
#         pass

#     for doc in (
#             "Now is the time",
#             r'''func placeholder - with ("""\nstring\n""")''',
#             r'''func placeholder - ' and with ("""\nstring\n""")''',
#             r"""func placeholder - ' and with ('''\nstring\n''') and \"\"\"\nstring\n\"\"\" """
#             ):
#         o = PrintFake()
#         print_docstring(o, '  ', doc)
#         print(o.f.getvalue())
