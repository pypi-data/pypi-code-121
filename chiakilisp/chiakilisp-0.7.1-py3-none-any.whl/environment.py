# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring

from functools import reduce
import hashedcolls  # <---- to use hashed dict and hashed list
from chiakilisp.utils import pprint  # our lovely custom print

ENVIRONMENT = {
    '+': lambda *args: reduce(lambda acc, cur: acc+cur,  args),
    '*': lambda *args: reduce(lambda acc, cur: acc*cur,  args),
    '/': lambda *args: reduce(lambda acc, cur: acc/cur,  args),
    '-': lambda *args: reduce(lambda acc, cur: acc-cur,  args),
    'mod': lambda *args: reduce(lambda ac, cr: ac % cr,  args),
    'listy': lambda *args: list(args),    # <-------- list cast
    'dicty': lambda *args: {args[idx]: args[idx+1]  # dict cast
                            for idx in range(0, len(args), 2)},
    'hashed-dict': hashedcolls.HashedDict,  # <---- embed later
    'hashed-list': hashedcolls.HashedList,  # <---- embed later
    'prn': pprint,
    'print': pprint,
    'println': pprint,  # we need more aliases for _print!  \O/
    'apply': lambda fn, args: fn(*args),  # built-in apply func
    '...': Ellipsis  # make it possible to write '...' for user
}
