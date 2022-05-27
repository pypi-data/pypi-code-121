from glob import glob
from ..utils.module import filter_kwargs


class ReducerMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    
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
                'curlrenderer': self.default_curlrenderer,
                'pathrenderer': self.default_pathrenderer,
            }[type]

        return filter_kwargs(f, *args, **kwargs)


            
    

    def default_urlfilter(self, url, context):
        return True
    
    def default_parser(self, response, context, **kwargs):
        return
    
    def default_urlrenderer(self, host, response, context):
        return host
    
    def default_curlrenderer(self, curl, resposne, context):
        return curl
    
    def default_pathrenderer(self, path, response, context):        
        return path
        
    def default_pattern_renderer(self, pattern, resposne, context):
        return pattern
    
    def default_breaker(self, response, context):
        return False
    
    def default_payloader(self, context):
        yield None
    