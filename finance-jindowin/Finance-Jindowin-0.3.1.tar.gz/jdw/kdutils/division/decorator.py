def _has_decorator_attr(obj):
    return (
      hasattr(obj, '_decorator') and
      isinstance(getattr(obj, '_decorator'), Decorator))

def unwrap(maybe_decorator):
    decorators = []
    cur = maybe_decorator
    while True:
        if isinstance(cur, Decorator):
            decorators.append(cur)
        elif _has_decorator_attr(cur):
            decorators.append(getattr(cur, '_decorator'))
        else:
            break
        if not hasattr(decorators[-1], 'decorated_target'):
            break
        cur = decorators[-1].decorated_target
    return decorators, cur

class Decorator(object):
    def __init__(self,
               decorator_name,
               target,
               decorator_doc='',
               decorator_argspec=None):
        self._decorated_target = target
        self._decorator_name = decorator_name
        self._decorator_doc = decorator_doc
        self._decorator_argspec = decorator_argspec
   
        if hasattr(target, '__name__'):
            self.__name__ = target.__name__
        if hasattr(target, '__qualname__'):
            self.__qualname__ = target.__qualname__
        if self._decorator_doc:
            self.__doc__ = self._decorator_doc
        elif hasattr(target, '__doc__') and target.__doc__:
            self.__doc__ = target.__doc__
        else:
            self.__doc__ = ''
        
    def __get__(self, instance, owner):
        return self._decorated_target.__get__(instance, owner)
    
    def __call__(self, *args, **kwargs):
        return self._decorated_target(*args, **kwargs)
    
    @property
    def decorated_target(self):
        return self._decorated_target
    
    @decorated_target.setter
    def decorated_target(self, decorated_target):
        self._decorated_target = decorated_target
        
    @property
    def decorator_name(self):
        return self._decorator_name
    
    @property
    def decorator_doc(self):
        return self._decorator_doc
    
    @property
    def decorator_argspec(self):
        return self._decorator_argspec