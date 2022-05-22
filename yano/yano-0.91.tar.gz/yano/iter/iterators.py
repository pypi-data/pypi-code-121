from .handler import adaptive
from ..helper import lambify

def dxy(iterable):
    """instead of yielding datasets, this iterator yields dataset, x, y"""
    return adaptive(iterable,"dxy")

def nonconst(iterable):
    """instead of yielding datasets, this iterator yields datasets without constant features"""
    return adaptive(iterable,"nonconst")

@lambify
def split(iterable,*args,**kwargs):
    """handles train test split for each input. Thus returns d, train, test_x, test_y"""
    return adaptive(iterable,"split",*args,**kwargs)

@lambify
def shuffle(iterable,seed=None):
    """shuffles whatever you put into it."""
    if seed is not None:
        return adaptive(iterable,"shuffle",seed=seed)
    else:
        return adaptive(iterable,"shuffle")

@lambify
def crossval(iterable, *args, **kwargs):
    """handles cross validation for each input. Thus returns d, train, test_x, test_y, but each n_folds times"""
    return adaptive(iterable,"crossval",*args,**kwargs)

def pipeline(iterable, *tasks):
    """pipeline is a way to chain multiple iterables together."""
    q=iterable
    for task in tasks:
        q=task(q)
    return q

@lambify
def normalize(iterable,method="zscore"):
    """normalizes the dataset"""
    return adaptive(iterable,"normalize_"+method)

def zscore(iterable):
    """normalizes the dataset so that the mean is 0 and the standard deviation is 1"""
    return normalize(iterable,"zscore")
normalize_zscore=zscore

def minmax(iterable):
    """normalizes the dataset so that max is 1 and min is 0"""
    return normalize(iterable,"minmax")
normalize_minmax=minmax

def listfold(iterable):
    return adaptive(iterable,"listfold")

def asfloat(iterable):
    return adaptive(iterable,"asfloat")

def asint(iterable):
    return adaptive(iterable,"asint")

@lambify
def cut(iterable, maxima=10):
    return adaptive(iterable,"cut",maxima=maxima)




