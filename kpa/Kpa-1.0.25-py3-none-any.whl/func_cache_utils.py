from typing import Any, cast, Callable, TypeVar, Iterator
import shelve, json, os.path


def _jsonify(obj: Any) -> str:
    return json.dumps(obj, default=_jsonify_default)
def _jsonify_default(obj: Any) -> Any:
    try:
        import pandas as pd
    except ImportError:
        pass
    else:
        if isinstance(obj, pd.DataFrame):
            return {'type=pandas.DataFrame': obj.to_json()}
    raise TypeError('Object of type {obj.__class__.__name__} is not JSON serializable!'.format(**locals()))


F = TypeVar('F', bound=Callable[..., Any])

def shelve_cache(func:F) -> F:
    filename = '.cache-{func.__name__}.shelve'.format(**locals())
    def wrapper(*args, **kwargs):
        key = _jsonify([args, kwargs])
        # with shelve.open(filename) as shelf:
        #     if key not in shelf: shelf[key] = func(*args, **kwargs)
        #     return shelf[key]
        with shelve.open(filename) as shelf:
            if key in shelf: return shelf[key]
        # release the file to allow other processes to use it
        # this function is meant for slow functions, so this extra closing and opening isn't significant
        ret = func(*args, **kwargs)
        with shelve.open(filename) as shelf: shelf[key] = ret
        return ret
    return cast(F, wrapper)

def cache_by_id(func:F) -> F:
    cache = {}
    def wrapper(*args, **kwargs):
        key = _jsonify([[id(arg) for arg in args], {k:id(v) for k,v in kwargs}])
        if key not in cache: cache[key] = func(*args, **kwargs)
        return cache[key]
    return cast(F, wrapper)


T = TypeVar('T')
F2 = TypeVar('F2', bound=Callable[[], Iterator[T]])

def cached_generator(record_maker:Callable[[Any],T]=lambda x:x) -> Callable[[F2],F2]:
    '''
    Caches a generator into jsonlines format.
    Deserialization is done by `record_maker(json.loads(line))`.
    Doesn't track args, so don't use any.
    '''
    def decorator(func:F2) -> F2:
        cache_fpath = os.path.join('.cache-{func.__name__}.jsonlines'.format(**locals()))
        def wrapper(*args, **kwargs):
            if args or kwargs: raise Exception('cached_generator() cannot handle args or kwargs')
            if not os.path.exists(cache_fpath):
                with open(cache_fpath+'.tmp', 'wt') as f:
                    for r in func():
                        f.write(json.dumps(r) + '\n')
                        yield r
                os.rename(cache_fpath+'.tmp', cache_fpath)
            else:
                with open(cache_fpath, 'rt') as f:
                    for line in f:
                        yield record_maker(json.loads(line))
        return cast(F2, wrapper)
    return decorator

def cached_generator_json(func:F2) -> F2:
    '''
    Caches a generator into jsonlines format.
    Deserialization is done by `json.loads(line)`.
    Doesn't track args, so don't use any.
    '''
    cache_fpath = os.path.join('.cache-{func.__name__}.jsonlines'.format(**locals()))
    def wrapper(*args, **kwargs):
        if args or kwargs: raise Exception('cached_generator() cannot handle args or kwargs')
        if not os.path.exists(cache_fpath):
            with open(cache_fpath+'.tmp', 'wt') as f:
                for r in func():
                    f.write(json.dumps(r) + '\n')
                    yield r
            os.rename(cache_fpath+'.tmp', cache_fpath)
        else:
            with open(cache_fpath, 'rt') as f:
                for line in f:
                    yield json.loads(line)
    return cast(F2, wrapper)
