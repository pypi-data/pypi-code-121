# tokens and special symbols for lexer
# based on builtins.token

IDENTIFIER = 1
NUMBER = 2
OPERATOR = 3
STRING = 4
SPACE = 5
TEXT = 6

KEYWORD = 7
BINOP = 8
RELATION = 9
COL_SEP = 10
ROW_SEP = 11
TEXT_SEP = 12
SUBB = 13
SUB = 14
SUPP = 15
SUP = 16
OPEN = 17
CLOSE = 18

OPEN_NEXT = 19
SHUT_NEXT = 20
OPEN_PREV = 21
SHUT_PREV = 22

FUNCTION = 23
MATRIX = 24
BEGIN = 25
END = 26
OVER = 27
CHOOSE = 28
LARGEOP = 29
SERIES = 30
HAT = 31
NORM = 32
SQRT = 33
VARIANT = 34
ENCLOSE = 35
CLASS_ = 36  # note _
NO_NUMBER = 37

SOFT_SPACE = 38
COMMENT = 39
PRESCRIPT = 40

UNDERSET = 41
OVERSET = 43
FRAC = 44
BINOM = 45
ROOT = 46
DISPLAYSTYLE = 47
PAD = 48
SHOE = 49
ENVIRONMENT = 50
WORD = 51

tok_name = {value: name
            for name, value in globals().items()
            if isinstance(value, int) and not name.startswith('_')}
