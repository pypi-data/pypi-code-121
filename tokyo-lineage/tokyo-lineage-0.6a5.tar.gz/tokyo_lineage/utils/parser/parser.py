# -*- coding: utf-8 -*-

import copy

from tokyo_lineage.utils.parser import lexer
from tokyo_lineage.utils.parser import tokens as T
from tokyo_lineage.utils.parser.utils import to_string

class Token:
    """Class to represent a single token with token type and value.

    It has two instance attributes: ``value`` is the optional unchanged value
    of the token and ``ttype`` is the token type based on :class:`~osaka.tokens`.
    """
    def __init__(self, ttype, value=None):
        self.ttype = ttype
        self.__value = value
        self.is_keyword = ttype in T.Keyword
        self.is_whitespace = ttype in T.Whitespace
        self.normalized = value.upper() if self.is_keyword and value is not None else value

    def __repr__(self):
        cls = str(self.ttype).split('.')[-1]
        value = self.value

        return "<{cls} {value}>".format(
            cls=cls, value=value
        )

    @property
    def value(self):
        return self.__value

class TokenList:
    """Represent group of ``Token`` instances"""

    def __init__(self, tokens=None):
        self.tokens = tokens if tokens else []
        self.idx = -1

    def append(self, token):
        """Add instance of :class:`~osaka.parser.Token` to token list"""
        self.tokens.append(token)
    
    def contains(self, ttype, value):
        """Return if a token with certain type and value is inside this TokenList"""
        for token in self.tokens:
            ctype = token.ttype
            cval = token.value

            if ctype in ttype \
                and (cval == value \
                or token.normalized == value):
                return token
        
        return False
    
    def at(self, idx):
        return self.tokens[idx]

    def stream(self):
        for idx in range(self.idx + 1, len(self.tokens), 1):
            self.idx = idx
            yield idx, self.tokens[idx]
    
    def advance(self, n=None, idx=None):
        if n is not None:
            self.idx += n
        elif idx is not None:
            self.idx = idx
        
        return self.idx
    
    def get_next(self, skip_ws=True):
        incr = 1

        if skip_ws:
            while self.tokens[self.idx + incr].ttype in T.Whitespace:
                incr += 1

        return self.tokens[self.idx + incr]
    
    def get_prev(self, skip_ws=True):
        decr = -1

        if skip_ws:
            while self.tokens[self.idx + decr].ttype in T.Whitespace:
                decr -= 1

        return self.tokens[self.idx + decr] if self.idx > 0 else None
    
    def index(self, token):
        """Return the index of token in token list"""
        return self.tokens.index(token)

    def reset(self):
        self.idx = -1
    
    def _token_get_all_matching(self, start=0, ttype=None, value=None, end=None):
        tokens = []
        value = value if not isinstance(value, str) else (value,)

        for idx, token in enumerate(self.tokens[start:end]):
            if value is None:
                if token.ttype in ttype:
                    tokens.append((start+idx, token))
            else:
                if (token.ttype in ttype and
                    (token.value in value or
                    token.normalized in value)):
                    tokens.append((start+idx, token))
        
        return tokens

    def _token_get_until(self, start=0, terminators=None, skip_ws=True):
        start = start + 1
        tokens = []

        def _is_equal(token, terminator):
            if terminator.value is None:
                if token.ttype in terminator.ttype:
                    return True
            else:
                if (token.ttype in terminator.ttype and
                    (token.value == terminator.value or 
                        token.normalized == terminator.value)):
                        return True
            
            return False
        
        for idx, token in enumerate(self.tokens[start:]):
            f_break = False

            for terminator in terminators:
                if _is_equal(token, terminator):
                    f_break = True
            
            if f_break:
                break

            if skip_ws and token.is_whitespace:
                continue

            tokens.append((start+idx, token))
        
        return tokens

    @classmethod
    def from_iterable(cls, tokens):
        """Create new TokenList populated with tokens from iterable"""
        tl = cls()

        for token in tokens:
            ttype, value = token
            tl.append(Token(ttype, value))
        
        return tl

