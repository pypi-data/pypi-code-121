

class GXFColmuns:
    _colmuns = [
        'chr_id',
        'source',
        'type',
        'start',
        'end',
        'score',
        'strand',
        'phase',
        'attributes'
    ]

    def __init__(self):
        for col in self._colmuns:
            self.__dict__[col] = col

    def __len__(self):
        return len(self._colmuns)

    def __iter__(self):
        return iter(self._colmuns)

    @property
    def columns(self):
        return self._colmuns
