import numpy as np

def seed_once(func, seed=42):

    def wrapper(*args,seed=seed, **kwargs):
        post=np.random.randint(0,2**32-1)
        np.random.seed(seed)
        result = func(*args, **kwargs)
        np.random.seed(post)
        return result
    return wrapper

def lambify(func):

    def wrapper(*args, **kwargs):
        if len(args) > 0 and (hasattr(args[0], '__iter__') and not isinstance(args[0], str)):
            return func(*args, **kwargs)
        else:
            return lambda x: func(x,*args, **kwargs)
    return wrapper

def adaptribute(obj, attr, els=None):
    if hasattr(obj, attr):
        return getattr(obj, attr)
    elif els is not None:
        return els
    else:
        return obj

def adaptricallable(obj, attr, els=None):
    if hasattr(obj, attr):
        return getattr(obj, attr)
    elif els is not None:
        return els
    else:
        return lambda obj=obj: obj

def nannable(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return np.nan
    return wrapper