class Parser:
    """Parse sql string"""
    def __init__(self, sql):
        self.__tokenized = TokenList.from_iterable(lexer.tokenize(sql))
    
    def get_tables(self):
        tables = self._get_tables()
        cte = self._get_cte()

        def _get_name_only(from_item):
            names = []
            for item in from_item:
                idx, token = item
                name = token.value
                names.append(name)
            
            return names
        
        def _clean_table(from_item):
            if len(from_item) == 0:
                return None
            
            if len(from_item) == 1:
                if from_item[0][1].ttype == T.Punctuation:
                    return None
            
            return _get_name_only(from_item)
        
        clean_tables = []
        for table in tables:
            ct = _clean_table(table)
            if ct is not None:
                clean_tables.append(ct)
        
        tables = [self._resolve_table_dot(t) for t in clean_tables]

        clean_cte = []
        for table in cte:
            ct = _clean_table(table)
            if ct is not None:
                clean_cte.append(ct)
        
        cte = [self._resolve_table_dot(t) for t in clean_cte]

        return {
            'tables': tables,
            'cte': cte
        }

    def _resolve_table_dot(self, arr):
        resolved = []
        stack = Stack()
        pos = 0
        for i, v in enumerate(arr):
            if len(arr) == 1:
                resolved = [v]

            if pos == 0:
                stack.push(v)
            else:
                if v == '.':
                    stack.push(v)
                elif len(stack) > 0:
                    if stack.peek() == '.':
                        prev = stack.drain()
                        new_v = ''.join(prev + [v])
                        resolved.append(new_v)
                    else:
                        resolved += stack.drain()
                        resolved.append(v)
                else:
                    resolved.append(v)
            
            pos += 1
        
        return resolved

    def _get_cte(self):
        """Returns list of defined CTE"""
        tokens = self.__tokenized
        tokens.reset()

        # CTE is valid only on top level
        m_start = T.Keyword, 'WITH'

        mtype, mval = m_start
        starter_token = tokens._token_get_all_matching(ttype=mtype, value=mval)

        try:
            assert len(starter_token) > 0
        except AssertionError:
            return []
        
        starter_token = starter_token[0]

        e_type, e_val = T.Punctuation, ')'
        # CTE is terminated by closing parenthesis followed by
        # <Keyword SELECT>
        # Technically, CTE can be terminated by any other keyword
        # such as INSERT, UPDATE, and DELETE.
        nt_type, nt_val = T.Keyword, ('SELECT', 'INSERT',
                                        'UPDATE', 'DELETE')

        end = None

        tokens.advance(idx=starter_token[0])
        for pos, token in tokens.stream():
            if token.ttype in e_type \
                and token.value == e_val:
                nt = tokens.get_next()

                if nt.ttype in nt_type \
                    and (nt.value in nt_val
                            or nt.normalized in nt_val):
                            end = pos, token
                            break
        
        tokens.reset()

        # from start - end
        # get all `with query` definition
        # `with query` is started with with_query_name
        # followed by <Keyword AS>, then <Punctuation '('>
        # and then <Keyword {kw}> {kw} is (select | values | insert | update | delete)
        wq_start = T.Keyword, 'AS'
        # Possible for `with_query` to have column alias
        # https://www.postgresql.org/docs/9.5/sql-select.html
        wq_p1 = T.Punctuation, ')'
        wq_n1 = T.Punctuation, '('
        wq_n2 = T.Keyword, ('SELECT', 'VALUES','INSERT',
                            'UPDATE', 'DELETE')

        mtype, mval = wq_start
        wq_starter = tokens._token_get_all_matching(
                        start=starter_token[0],
                        ttype=mtype, value=mval,
                        end=end[0])

        def _get_with_query_name(pos, tokens, wq_n1, wq_n2):
            """Sub function to get ``with_query_name``

            Written based on PostgreSQL SELECT statement grammar.\n
            https://www.postgresql.org/docs/9.5/sql-select.html

            Parameters:
                    pos (int): the position where <Keyword 'AS'> is found
                    tokens (TokenList): list of tokens
                    wq_n1 (tuple): syntax rule for next token of 'AS'
                    wq_n2 (tuple): syntax rule for next-next token of 'AS'

            Returns:
                    wqn (str): the ``with_query_name`` of CTE definition
            """
            tokens.advance(idx=pos)
            pv_token = tokens.get_prev()
            assert pv_token.ttype in T.Name

            n1 = tokens.get_next()
            assert n1.ttype in wq_n1[0] and (n1.value in wq_n1[1]
                                                or n1.normalized in wq_n1[1])

            tokens.advance(idx=tokens.index(n1))

            n2 = tokens.get_next()
            assert n2.ttype in wq_n2[0] and (n2.value in wq_n2[1]
                                                or n2.normalized in wq_n2[1])

            tokens.reset()

            return pv_token
        
        cte = []
        for pos, token in wq_starter:
            try:
                wqn = _get_with_query_name(pos, tokens, wq_n1, wq_n2)
            except AssertionError:
                continue
            cte.append([(pos, wqn)])

        return cte

    def _get_tables(self):
        """Returns list of table referenced"""
        tokens = self.__tokenized
        tokens.reset()

        m_start = [(T.Keyword, 'FROM'),
                    (T.Keyword, 'JOIN'),
                    (T.Keyword, 'INNER JOIN'),
                    (T.Keyword, 'LEFT JOIN'),
                    (T.Keyword, 'LEFT OUTER JOIN'),
                    (T.Keyword, 'RIGHT JOIN'),
                    (T.Keyword, 'RIGHT OUTER JOIN'),
                    (T.Keyword, 'FULL JOIN'),
                    (T.Keyword, 'FULL OUTER JOIN'),
                    (T.Keyword, 'UNION'),
                    (T.Keyword, 'UNION ALL')]
        
        # Any keyword will terminate table reference/definition
        # m_end = [(T.Keyword, None)]
        m_end = [
            Token(T.Keyword, None),
            Token(T.Punctuation, '('),
            Token(T.Punctuation, ')'),
            Token(T.Punctuation, ',')
        ]

        starter_token = []
        for match in m_start:
            mtype, mval = match
            st = tokens._token_get_all_matching(ttype=mtype, value=mval)
            starter_token += st
        
        def _get_tables_from(pos, tokens, m_end):
            tables = []
            table = tokens. \
                _token_get_until(
                        start=pos,
                        terminators=m_end)
            tables += table
            
            return tables

        tables = []
        for pos, token in starter_token:
            tables += [_get_tables_from(pos, tokens, m_end)]

        return tables

    @property
    def tokens(self):
        return self.__tokenized

def parse(sql):
    sql = to_string(sql)
    return Parser(sql)

class Stack:
    def __init__(self, stack=None):
        self.__stack = []
    
    def __len__(self):
        return len(self.__stack)

    def push(self, item):
        self.__stack.append(item)
    
    def peek(self):
        return self.__stack[-1]
    
    def pop(self):
        it = self.__stack[-1]
        self.__stack = self.__stack[:-1]
        return it
    
    def drain(self):
        it = self.__stack
        self.__stack = []
        return it