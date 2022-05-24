import json
from functools import wraps
from itertools import dropwhile

from bs4.element import Tag


def prettify_content(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        content = func(*args, **kwargs)

        if isinstance(content, Tag):
            content = content.get_text()

        if not content:
            return content

        trantab = {
            '<br>': '',
            '</br>': '\n',
            '<p>':'',
            '</p>': '\n',
            '\t': '',
            '\u200b': '',
            '\xa0': '',
            
        }
        for tok, repl in trantab.items():
            content = content.replace(tok, repl)
        
        lines = []
        for line in content.split('\n'):
            if line := line.strip():
                lines.append(line)

        return '\n'.join(lines)
    return wrapper



def extract_json(content, many=True):
    # vars,
    OPENING_BRAKET, CLOSING_BRAKET, OPENING_BRACE, CLOSING_BRACE = 'OPENING_BRAKET', 'CLOSING_BRAKET', 'OPENING_BRACE', 'CLOSING_BRACE',
    OPENING, CLOSING = 'OPENING', 'CLOSING',
    BRAKET, BRACE = 'BRAKET', 'BRACE',
    objmap = {
        '[': OPENING_BRAKET, b'[': OPENING_BRAKET,
        ']': CLOSING_BRAKET, b']': CLOSING_BRAKET,
        '{': OPENING_BRACE, b'{': OPENING_BRACE,
        '}': CLOSING_BRACE, b'}': CLOSING_BRACE,
    }

    balancer = {
        BRAKET: 0, BRACE:0
    }

    ## cut off head, tail impure
    content = ''.join(dropwhile(lambda c: objmap.get(c) not in [OPENING_BRAKET, OPENING_BRACE], content))
    content = ''.join(reversed(list(dropwhile(lambda c: objmap.get(c) not in [CLOSING_BRAKET, CLOSING_BRACE], reversed(content)))))


    _records = []
    for i, c in enumerate(content):
        if not(token := objmap.get(c)):
            continue

        option, kind = token.split('_') # ex) OPENING, BRACE

        if option == OPENING:
            balancer[kind] += 1
        else:
            balancer[kind] -= 1
        
        record = dict(
            index=i, kind=kind, option=option, balance=balancer[kind]
        )
        _records.append(record)
    
    if len(_records) < 2:
        return []

    starts = None
    tokens = []
    for r in _records:
        if starts is None:
            starts = r
            continue
        if starts['kind'] == r['kind'] and r['option'] == CLOSING and r['balance'] == 0:
            tok = content[starts['index']: r['index']+1]
            tokens.append(tok)
            starts = None

    success = []
    for tok in tokens:
        try:
            obj = json.loads(tok)
        except json.decoder.JSONDecodeError:
            continue
        success.append(obj)
    if many:
        return success
    else:
        if success:
            return success[0]
        

  