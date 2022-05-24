from cgitb import reset
from ..utils.module import filter_kwargs


class ReducerMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_method(self, func, kind):
        if callable(func):
            return func
        if isinstance(func, str):
            if hasattr(self, func):
                return getattr(self, func)     
        return {
            'urlfilter': self.default_urlfilter,
            'parser': self.default_parser,
            'urlrenderer': self.default_urlrenderer,
            'urlpattern_renderer': self.default_pattern_renderer,
            'breaker': self.default_breaker,
            'payloader': self.default_payloader
        }[kind]
    
    
    def dispatch(self, type, func, *args, **kwargs):
        
        if callable(func):
            f = func
        elif isinstance(func, str):
            if hasattr(self, func):
                f = getattr(self, func)
            else:
                raise NotImplementedError(f"The method {func} is not implemented!")
        else:
            f = {
                'urlfilter': self.default_urlfilter,
                'parser': self.default_parser,
                'urlrenderer': self.default_urlrenderer,
                'urlpattern_renderer': self.default_pattern_renderer,
                'breaker': self.default_breaker,
                'payloader': self.default_payloader,
            }[type]

        return filter_kwargs(f, *args, **kwargs)


            
    

    def default_urlfilter(self, url, context):
        return True
    
    def default_parser(self, response, context, **kwargs):
        return
    
    def default_urlrenderer(self, host, response, context):
        return host
        
    def default_pattern_renderer(self, pattern, resposne, context):
        return pattern
    
    def default_breaker(self, response, context):
        return False
    
    def default_payloader(self, context):
        yield None
    