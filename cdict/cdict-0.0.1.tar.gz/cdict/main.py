import itertools
# import copy

class cdict():
    @classmethod
    def dict(cls, **kwargs):
        return cls(dicts=[dict(**kwargs)])

    def __init__(self, dicts=None, cdicts=None):
        assert dicts is None or cdicts is None
        if dicts is None:
            self._type = "mul"
            for c in cdicts:
                assert isinstance(c, cdict), "Cannot multiply"
            self._cdicts = cdicts
        else:
            self._type = "add"
            self._dicts = dicts

    def dicts(self):
        if self._type == "add":
            for d in self._dicts:
                ks = list(d.keys())
                viters = []
                for k in ks:
                    v = d[k]
                    if isinstance(v, cdict):
                        viters.append(v.dicts())
                    else:
                        viters.append([v])
                for vs in itertools.product(*viters):
                    yield {k: v for k, v in zip(ks, vs)}
        else:
            assert self._type == "mul"
            for ds in itertools.product(*[
                c.dicts() for c in self._cdicts
            ]):
                yield dict(sum((list(d.items()) for d in ds), []))

    def __add__(self, other):
        return cdict(dicts=self._dicts + other._dicts)

    def __mul__(self, other):
        return cdict(cdicts=[self, other])

    def __repr_helper__(self):
        if self._type == "add":
            return " + ".join([str(d) for d in self._dicts])
        else:
            assert self._type == "mul"
            return " * ".join([d.__repr_helper__() for d in self._cdicts])

    def __repr__(self):
        return f"cdict({self.__repr_helper__()})"
