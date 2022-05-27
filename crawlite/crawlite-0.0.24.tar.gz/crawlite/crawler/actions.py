from glob import glob
from pathlib import Path
from threading import local

from ..utils.regex import strcompile



class BaseAction:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        
        if not self.name:
            raise NotImplementedError(
                f"action name must be specified"
            )

    def as_kwargs(self):
        return self.__dict__



class UrlRenderAction(BaseAction):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not (self.host or self.urlrenderer):
            raise NotImplementedError(
                f"host or urlrenderer must be specified"
            )



class UrlPatternAction(BaseAction):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not (self.urlpattern or self.urlpattern_renderer):
            raise NotImplementedError(
                f"urlpattern or urlpattern_renderer must be specified"
            )
       
    def set_urlpattern(self, urlpattern_renderer, **kwargs):
        pattern = urlpattern_renderer(**kwargs)
        return strcompile(pattern)



class CurlAction(BaseAction):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if not (self.curl or self.curlrenderer):
            raise NotImplementedError(
                f"curl or curl_renderer must be specified"
            )



class FileAction(BaseAction):
    method = 'get'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not (self.path or self.pathrenderer):
            raise NotImplementedError(
                f"path or pathrenderer must be specified"
            )
        self._check_globpath()

    def _check_globpath(self):
        if '*' in self.path:
            self.pathrenderer = self.pathrenderer or (lambda: glob(self.path))
            




def urlrender(
    host=None, urlrenderer=None, headers=None, cookies=None,
    payloader=None, parser=None, extractor=None, urlfilter=None, breaker=None, fields=None, referer=None, name=None, refresh=False, delay=None, method=None):
    return UrlRenderAction(**locals())


def urlpattern(
    urlpattern=None, urlpattern_renderer=None, remove_duplicates=True, attrs=None, css_selector=None, recursive=False, headers=None, cookies=None,
    payloader=None, parser=None, extractor=None, urlfilter=None, breaker=None, fields=None, referer=None, name=None, refresh=False, delay=None, method=None):
    return UrlPatternAction(**locals())


def curl(curl=None, curlrenderer=None, parser=None, extractor=None, breaker=None, name=None, refresh=False, delay=None):
    '''bash curl command needed
    '''
    return CurlAction(**locals())


def file(path=None, pathrenderer=None, parser=None, extractor=None, breaker=None, name=None, refresh=False, delay=None):
    ''' path=file:///D:/dev/crawlite/test/logparser/access.log (file uri)
        path=*/*/access.log (glob exp)
    '''
    return FileAction(**locals())

