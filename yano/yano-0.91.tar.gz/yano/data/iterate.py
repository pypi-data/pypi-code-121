
from .loaddata import allfiles, fileinfo
from .dataset import dataset


def _iterate_all():
    for f in allfiles():
        yield f

def _iterate_condition(condition):
    if callable(condition):
        for f in _iterate_all():
            if condition(fileinfo(f)):
                yield f
    elif type(condition) is dict:
        for f in _iterate_all():
            if not f in condition:continue
            if condition[f]:
                yield f
    elif hasattr(condition, '__iter__'):
        for f in _iterate_all():
            if f in condition:
                yield f
    else:
        try:
            b=bool(condition)
        except:
            raise ValueError('if condition is not defined by metalogic, it must be callable, dict or iterable')
        if b:
            for f in _iterate_all():
                yield f



def _iterate(condition=None):
    if condition is None:
        return _iterate_all()
    else:
        return _iterate_condition(condition)

def iterate(condition=None):
    for f in _iterate(condition):
        yield dataset(f)

def load_dataset(nam):
    #condition=symbols.name==nam
    for d in iterate():
        if d.name()==nam:
            return d
    return None

if __name__=="__main__":
    for f in iterate():
        print(f)




