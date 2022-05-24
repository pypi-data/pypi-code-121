import itertools, functools
from boltons import iterutils

def Fn(s):
    return eval('(lambda _: ({}))'.format(s.replace('`',"'''")))
def Fn_idx(s):
    return eval('(lambda _,idx: ({}))'.format(s.replace('`',"'''")))
def Fn2(s):
    return eval('(lambda _,__: ({}))'.format(s.replace('`',"'''")))

def try_except_pass(func, exceptions=Exception):
    if isinstance(func, str): func = Fn(func)
    try: return func()
    except exceptions: return None

class KpaIterable:
    def __init__(self, iterable): self._iterable = iterable
    def __iter__(self): return iter(self._iterable)
    def __repr__(self):
        lst = self.take(1001)
        if len(lst) <= 10: return '<KpaIterable len={} values={}>'.format(len(lst), lst)
        elif len(lst) <= 1000: return '<KpaIterable len={} values={}...>'.format(len(lst), lst[:10])
        else: return '<KpaIterable len={}+ values={}...>'.format(1000, lst[:10])

    # map-like
    def map(self, func):
        if isinstance(func, str): func = Fn_idx(func)
        two_arg = try_except_pass(lambda: func.__code__.co_argcount == 2, AttributeError)
        if two_arg: return KpaIterable(func(item,idx) for idx,item in enumerate(self))
        else: return KpaIterable(func(item) for item in self)
    def mmap(self, func):
        if isinstance(func, str): func = Fn_idx(func)
        two_arg = try_except_pass(lambda: func.__code__.co_argcount == 2, AttributeError)
        if two_arg: return KpaIterable(itertools.chain.from_iterable(func(item,idx) for idx,item in enumerate(self)))
        else: return KpaIterable(itertools.chain.from_iterable(func(item) for item in self))
    def filter(self, func):
        if isinstance(func, str): func = Fn_idx(func)
        two_arg = try_except_pass(lambda: func.__code__.co_argcount == 2, AttributeError)
        if two_arg: return KpaIterable(item for idx,item in enumerate(self) if func(item,idx))
        else: return KpaIterable(item for item in self if func(item))

    # to one item
    def reduce(self, func, *initial): func = Fn2(func) if isinstance(func,str) else func; return functools.reduce(func, self, *initial)
    def join(self, s=';'): return s.join(self.map(str))
    def len(self): return sum(1 for _ in self)
    def all(self): return all(self)
    def any(self): return any(self)
    def all_same(self): return iterutils.same(self)

    # to list
    def head(self, n=10): return KpaIterable(item for _,item in zip(range(n), self))
    def skip(self, n): return KpaIterable(item for idx,item in enumerate(self) if idx>=n)
    def tail(self, n=10):
        if n == 0: return KpaIterable([])
        ret = [None]*n
        for idx, item in enumerate(self): ret[idx%n] = item
        return KpaIterable(ret[:idx+1] if idx<n else ret[idx+1:] + ret[:idx+1])
    def list(self): return list(self._iterable) # trivial if isinstance(self._iterable, list)
    def take(self, n=5): return self.head(n).list()

    # fancy
    def uniq(self): return KpaIterable(iterutils.unique_iter(self)) # uses set(), so not quite general
    def sorted(self, key=None): return KpaIterable(sorted(self, key=Fn(key) if isinstance(key,str) else key))
    def chunks(self, size): return KpaIterable(iterutils.chunked_iter(self, size))
    def windows(self, size): return KpaIterable(iterutils.windowed_iter(self, size))
    def flatten(self): return KpaIterable(itertools.chain.from_iterable(KpaIterable(item).flatten() if isinstance(item, (list,tuple)) else [item] for item in self))
    def _accumulate(self):
        for idx,item in enumerate(self):
            if idx == 0: total = item
            else: total += item
            yield total
    def accumulate(self): return KpaIterable(self._accumulate())
    def diffs(self): return self.windows(2).map('_[1] - _[0]') # I wish this included the first item


if __name__ == '__main__':
    # TODO: make these run via pytest
    assert Fn('_ % 30')(10) == 10

    repr(KpaIterable(itertools.count()))

    # map-like
    KpaIterable(itertools.count()).map('_*2').take()
    KpaIterable(itertools.count()).mmap('[9-_]*_').take()
    KpaIterable(itertools.count()).filter('_*2 != 4').take()

    # to one item
    KpaIterable(range(100)).reduce('_ + __')
    KpaIterable(range(100)).reduce('_ + __', -1000)
    KpaIterable(range(100)).map('[str(_)]').reduce('_ + __')
    KpaIterable(range(100)).map('[str(_)]').reduce('_ + __', [7])
    KpaIterable(range(100)).join()
    KpaIterable(range(100)).join(' ')
    KpaIterable(range(100)).len()
    KpaIterable(range(100)).all()
    KpaIterable(itertools.count()).any()
    KpaIterable(range(100)).map('[_,str(_),{(_):{_}}]').all_same()

    # to list
    KpaIterable(itertools.count()).head(0)
    KpaIterable(itertools.count()).head(1)
    KpaIterable(range(100)).head(1000)
    KpaIterable(range(100)).tail(0)
    KpaIterable(range(100)).tail(1)
    KpaIterable(range(100)).tail(1000)
    KpaIterable(itertools.count()).skip(1000).take()
    assert KpaIterable(range(100)).skip(0).list() == KpaIterable(range(100)).list()
    assert KpaIterable(range(100)).skip(10).list() == KpaIterable(range(100)).list()[10:]
    assert KpaIterable(range(100)).skip(1000).list() == []

    # fancy
    KpaIterable(itertools.count()).uniq().take()
    KpaIterable(itertools.count()).head().sorted()
    KpaIterable(itertools.count()).chunks(2).take()
    KpaIterable(itertools.count()).windows(2).take()
    KpaIterable(itertools.count()).chunks(2).flatten().take()
    KpaIterable(itertools.count()).accumulate().take()
    KpaIterable(itertools.count()).diffs().take()

    # etc
    KpaIterable(itertools.count()).map('_*2').mmap('[str(9-_)]*_').windows(2).take()
    KpaIterable(itertools.count()).map('_*2').mmap('[str(9-_)]*_').windows(2).flatten().head().sorted().uniq().map(type).tail().join()
    KpaIterable(itertools.count()).map('_*2').mmap('[str(9-_)]*_').windows(2).flatten().head().sorted().map(int).reduce('_ + __')
