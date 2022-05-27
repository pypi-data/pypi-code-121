from collections import abc

from ..utils.urls import parse_query
from ..utils.regex import extgroup
from .actions import UrlRenderAction, UrlPatternAction


class ResponseMeta:

    def __init__(self, match=None, pattern=None, query=None, soup=None, link_count=0):
        for k, v in locals().items():
            setattr(self, k, v)

    def set_urlutils(self, link, action):
        if isinstance(action, UrlRenderAction):
            if isinstance(link, str):
                self.query = parse_query(link)
            elif isinstance(link, abc.Mapping):
                self.query = link
            else:
                self.query = None
        
        elif isinstance(action, UrlPatternAction):
            self.match = extgroup(action.urlpattern, link)
            self.query = parse_query(link)
    

    def set_responsemap(self, response, action):
        self.responsemap = {
            action.name: response
        }
    
    def update_responsemap(self, prev_response_meta):
        self.responsemap.update(
            prev_response_meta
        )
    
        
        
