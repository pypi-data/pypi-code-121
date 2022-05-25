"""Lexer"""

# Copyright (C) 2009-2020 the sqlparse authors and contributors
# This code is based on the Lexer in sqlparse with modification.
# https://github.com/andialbrecht/sqlparse

from tokyo_lineage.utils.parser import utils
from tokyo_lineage.utils.parser import tokens
from tokyo_lineage.utils.parser.dictionary import SQL_REGEX

def tokenize(sql):
    """Tokenize sql.

    Return 2-tuple stream of ``(token type, value)`` items
    """
    sql = utils.to_string(sql)

    iterable = enumerate(sql)
    for pos, char in iterable:
        for re_match, action in SQL_REGEX:
            m = re_match(sql, pos)

            if not m:
                continue
            elif isinstance(action, tokens._TokenType):
                yield action, m.group()
            elif callable(action):
                yield action(m.group())
            
            utils.advance(iterable, m.end() - pos - 1)
            break
        else:
            yield tokens.Error, char