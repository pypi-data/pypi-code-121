"""
primitive manipulation
"""

import re
from typing import List, Any

__all__ = ['nan', 'is_float', 'clean_whitespace', 'get_substr_indices']


nan = float('nan')


def is_float(x: Any, no_int=False, no_sci=False) -> bool:
    try:
        is_sci = isinstance(x, str) and 'e' in x.lower()
        f = float(x)
        is_int = f.is_integer()
        out = True
        if no_int:
            out = out and (not is_int)
        if no_sci:
            out = out and (not is_sci)
        return out
    except (ValueError, TypeError):
        return False


def clean_whitespace(s: str):
    if not hasattr(clean_whitespace, 'pattern_space'):
        clean_whitespace.pattern_space = re.compile(r'\s+')
    return clean_whitespace.pattern_space.sub(' ', s).strip()


def get_substr_indices(s: str, s_sub: str) -> List[int]:
    s_sub = re.escape(s_sub)
    return [m.start() for m in re.finditer(s_sub, s)]
