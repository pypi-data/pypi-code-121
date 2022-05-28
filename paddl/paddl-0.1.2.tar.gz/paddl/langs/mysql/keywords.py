# https://pyparsing-docs.readthedocs.io/en/latest/HowToUsePyparsing.html#hello-world
from pyparsing import Keyword, OneOrMore, Optional, Group, CaselessKeyword

CREATE = CaselessKeyword('CREATE')
TEMPORARY = Optional(CaselessKeyword('TEMPORARY')('temporary'))
TABLE = CaselessKeyword('TABLE')
IF_NOT_EXISTS = Optional(CaselessKeyword('IF NOT EXISTS')('if_not_exists'))


# extract to util
def wrap(word, many=False):
    if many:
        word = OneOrMore(word)
    return word


_ = wrap
