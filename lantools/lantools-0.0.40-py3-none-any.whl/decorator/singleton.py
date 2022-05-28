import functools

def cache():
    results = {}
    
    def cached(function):
        @functools.wraps(function)
        def _cached(*args, **kwargs):
            if function not in results:
                results[function] = function(*args, **kwargs)

            return results[function]
 
        return _cached
 
    return cached

singleton = cache()
