import ply.lex as lex
import sys

reserved = {
    "and": "AND",
    "elif": "ELIF",
    "else": "ELSE",
    "endfor": "ENDFOR",
    "endif": "ENDIF",
    "endrepeat": "ENDREPEAT",
    "for": "FOR",
    "if": "IF",
    "in": "IN",
    "is": "IS",
    "not": "NOT",
    "or": "OR",
    "repeat": "REPEAT",
    "True": "TRUE",
    "False": "FALSE",
}

literals = ("|", ".", "(", ")", "[", "]", ",")

tokens = [
    "id",
    "int",
    "float",
    "str",
    "text",
    "ADD",
    "SUB",
    "MUL",
    "DIV",
    "FDIV",
    "RMD",
    "POW",
    "NE",
    "EQ",
    "GT",
    "GE",
    "LT",
    "LE",
    "ISNOT",
    "NOTIN",
    "PIPE",
    "DOT",
    "OE",  # Open  Expression {{
    "CE",  # Close Expression }}
    "OS",  # Open  Statement  {%
    "CS",  # Close Statement  %}
] + list(reserved.values())

states = (
    ("code", "exclusive"),
    ("raw", "exclusive"),
)

t_code_ADD = "\+"
t_code_SUB = "-"
t_code_MUL = "\*"
t_code_DIV = "/"
t_code_FDIV = "//"
t_code_RMD = "%"
t_code_POW = "\*\*"
t_code_EQ = "=="
t_code_NE = "!="
t_code_GT = ">"
t_code_GE = ">="
t_code_LT = "<"
t_code_LE = "<="
t_code_PIPE = "\|"
t_code_DOT = "\."
t_code_int = r"[+-]?\d(?:_?\d+)*"
t_code_float = r"[+-]?\d(?:_?\d+)*\.\d+(?:e[+-]?\d+)?"


def t_code_ISNOT(t):
    r"is\s+not"
    return t


def t_code_NOTIN(t):
    r"not\s+in"
    return t


# ! maybe integrate into the code and make raw a reserved word
def t_raw(t):
    r"{%\s*raw\s*%}"
    t.lexer.begin("raw")


def t_end_raw(t):
    r"{%\s*endraw\s*%}"
    t.lexer.begin("INITIAL")


# ! lookahead/behind might not be the best way to go as it requeries ignoring quotes
def t_code_str(t):
    r"""
    (
      "(?:\\.|[^"\\])*"     # Double quoted strings
    |
      '(?:\\.|[^'\\])*'     # Single quoted strings
    )
    """
    return t


def t_code_id(t):
    r"[a-zA-Z_]\w*"
    t.type = reserved.get(t.value, "id")  # Check for reserved words
    return t


def t_OE(t):
    r"{{"
    t.lexer.begin("code")
    return t


def t_OS(t):
    r"{%"
    t.lexer.begin("code")
    return t


def t_code_CE(t):
    r"}}"
    t.lexer.begin("INITIAL")
    return t


def t_code_CS(t):
    r"%}"
    t.lexer.begin("INITIAL")
    return t


def t_comment(t):
    r"""
    (?s)    # Make the '.' special character match any character at all, including a newline
    {[#]    # Open Comment
    .+?     # One or more characters, non-greedy
    [#]}    # Close Comment
    """


def t_INITIAL_raw_text(t):
    r"""
    (?s)        # Make the '.' special character match any character at all, including a newline
    .+?         # One or more characters, non-greedy
    (?=         # Positive lookahead assertion
      {{|       # Open Expressions
      {%|       # Open Statements
      {[#]|     # Open Comments
      \Z        # Matches only at the end of the string
    )
    """
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


t_code_ignore = " \t"


def t_ANY_error(t):
    print(f"Illegal character {t.value[0]}")
    t.lexer.skip(1)


lexer = lex.lex()


def main(argv):
    import readline

    while True:
        try:
            s = input("template > ")
        except EOFError:
            break
        if not s:
            continue

        lexer.input(s)  # Give input to lexer
        while True:  # Tokenize
            tok = lexer.token()
            if not tok:
                break  # No more input
            print(tok)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
