from typing import Final

# fmt: off
SYMBOLS: Final[dict[str, str]] = {
    "=":  "EQUALS",
    ">":  "GREATER",
    "<":  "LESS",
    "+":  "PLUS",
    "-":  "MINUS",
    "*":  "STAR",
    "/":  "SLASH",
    "!":  "BANG",
    "^":  "XOR",
    ",":  "COMMA",
    ".":  "DOT",
    "(":  "LPAREN",
    ")":  "RPAREN",
    "{":  "LBRACE",
    "}":  "RBRACE",
    "[":  "LBRACKET",
    "]":  "RBRACKET",
    ":":  "COLON",
    "==": "EQUALS_EQUALS",
    "!=": "NOT_EQUALS",
    ">=": "GREATER_EQUALS",
    "<=": "LESS_EQUALS",
    "&&": "AND",
    "||": "OR",
    "++": "PLUS_PLUS",
    "--": "MINUS_MINUS",
    "//": "SLASH_SLASH",
    "**": "STAR_STAR",
    "->": "ARROW",
    ">>": "GREATER_GREATER",
    "<<": "LESS_LESS",
}
# fmt: on

SYMBOL_CHARS: Final[set[str]] = set("".join(SYMBOLS))
