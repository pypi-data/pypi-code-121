from glob import glob
from pathlib import Path

from ..utils.regex import strcompile
from ..utils.urls import parse_curl



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



def urlrender(
    host=None, urlrenderer=None, headers=None, cookies=None,
    payloader=None, parser=None, extractor=None, urlfilter=None, breaker=None, fields=None, contentfile=False, referer=None, name=None, refresh=False, delay=None, method=None):
    return UrlRenderAction(**locals())


def urlpattern(
    urlpattern=None, urlpattern_renderer=None, remove_duplicates=True, attrs=None, css_selector=None, recursive=False, headers=None, cookies=None,
    payloader=None, parser=None, extractor=None, urlfilter=None, breaker=None, fields=None, contentfile=False, referer=None, name=None, refresh=False, delay=None, method=None):
    return UrlPatternAction(**locals())


def fromcurl(curl_template=None, payloader=None, urlrenderer=None, parser=None, name=None, headers=None, cookies=None, remove_line='\n', method=None, **kwargs):
    if remove_line:
        curl_template = curl_template.replace(remove_line, '')
    
    p = parse_curl(curl_template)

    def fromcurl_urlrenderer(url):
        yield p['url']

    def fromcurl_payloader():
        yield p['payloads']
    
    return urlrender(
        host=p['url'], 
        headers=headers or p['headers'],
        cookies=cookies or p['cookies'],
        urlrenderer=urlrenderer or fromcurl_urlrenderer,
        payloader=payloader or fromcurl_payloader,
        method= method or p['method'],
        parser=parser,
        name=name, **kwargs
    )


def frompath(path, path_renderer=None, parser=None, name=None, refresh=True, delay=0, recursive=True, **kwargs):
    def urlrenderer(url):
        if url.startswith('file:///'):
            yield url
        
        for p in glob(url, recursive=recursive):
            p = Path(p).absolute().as_uri()
            yield p   
    
    return urlrender(
        host=path,
        urlrenderer=path_renderer or urlrenderer,
        parser=parser,
        name=name,
        refresh=refresh,
        delay=delay,
        **kwargs
    )